# -*- coding: UTF-8 -*-
"""
@Project ：wasm-WASMixer
@File    ：instr_stack_change.py
@Author  ：格友
"""

import math
from ..parser.types import ValTypeF64, ValTypeF32, ValTypeI32, ValTypeI64


def unreachable(interpreter, args, stack):
    pass


def nop(interpreter, args, stack):
    pass


def block(interpreter, args, stack):
    if args.bt > 0:
        for param_type in interpreter.wasm_binary.module.type_sec[args.bt].param_types:
            stack.pop()
        for result_type in interpreter.wasm_binary.module.type_sec[args.bt].result_types:
            stack.append(result_type)
    elif args.bt == -1:
        stack.append(ValTypeI32)
    elif args.bt == -2:
        stack.append(ValTypeI64)
    elif args.bt == -3:
        stack.append(ValTypeF32)
    elif args.bt == -4:
        stack.append(ValTypeF64)
    elif args.bt == -64:
        pass


def loop(interpreter, args, stack):
    if args.bt > 0:
        for param_type in interpreter.wasm_binary.module.type_sec[args.bt].param_types:
            stack.pop()
        for result_type in interpreter.wasm_binary.module.type_sec[args.bt].result_types:
            stack.append(result_type)
    elif args.bt == -1:
        stack.append(ValTypeI32)
    elif args.bt == -2:
        stack.append(ValTypeI64)
    elif args.bt == -3:
        stack.append(ValTypeF32)
    elif args.bt == -4:
        stack.append(ValTypeF64)
    elif args.bt == -64:
        pass


def control_if(interpreter, args, stack):
    stack.pop()
    if args.bt > 0:
        for param_type in interpreter.wasm_binary.module.type_sec[args.bt].param_types:
            stack.pop()
        for result_type in interpreter.wasm_binary.module.type_sec[args.bt].result_types:
            stack.append(result_type)
    elif args.bt == -1:
        stack.append(ValTypeI32)
    elif args.bt == -2:
        stack.append(ValTypeI64)
    elif args.bt == -3:
        stack.append(ValTypeF32)
    elif args.bt == -4:
        stack.append(ValTypeF64)
    elif args.bt == -64:
        pass


def br(interpreter, args, stack):
    pass


def br_if(interpreter, args, stack):
    stack.pop()


def br_table(interpreter, args, stack):
    stack.pop()

# return 的处理是，在分割基本块的时候就就不把它放到基本块中
def control_return(interpreter, args, stack):
    pass


def call(interpreter, args, stack):
    import_func_list = interpreter.wasm_binary.get_import_func_list()
    if args <= (interpreter.wasm_binary.get_import_func_num() - 1):
        for param_type in interpreter.wasm_binary.module.type_sec[import_func_list[args].desc.func_type].param_types:
            stack.pop()
        for result_type in interpreter.wasm_binary.module.type_sec[import_func_list[args].desc.func_type].result_types:
            stack.append(result_type)
    else:
        for param_type in interpreter.wasm_binary.module.type_sec[interpreter.wasm_binary.module.func_sec[args - interpreter.wasm_binary.get_import_func_num()]].param_types:
            stack.pop()
        for result_type in interpreter.wasm_binary.module.type_sec[interpreter.wasm_binary.module.func_sec[args - interpreter.wasm_binary.get_import_func_num()]].result_types:
            stack.append(result_type)


def call_indirect(interpreter, args, stack):
    stack.pop()
    for param_type in interpreter.wasm_binary.module.type_sec[args].param_types:
        stack.pop()
    for result_type in interpreter.wasm_binary.module.type_sec[args].result_types:
        stack.append(result_type)


def memory_size(interpreter, args, stack):
    stack.append(ValTypeI32)


def memory_grow(interpreter, args, stack):
    pass


# load
def i32_load(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI32)


def i64_load(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def f32_load(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF32)


def f64_load(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF64)


def i32_load_8s(interpreter, args, stack):
    pass


def i32_load_8u(interpreter, args, stack):
    pass


def i32_load_16s(interpreter, args, stack):
    pass


def i32_load_16u(interpreter, args, stack):
    pass


def i64_load_8s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def i64_load_8u(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def i64_load_16s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def i64_load_16u(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def i64_load_32s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def i64_load_32u(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


# store
def i32_store(interpreter, args, stack):
    stack.pop()
    stack.pop()


def i64_store(interpreter, args, stack):
    stack.pop()
    stack.pop()


def f32_store(interpreter, args, stack):
    stack.pop()
    stack.pop()


def f64_store(interpreter, args, stack):
    stack.pop()
    stack.pop()


def i32_store_8(interpreter, args, stack):
    stack.pop()
    stack.pop()


def i32_store_16(interpreter, args, stack):
    stack.pop()
    stack.pop()


def i64_store_8(interpreter, args, stack):
    stack.pop()
    stack.pop()


def i64_store_16(interpreter, args, stack):
    stack.pop()
    stack.pop()


def i64_store_32(interpreter, args, stack):
    stack.pop()
    stack.pop()


def drop(interpreter, args, stack):
    stack.pop()


def _select(interpreter, args, stack):
    stack.pop()
    stack.pop()


def local_get(interpreter, args, stack):
    inner_func_id = interpreter.inner_func_id
    func_type = interpreter.wasm_binary.module.type_sec[interpreter.wasm_binary.module.func_sec[inner_func_id]]
    if args in range(len(func_type.param_types)):
        stack.append(func_type.param_types[args])
    else:
        locals_num = 0
        for item in interpreter.wasm_binary.module.code_sec[inner_func_id].locals:
            locals_num += item.n
            if locals_num >= (args - len(func_type.param_types) + 1):
                stack.append(item.type)
                return



def local_set(interpreter, args, stack):
    stack.pop()


def local_tee(interpreter, args, stack):
    pass


def global_get(interpreter, args, stack):
    import_global_num = -1
    for _, import_item in enumerate(interpreter.wasm_binary.module.import_sec):
        if import_item.desc.global_type != None:
            import_global_num += 1
            if import_global_num == args:
                stack.append(import_item.desc.global_type)
                return
    for _, global_item in enumerate(interpreter.wasm_binary.module.global_sec):
        import_global_num += 1
        if import_global_num == args:
            stack.append(global_item.type.val_type)
            return


def global_set(interpreter, args, stack):
    stack.pop()


def i32_const(interpreter, args, stack):
    stack.append(ValTypeI32)


def i64_const(interpreter, args, stack):
    stack.append(ValTypeI64)


def f32_const(interpreter, args, stack):
    stack.append(ValTypeF32)


def f64_const(interpreter, args, stack):
    stack.append(ValTypeF64)


# i32 example & rel
def i32_eqz(interpreter, args, stack):
    pass


def i32_eq(interpreter, args, stack):
    stack.pop()


def i32_ne(interpreter, args, stack):
    stack.pop()


def i32_lt_s(interpreter, args, stack):
    stack.pop()


def i32_lt_u(interpreter, args, stack):
    stack.pop()


def i32_gt_s(interpreter, args, stack):
    stack.pop()


def i32_gt_u(interpreter, args, stack):
    stack.pop()


def i32_le_s(interpreter, args, stack):
    stack.pop()


def i32_le_u(interpreter, args, stack):
    stack.pop()


def i32_ge_s(interpreter, args, stack):
    stack.pop()


def i32_ge_u(interpreter, args, stack):
    stack.pop()


# i64 example & rel
def i64_eqz(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI32)


def i64_eq(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def i64_ne(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def i64_lt_s(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def i64_lt_u(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def i64_gt_s(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def i64_gt_u(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def i64_le_s(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def i64_le_u(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def i64_ge_s(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def i64_ge_u(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


# f32 rel
def f32_eq(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def f32_ne(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def f32_lt(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def f32_gt(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def f32_le(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def f32_ge(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


# f64 rel
def f64_eq(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def f64_ne(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def f64_lt(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def f64_gt(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def f64_le(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


def f64_ge(interpreter, args, stack):
    stack.pop()
    stack.pop()
    stack.append(ValTypeI32)


# i32 arithmetic & bitwise
def i32_clz(interpreter, args, stack):
    pass


def i32_ctz(interpreter, args, stack):
    pass


def i32_pop_cnt(interpreter, args, stack):
    pass


def i32_add(interpreter, args, stack):
    stack.pop()


def i32_sub(interpreter, args, stack):
    stack.pop()


def i32_mul(interpreter, args, stack):
    stack.pop()


def i32_div_s(interpreter, args, stack):
    stack.pop()


def i32_div_u(interpreter, args, stack):
    stack.pop()


def i32_rem_s(interpreter, args, stack):
    stack.pop()


def i32_rem_u(interpreter, args, stack):
    stack.pop()


def i32_and(interpreter, args, stack):
    stack.pop()


def i32_or(interpreter, args, stack):
    stack.pop()


def i32_xor(interpreter, args, stack):
    stack.pop()


def i32_shl(interpreter, args, stack):
    stack.pop()


def i32_shr_s(interpreter, args, stack):
    stack.pop()


def i32_shr_u(interpreter, args, stack):
    stack.pop()


def i32_rotl(interpreter, args, stack):
    stack.pop()


def i32_rotr(interpreter, args, stack):
    stack.pop()

# i64 arithmetic & bitwise
def i64_clz(interpreter, args, stack):
    pass


def i64_ctz(interpreter, args, stack):
    pass


def i64_pop_cnt(interpreter, args, stack):
    pass


def i64_add(interpreter, args, stack):
    stack.pop()


def i64_sub(interpreter, args, stack):
    stack.pop()


def i64_mul(interpreter, args, stack):
    stack.pop()


def i64_div_s(interpreter, args, stack):
    stack.pop()


def i64_div_u(interpreter, args, stack):
    stack.pop()


def i64_rem_s(interpreter, args, stack):
    stack.pop()


def i64_rem_u(interpreter, args, stack):
    stack.pop()


def i64_and(interpreter, args, stack):
    stack.pop()


def i64_or(interpreter, args, stack):
    stack.pop()


def i64_xor(interpreter, args, stack):
    stack.pop()


def i64_shl(interpreter, args, stack):
    stack.pop()


def i64_shr_s(interpreter, args, stack):
    stack.pop()


def i64_shr_u(interpreter, args, stack):
    stack.pop()


def i64_rotl(interpreter, args, stack):
    stack.pop()


def i64_rotr(interpreter, args, stack):
    stack.pop()


# f32 arithmetic
def f32_abs(interpreter, args, stack):
    pass


def f32_neg(interpreter, args, stack):
    pass


def f32_ceil(interpreter, args, stack):
    pass


def f32_floor(interpreter, args, stack):
    pass


def f32_trunc(interpreter, args, stack):
    pass


def f32_nearest(interpreter, args, stack):
    pass


def f32_sqrt(interpreter, args, stack):
    pass


def f32_add(interpreter, args, stack):
    stack.pop()


def f32_sub(interpreter, args, stack):
    stack.pop()


def f32_mul(interpreter, args, stack):
    stack.pop()


def f32_div(interpreter, args, stack):
    stack.pop()


def f32_min(interpreter, args, stack):
    stack.pop()


def f32_max(interpreter, args, stack):
    stack.pop()


def f32_copysign(interpreter, args, stack):
    stack.pop()


# f64 arithmetic
def f64_abs(interpreter, args, stack):
    pass


def f64_neg(interpreter, args, stack):
    pass


def f64_ceil(interpreter, args, stack):
    pass


def f64_floor(interpreter, args, stack):
    pass


def f64_trunc(interpreter, args, stack):
    pass


def f64_nearest(interpreter, args, stack):
    pass


def f64_sqrt(interpreter, args, stack):
    pass


def f64_add(interpreter, args, stack):
    stack.pop()


def f64_sub(interpreter, args, stack):
    stack.pop()


def f64_mul(interpreter, args, stack):
    stack.pop()


def f64_div(interpreter, args, stack):
    stack.pop()


def f64_min(interpreter, args, stack):
    stack.pop()


def f64_max(interpreter, args, stack):
    stack.pop()


def f64_copysign(interpreter, args, stack):
    stack.pop()


# conversions
def i32_wrap_i64(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI32)


def i32_trunc_f32s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI32)


def i32_trunc_f32u(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI32)


def i32_trunc_f64s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI32)


def i32_trunc_f64u(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI32)


def i64_extend_i32s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def i64_extend_i32u(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def i64_trunc_f32s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def i64_trunc_f32u(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def i64_trunc_f64s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def i64_trunc_f64u(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def f32_convert_i32s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF32)


def f32_convert_i32u(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF32)


def f32_convert_i64s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF32)


def f32_convert_i64u(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF32)


def f32_demote_f64(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF32)


def f64_convert_i32s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF64)


def f64_convert_i32u(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF64)


def f64_convert_i64s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF64)


def f64_convert_i64u(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF64)


def f64_promote_f32(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF64)


def i32_reinterpret_f32(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI32)


def i64_reinterpret_f64(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def f32_reinterpret_i32(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF32)


def f64_reinterpret_i64(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeF64)


def i32_extend_8s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI32)


def i32_extend_16s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI32)


def i64_extend_8s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def i64_extend_16s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def i64_extend_32s(interpreter, args, stack):
    stack.pop()
    stack.append(ValTypeI64)


def trunc_sat(interpreter, args, stack):
    pass
