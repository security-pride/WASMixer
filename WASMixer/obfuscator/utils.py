import math
import random

from WASMixer import *
from WASMixer.interpreter.mini_interpreter import MiniInterpreter
from WASMixer.parser.opcodes_stack import stack_change
from WASMixer.rewriter.modify_binary import *
from WASMixer.obfuscator.instruction_blocks import *

def get_instrs_max_stack_depth(binary, instr_list):
    """
    获取指令序列使用的最大栈长度
    Args:
        instr_list:
    """
    max_stack = 0
    current_stack = 0
    for _, instr in enumerate(instr_list):  # 这里有个问题，就是没考虑vec类型的值，怎么处理？
        if instr.opcode == Block or instr.opcode == Loop or instr.opcode == If:
            if instr.args.bt > 0:
                current_stack += len(binary.module.type_sec[instr.args.bt].result_types) - len(
                    binary.module.type_sec[instr.args.bt].param_types)
            elif 0 > instr.args.bt > -64:
                current_stack += -1
            elif instr.args.bt == -64:
                pass
        elif instr.opcode == Call:
            if instr.args <= (binary.get_import_func_num() - 1):
                import_func_list = binary.get_import_func_list()

                current_stack += (len(binary.module.type_sec[import_func_list[
                    instr.args].desc.func_type].result_types) - len(binary.module.type_sec[
                                                                        import_func_list[
                                                                            instr.args].desc.func_type].param_types))
            else:
                current_stack += (len(binary.module.type_sec[binary.module.func_sec[
                    instr.args - binary.get_import_func_num()]].result_types) - len(
                    binary.module.type_sec[binary.module.func_sec[
                        instr.args - binary.get_import_func_num()]].param_types))

        elif instr.opcode == CallIndirect:
            current_stack += (len(binary.module.type_sec[instr.args].result_types) -
                              len(binary.module.type_sec[instr.args].param_types)) - 1
        else:
            # 这里可能因为遇到了没收录的指令而报越界
            current_stack += stack_change[instr.opcode]

        if current_stack > max_stack:
            max_stack = current_stack

    return max_stack


def get_function_memory_stack_length(binary, inner_func_id):

    expr = binary.module.code_sec[inner_func_id].expr
    stack_len = 0
    contain_globalget = False
    contain_i32const = False
    contain_i32sub = False
    for instr in expr[:8]:
        if instr.opcode == GlobalGet and instr.args == 0:
            contain_globalget = True
        if instr.opcode == I32Const:
            contain_i32const = True
            stack_len = instr.args
        if instr.opcode == I32Sub:
            contain_i32sub = True
    if contain_globalget is True and contain_i32const is True and contain_i32sub is True:
        if stack_len > 200:
            return 0
        else:
            return stack_len
    else:
        return 0


def code_block_splitting(binary, instr_list, split_num, func_id):

    max_stack = get_instrs_max_stack_depth(binary, instr_list)

    # 如果遇到了无法识别的指令，就直接不平坦化了
    if max_stack == -1:
        return instr_list

    # 添加用于维持栈平衡和跳转标志的local，+1那个就是跳转标志的local
    new_local_i32 = []
    new_local_f32 = []
    new_local_i64 = []
    new_local_f64 = []
    for i in range(max_stack):
        new_local_i32.append(binary.add_new_local_to_func(func_id, ValTypeI32))
        new_local_f32.append(binary.add_new_local_to_func(func_id, ValTypeF32))
        new_local_i64.append(binary.add_new_local_to_func(func_id, ValTypeI64))
        new_local_f64.append(binary.add_new_local_to_func(func_id, ValTypeF64))

    # 分割基本块
    instrs_list = []

    # 按照split_num的数量分割基本块
    index = 0
    instrs_size = math.ceil(len(instr_list) / split_num)
    for i in range(split_num):
        if i != (split_num - 1):
            instrs_list.append(instr_list[index:index + instrs_size])
            index += instrs_size
        else:
            instrs_list.append(instr_list[index:len(instr_list)])

    # 获取每个基本块的栈快照
    interpreter = MiniInterpreter(instr_list, binary, func_id)
    stack_snapshot = []
    instr_index = 0
    for _, instrs in enumerate(instrs_list):
        instr_index += len(instrs_list[_])
        stack_snapshot.append(interpreter.get_stack_snapshot(instr_index))

    # 构建每个基本块结构体
    basic_blocks = []
    for i in range(len(instrs_list)):
        if i == 0:
            # 因为wasm函数参数不在栈上，所以stack_snapshot_pre为0
            basic_blocks.append({
                'id': i,
                'instrs': instrs_list[i],
                'stack_snapshot_pre': [],
                'stack_snapshot_post': stack_snapshot[i]
            })
        else:
            basic_blocks.append({
                'id': i,
                'instrs': instrs_list[i],
                'stack_snapshot_pre': stack_snapshot[i - 1],
                'stack_snapshot_post': stack_snapshot[i]
            })

    # 打乱基本块顺序   (打不打乱都行)
    random.shuffle(basic_blocks)

    for _, bb in enumerate(basic_blocks):
        instrs_pre = []
        # 恢复堆栈
        for i, stack_type in enumerate(bb['stack_snapshot_pre']):
            if stack_type == ValTypeI32:
                instrs_pre.append(Instruction(LocalGet, new_local_i32[i]))
            elif stack_type == ValTypeI64:
                instrs_pre.append(Instruction(LocalGet, new_local_i64[i]))
            elif stack_type == ValTypeF32:
                instrs_pre.append(Instruction(LocalGet, new_local_f32[i]))
            elif stack_type == ValTypeF64:
                instrs_pre.append(Instruction(LocalGet, new_local_f64[i]))
            else:
                raise Exception("error")

        bb['instrs'] = instrs_pre + bb['instrs']

        # 保存堆栈
        for i, stack_type in enumerate(reversed(bb['stack_snapshot_post'])):
            if stack_type == ValTypeI32:
                bb['instrs'].append(
                    Instruction(LocalSet, new_local_i32[len(bb['stack_snapshot_post']) - i - 1]))
            elif stack_type == ValTypeI64:
                bb['instrs'].append(
                    Instruction(LocalSet, new_local_i64[len(bb['stack_snapshot_post']) - i - 1]))
            elif stack_type == ValTypeF32:
                bb['instrs'].append(
                    Instruction(LocalSet, new_local_f32[len(bb['stack_snapshot_post']) - i - 1]))
            elif stack_type == ValTypeF64:
                bb['instrs'].append(
                    Instruction(LocalSet, new_local_f64[len(bb['stack_snapshot_post']) - i - 1]))
            else:
                raise Exception("error")

    return basic_blocks, new_local_i32, new_local_i64, new_local_f32, new_local_f64

def add_table_funcref_limits(binary, num):
    """
    为
    Args:
        num:

    Returns:

    """
    if not binary.module.table_sec:
        binary.module.table_sec.append(TableType(limits=Limits(1, num + 1, num + 1)))
    else:
        binary.module.table_sec[0].limits.min += num
        binary.module.table_sec[0].limits.max += (num + 5)