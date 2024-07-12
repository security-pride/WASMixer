# -*- coding: UTF-8 -*-
"""
@Project ：wasm-WASMixer
@File    ：instructions.py
@Author  ：格友
"""
from .instr_stack_change import _select
from ..parser import opcodes
from .instr_stack_change import *

"""
函数list，每一项都对应指令函数
"""


def instr_fn(vm, args):
    pass


instr_table = [instr_fn] * 256

# instr_control
instr_table[opcodes.Unreachable] = unreachable
instr_table[opcodes.Nop] = nop
instr_table[opcodes.Block] = block
instr_table[opcodes.Loop] = loop
instr_table[opcodes.If] = control_if
instr_table[opcodes.Br] = br
instr_table[opcodes.BrIf] = br_if
instr_table[opcodes.BrTable] = br_table
instr_table[opcodes.Return] = control_return
instr_table[opcodes.Call] = call
instr_table[opcodes.CallIndirect] = call_indirect

# instr_parametric
instr_table[opcodes.Drop] = drop
instr_table[opcodes.Select] = _select

# instr_variable
instr_table[opcodes.LocalGet] = local_get
instr_table[opcodes.LocalSet] = local_set
instr_table[opcodes.LocalTee] = local_tee
instr_table[opcodes.GlobalGet] = global_get
instr_table[opcodes.GlobalSet] = global_set

# instr_memory
instr_table[opcodes.I32Load] = i32_load
instr_table[opcodes.I64Load] = i64_load
instr_table[opcodes.F32Load] = f32_load
instr_table[opcodes.F64Load] = f64_load
instr_table[opcodes.I32Load8S] = i32_load_8s
instr_table[opcodes.I32Load8U] = i32_load_8u
instr_table[opcodes.I32Load16S] = i32_load_16s
instr_table[opcodes.I32Load16U] = i32_load_16u
instr_table[opcodes.I64Load8S] = i64_load_8s
instr_table[opcodes.I64Load8U] = i64_load_8u
instr_table[opcodes.I64Load16S] = i64_load_16s
instr_table[opcodes.I64Load16U] = i64_load_16u
instr_table[opcodes.I64Load32S] = i64_load_32s
instr_table[opcodes.I64Load32U] = i64_load_32u
instr_table[opcodes.I32Store] = i32_store
instr_table[opcodes.I64Store] = i64_store
instr_table[opcodes.F32Store] = f32_store
instr_table[opcodes.F64Store] = f64_store
instr_table[opcodes.I32Store8] = i32_store_8
instr_table[opcodes.I32Store16] = i32_store_16
instr_table[opcodes.I64Store8] = i64_store_8
instr_table[opcodes.I64Store16] = i64_store_16
instr_table[opcodes.I64Store32] = i64_store_32
instr_table[opcodes.MemorySize] = memory_size
instr_table[opcodes.MemoryGrow] = memory_grow

# instr_numeric
instr_table[opcodes.I32Const] = i32_const
instr_table[opcodes.I64Const] = i64_const
instr_table[opcodes.F32Const] = f32_const
instr_table[opcodes.F64Const] = f64_const
instr_table[opcodes.I32Eqz] = i32_eqz
instr_table[opcodes.I32Eq] = i32_eq
instr_table[opcodes.I32Ne] = i32_ne
instr_table[opcodes.I32LtS] = i32_lt_s
instr_table[opcodes.I32LtU] = i32_lt_u
instr_table[opcodes.I32GtS] = i32_gt_s
instr_table[opcodes.I32GtU] = i32_gt_u
instr_table[opcodes.I32LeS] = i32_le_s
instr_table[opcodes.I32LeU] = i32_le_u
instr_table[opcodes.I32GeS] = i32_ge_s
instr_table[opcodes.I32GeU] = i32_ge_u
instr_table[opcodes.I64Eqz] = i64_eqz
instr_table[opcodes.I64Eq] = i64_eq
instr_table[opcodes.I64Ne] = i64_ne
instr_table[opcodes.I64LtS] = i64_lt_s
instr_table[opcodes.I64LtU] = i64_lt_u
instr_table[opcodes.I64GtS] = i64_gt_s
instr_table[opcodes.I64GtU] = i64_gt_u
instr_table[opcodes.I64LeS] = i64_le_s
instr_table[opcodes.I64LeU] = i64_le_u
instr_table[opcodes.I64GeS] = i64_ge_s
instr_table[opcodes.I64GeU] = i64_ge_u
instr_table[opcodes.F32Eq] = f32_eq
instr_table[opcodes.F32Ne] = f32_ne
instr_table[opcodes.F32Lt] = f32_lt
instr_table[opcodes.F32Gt] = f32_gt
instr_table[opcodes.F32Le] = f32_le
instr_table[opcodes.F32Ge] = f32_ge
instr_table[opcodes.F64Eq] = f64_eq
instr_table[opcodes.F64Ne] = f64_ne
instr_table[opcodes.F64Lt] = f64_lt
instr_table[opcodes.F64Gt] = f64_gt
instr_table[opcodes.F64Le] = f64_le
instr_table[opcodes.F64Ge] = f64_ge
instr_table[opcodes.I32Clz] = i32_clz
instr_table[opcodes.I32Ctz] = i32_ctz
instr_table[opcodes.I32PopCnt] = i32_pop_cnt
instr_table[opcodes.I32Add] = i32_add
instr_table[opcodes.I32Sub] = i32_sub
instr_table[opcodes.I32Mul] = i32_mul
instr_table[opcodes.I32DivS] = i32_div_s
instr_table[opcodes.I32DivU] = i32_div_u
instr_table[opcodes.I32RemS] = i32_rem_s
instr_table[opcodes.I32RemU] = i32_rem_u
instr_table[opcodes.I32And] = i32_and
instr_table[opcodes.I32Or] = i32_or
instr_table[opcodes.I32Xor] = i32_xor
instr_table[opcodes.I32Shl] = i32_shl
instr_table[opcodes.I32ShrS] = i32_shr_s
instr_table[opcodes.I32ShrU] = i32_shr_u
instr_table[opcodes.I32Rotl] = i32_rotl
instr_table[opcodes.I32Rotr] = i32_rotr
instr_table[opcodes.I64Clz] = i64_clz
instr_table[opcodes.I64Ctz] = i64_ctz
instr_table[opcodes.I64PopCnt] = i64_pop_cnt
instr_table[opcodes.I64Add] = i64_add
instr_table[opcodes.I64Sub] = i64_sub
instr_table[opcodes.I64Mul] = i64_mul
instr_table[opcodes.I64DivS] = i64_div_s
instr_table[opcodes.I64DivU] = i64_div_u
instr_table[opcodes.I64RemS] = i64_rem_s
instr_table[opcodes.I64RemU] = i64_rem_u
instr_table[opcodes.I64And] = i64_and
instr_table[opcodes.I64Or] = i64_or
instr_table[opcodes.I64Xor] = i64_xor
instr_table[opcodes.I64Shl] = i64_shl
instr_table[opcodes.I64ShrS] = i64_shr_s
instr_table[opcodes.I64ShrU] = i64_shr_u
instr_table[opcodes.I64Rotl] = i64_rotl
instr_table[opcodes.I64Rotr] = i64_rotr
instr_table[opcodes.F32Abs] = f32_abs
instr_table[opcodes.F32Neg] = f32_neg
instr_table[opcodes.F32Ceil] = f32_ceil
instr_table[opcodes.F32Floor] = f32_floor
instr_table[opcodes.F32Trunc] = f32_trunc
instr_table[opcodes.F32Nearest] = f32_nearest
instr_table[opcodes.F32Sqrt] = f32_sqrt
instr_table[opcodes.F32Add] = f32_add
instr_table[opcodes.F32Sub] = f32_sub
instr_table[opcodes.F32Mul] = f32_mul
instr_table[opcodes.F32Div] = f32_div
instr_table[opcodes.F32Min] = f32_min
instr_table[opcodes.F32Max] = f32_max
instr_table[opcodes.F32CopySign] = f32_copysign
instr_table[opcodes.F64Abs] = f64_abs
instr_table[opcodes.F64Neg] = f64_neg
instr_table[opcodes.F64Ceil] = f64_ceil
instr_table[opcodes.F64Floor] = f64_floor
instr_table[opcodes.F64Trunc] = f64_trunc
instr_table[opcodes.F64Nearest] = f64_nearest
instr_table[opcodes.F64Sqrt] = f64_sqrt
instr_table[opcodes.F64Add] = f64_add
instr_table[opcodes.F64Sub] = f64_sub
instr_table[opcodes.F64Mul] = f64_mul
instr_table[opcodes.F64Div] = f64_div
instr_table[opcodes.F64Min] = f64_min
instr_table[opcodes.F64Max] = f64_max
instr_table[opcodes.F64CopySign] = f64_copysign
instr_table[opcodes.I32WrapI64] = i32_wrap_i64
instr_table[opcodes.I32TruncF32S] = i32_trunc_f32s
instr_table[opcodes.I32TruncF32U] = i32_trunc_f32u
instr_table[opcodes.I32TruncF64S] = i32_trunc_f64s
instr_table[opcodes.I32TruncF64U] = i32_trunc_f64u
instr_table[opcodes.I64ExtendI32S] = i64_extend_i32s
instr_table[opcodes.I64ExtendI32U] = i64_extend_i32u
instr_table[opcodes.I64TruncF32S] = i64_trunc_f32s
instr_table[opcodes.I64TruncF32U] = i64_trunc_f32u
instr_table[opcodes.I64TruncF64S] = i64_trunc_f64s
instr_table[opcodes.I64TruncF64U] = i64_trunc_f64u
instr_table[opcodes.F32ConvertI32S] = f32_convert_i32s
instr_table[opcodes.F32ConvertI32U] = f32_convert_i32u
instr_table[opcodes.F32ConvertI64S] = f32_convert_i64s
instr_table[opcodes.F32ConvertI64U] = f32_convert_i64u
instr_table[opcodes.F32DemoteF64] = f32_demote_f64
instr_table[opcodes.F64ConvertI32S] = f64_convert_i32s
instr_table[opcodes.F64ConvertI32U] = f64_convert_i32u
instr_table[opcodes.F64ConvertI64S] = f64_convert_i64s
instr_table[opcodes.F64ConvertI64U] = f64_convert_i64u
instr_table[opcodes.F64PromoteF32] = f64_promote_f32
instr_table[opcodes.I32ReinterpretF32] = i32_reinterpret_f32
instr_table[opcodes.I64ReinterpretF64] = i64_reinterpret_f64
instr_table[opcodes.F32ReinterpretI32] = f32_reinterpret_i32
instr_table[opcodes.F64ReinterpretI64] = f64_reinterpret_i64
instr_table[opcodes.I32Extend8S] = i32_extend_8s
instr_table[opcodes.I32Extend16S] = i32_extend_16s
instr_table[opcodes.I64Extend8S] = i64_extend_8s
instr_table[opcodes.I64Extend16S] = i64_extend_16s
instr_table[opcodes.I64Extend32S] = i64_extend_32s
