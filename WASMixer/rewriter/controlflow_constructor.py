
from ..parser.instruction import *
from ..parser.opcodes_stack import *
from ..interpreter.instructions import *
from ..parser.types import *


# class StackCalcuator:
#
#     def __init__(self):
#         pass
#
#     def get_instrs_max_stack_depth(self, binary, instr_list):
#         max_stack = 0
#         current_stack = 0
#         for _, instr in enumerate(instr_list):
#             if instr.opcode == Block or instr.opcode == Loop or instr.opcode == If:
#                 if instr.args.bt > 0:
#                     current_stack += len(SectionRewriter.get_typesec_functype(binary, instr.args.bt).result_types) - len(
#                         SectionRewriter.get_typesec_functype(binary, instr.args.bt).param_types)
#                 elif 0 > instr.args.bt > -64:
#                     current_stack += -1
#                 elif instr.args.bt == -64:
#                     pass
#             elif instr.opcode == Call:
#                 if instr.args <= (SectionRewriter.get_import_func_num(binary) - 1):
#                     import_func_list = SectionRewriter.get_import_func_list(binary)
#                     current_stack += (len(SectionRewriter.get_typesec_functype(binary, import_func_list[instr.args].desc.func_type).result_types) -
#                                       len(SectionRewriter.get_typesec_functype(binary, import_func_list[instr.args].desc.func_type).param_types))
#                 else:
#                     internal_funcidx = instr.args - SectionRewriter.get_import_func_num(binary)
#                     functypeidx = SectionRewriter.get_funcsec_functypeidx(binary, internal_funcidx)
#                     functype = SectionRewriter.get_typesec_functype(binary, functypeidx)
#                     current_stack += (len(functype.result_types) - len(functype.param_types))
#
#             elif instr.opcode == CallIndirect:
#                 functype = SectionRewriter.get_typesec_functype(binary, instr.args)
#                 current_stack += (len(functype.result_types) - len(functype.param_types)) - 1
#             else:
#                 # 这里可能因为遇到了没收录的指令而报越界
#                 current_stack += stack_change[instr.opcode]
#             if current_stack > max_stack:
#                 max_stack = current_stack
#
#         return max_stack
#
#     def get_stack_snapshot(self, binary, instr_list: list, instr_index: int):
#         instr_list = instr_list[0:instr_index]
#         stack = []
#         for i in range(instr_index):
#             instr = instr_list[i]
#             instr_table[instr.opcode](binary, instr.args, stack)
#
#         return stack

class ControlFlowConstructor:

    def __init__(self):
        pass

    def fix_br_instruction(self, instrs_list, increment):
        for _, instr in enumerate(instrs_list):
            if instr.opcode == Br:
                instr.args = instr.args + increment
            elif instr.opcode == BrIf:
                instr.args = instr.args + increment
            elif instr.opcode == BrTable:
                for label_id in instr.args.labels:
                    instr.args.labels[label_id] += increment
            elif instr.opcode in [Block, Loop]:
                self.fix_br_instruction(instr.args.instrs, increment)
            elif instr.opcode == If:
                self.fix_br_instruction(instr.args.instrs1, increment)
                self.fix_br_instruction(instr.args.instrs2, increment)


    def sequential_statement(self, instrs_list):
        sequential_block = Instruction(Block, BlockArgs(BlockTypeEmpty, []))
        for instrs in instrs_list:
            instrs_block = Instruction(Block, BlockArgs(BlockTypeEmpty, instrs))
            sequential_block.args.instrs.append(instrs_block)
        return sequential_block

    def if_else_statement(self, if_cond, if_body, else_body):
        if_cond_block = Instruction(If, BlockArgs(BlockTypeEmpty, if_cond))
        if_cond_block.args.instrs.append(Instruction(BrIf, 0))
        if_cond_block.args.instrs.append(Instruction(Br, 1))
        if_block = Instruction(Block, BlockArgs(BlockTypeEmpty, [if_cond_block] + if_body))
        if_block.args.instrs.append(Instruction(Br, 1))

        else_block = Instruction(Block, BlockArgs(BlockTypeEmpty, [if_cond_block] + else_body))
        else_block.args.instrs.append(Instruction(Br, 0))

        if_else_block = else_block
        return if_else_block

    def while_statement(self, while_cond, while_body):
        while_cond_block = Instruction(Loop, BlockArgs(BlockTypeEmpty, while_cond))
        while_cond_block.args.instrs.append(Instruction(BrIf, 1))
        while_cond_block.args.instrs.extend(while_body)
        while_cond_block.args.instrs.append(Instruction(Br, 0))
        while_block = Instruction(Block, BlockArgs(BlockTypeEmpty, while_cond_block))
        return while_block


    def switch_case_statement(self, switch_cond, case_list):
        switch_cond_block = Instruction(Block, BlockArgs(BlockTypeEmpty, switch_cond))
        case_block_list = []
        for i, case in enumerate(case_list):
            case_block = Instruction(Block, BlockArgs(BlockTypeEmpty, case))
            case_block.args.instrs.append(Instruction(Br, len(case_list) - 1 - i))
            case_block_list.append(case_block)

        for _, cb in enumerate(case_block_list):
            # 最内层block块开头插入分发块
            if _ == 0:
                cb.args.instrs.insert(0, switch_cond_block)
            else:
                cb.args.instrs.insert(0, case_block_list[_ - 1])
        switch_case_block = case_block_list[-1]
        return switch_case_block