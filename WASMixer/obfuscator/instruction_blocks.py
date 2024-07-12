import sys
from typing import List
from enum import Enum, unique

from WASMixer.parser.instruction import *
from WASMixer.parser.module import *
from WASMixer.parser.opcodes import *
from WASMixer.parser.types import *


# load
# address offset | data
def i32_load():
    instrs = [Instruction(LocalGet, 0),
              Instruction(LocalGet, 1),
              Instruction(I32Add),
              Instruction(I32Load),
              Instruction(GlobalGet, None),  # key
              Instruction(I32Xor)]
    return instrs


# address offset | data
def i64_load():
    instrs = [Instruction(LocalGet, 0),
              Instruction(LocalGet, 1),
              Instruction(I32Add),
              Instruction(I64Load),
              Instruction(GlobalGet, None),  # key
              Instruction(I64Xor)]
    return instrs


def f32_load():
    instrs = [Instruction(LocalGet, 0),
              Instruction(LocalGet, 1),
              Instruction(I32Add),
              Instruction(F32Load),
              Instruction(I32ReinterpretF32),
              Instruction(GlobalGet, None),  # key
              Instruction(I32Xor),
              Instruction(F32ReinterpretI32)]
    return instrs


def f64_load():
    instrs = [Instruction(LocalGet, 0),
              Instruction(LocalGet, 1),
              Instruction(I32Add),
              Instruction(F64Load),
              Instruction(I64ReinterpretF64),
              Instruction(GlobalGet, None),  # key
              Instruction(I64Xor),
              Instruction(F64ReinterpretI64)]
    return instrs


def i32_load_8s():
    instrs = [Instruction(LocalGet, 0),
              Instruction(LocalGet, 1),
              Instruction(I32Add),
              Instruction(I32Load),
              Instruction(LocalTee, 0),
              Instruction(GlobalGet, None),  # key
              Instruction(I32Xor)]
    return instrs


def i32_load_8u():
    instrs = [Instruction(LocalGet, 0),
              Instruction(LocalGet, 1),
              Instruction(I32Add),
              Instruction(),
              Instruction(GlobalGet, None),  # key
              Instruction(I32Xor)]
    return instrs
    pass


def i32_load_16s():
    pass


def i32_load_16u():
    pass


def i64_load_8s():
    pass


def i64_load_8u():
    pass


def i64_load_16s():
    pass


def i64_load_16u():
    pass


def i64_load_32s():
    pass


def i64_load_32u():
    pass


# store
def i32_store():
    pass


def i64_store():
    pass


def f32_store():
    pass


def f64_store():
    pass


def i32_store_8():
    pass


def i32_store_16():
    pass


def i64_store_8():
    pass


def i64_store_16():
    pass


def i64_store_32():
    pass


@unique
class LoadInstr(Enum):
    I32Load = 0x28  # i32.load m
    I64Load = 0x29  # i64.load m
    F32Load = 0x2A  # f32.load m
    F64Load = 0x2B  # f64.load m
    I32Load8S = 0x2C  # i32.load8_s m
    I32Load8U = 0x2D  # i32.load8_u m
    I32Load16S = 0x2E  # i32.load16_s m
    I32Load16U = 0x2F  # i32.load16_u m
    I64Load8S = 0x30  # i64.load8_s m
    I64Load8U = 0x31  # i64.load8_u m
    I64Load16S = 0x32  # i64.load16_s m
    I64Load16U = 0x33  # i64.load16_u m
    I64Load32S = 0x34  # i64.load32_s m
    I64Load32U = 0x35  # i64.load32_u m


@unique
class StoreInstr(Enum):
    I32Store = 0x36  # i32.store m
    I64Store = 0x37  # i64.store m
    F32Store = 0x38  # f32.store m
    F64Store = 0x39  # f64.store m
    I32Store8 = 0x3A  # i32.store8 m
    I32Store16 = 0x3B  # i32.store16 m
    I64Store8 = 0x3C  # i64.store8 m
    I64Store16 = 0x3D  # i64.store16 m
    I64Store32 = 0x3E  # i64.store32 m



def get_encrypten_store():
    encrypten_store = [Instruction(LocalGet, 0),
                       Instruction(LocalGet, 2),
                       Instruction(I32Add),
                       Instruction(LocalSet, 0),
                       Instruction(Block, BlockArgs(-64)),
                       Instruction(Block, BlockArgs(-64))]

    encrypten_store[4].args.instrs = [Instruction(Block, BlockArgs(-64)),
                                      Instruction(LocalGet, 1),
                                      Instruction(GlobalGet, None),  # key
                                      Instruction(I64Xor),
                                      Instruction(LocalSet, 1)]

    encrypten_store[4].args.instrs[0].args.instrs = [Instruction(Br, 1)]  # min <= address <= max

    encrypten_store[5].args.instrs = [Instruction(Block, BlockArgs(-64)),
                                      Instruction(LocalGet, 0),
                                      Instruction(LocalGet, 1),
                                      Instruction(I64Store, MemArg()),
                                      Instruction(Br, 0)]
    encrypten_store[5].args.instrs[0].args.instrs = [Instruction(Block, BlockArgs(-64)),
                                                     Instruction(LocalGet, 0),
                                                     Instruction(LocalGet, 1),
                                                     Instruction(I64Store32, MemArg()),
                                                     Instruction(Br, 1)]
    encrypten_store[5].args.instrs[0].args.instrs[0].args.instrs = [Instruction(Block, BlockArgs(-64)),
                                                                    Instruction(LocalGet, 0),
                                                                    Instruction(LocalGet, 1),
                                                                    Instruction(I64Store16, MemArg()),
                                                                    Instruction(Br, 2)]
    encrypten_store[5].args.instrs[0].args.instrs[0].args.instrs[0].args.instrs = [
        Instruction(Block, BlockArgs(-64, [Instruction(LocalGet, 3),
                                           Instruction(BrTable, BrTableArgs([0, 1, 2, 3], 0))])),
        Instruction(LocalGet, 0),
        Instruction(LocalGet, 1),
        Instruction(I64Store8, MemArg()),
        Instruction(Br, 3)]

    return encrypten_store


def get_decrypten_load():
    decrypten_load = [Instruction(LocalGet, 0),
                      Instruction(LocalGet, 1),
                      Instruction(I32Add),
                      Instruction(LocalSet, 0),
                      Instruction(Block, BlockArgs(-64)),
                      Instruction(Block, BlockArgs(-64)),
                      Instruction(LocalGet, 4)]
    decrypten_load[4].args.instrs = [Instruction(Block, BlockArgs(-64)),
                         Instruction(LocalGet, 0),
                         Instruction(I64Load, MemArg()),
                         Instruction(GlobalGet, None),  # key
                         Instruction(I64Xor),
                         Instruction(LocalSet, 4)]

    decrypten_load[4].args.instrs[0].args.instrs = [Instruction(LocalGet, 0),
                                                    Instruction(I64Load, MemArg()),
                                                    Instruction(LocalSet, 4),
                                                    Instruction(Br, 1)]

    decrypten_load[5].args.instrs = [Instruction(Block, BlockArgs(-64)),
                                     Instruction(Block, BlockArgs(-64)), ]
    decrypten_load[5].args.instrs[0].args.instrs = [Instruction(LocalGet, 2),
                                                    Instruction(I32Const, 1),
                                                    Instruction(I32Eq),
                                                    Instruction(BrIf, 0),
                                                    Instruction(LocalGet, 2),
                                                    Instruction(I32Const, 2),
                                                    Instruction(I32Eq),
                                                    Instruction(BrIf, 1),
                                                    Instruction(Block, BlockArgs(-64))]
    decrypten_load[5].args.instrs[0].args.instrs[8].args.instrs = [Instruction(Block, BlockArgs(-64)),
                                                                   Instruction(LocalGet, 4),
                                                                   Instruction(I64Const, 4294967295),
                                                                   Instruction(I64And),
                                                                   Instruction(LocalSet, 4),
                                                                   Instruction(Br, 2)]
    decrypten_load[5].args.instrs[0].args.instrs[8].args.instrs[0].args.instrs = [Instruction(Block, BlockArgs(-64)),
                                                                                  Instruction(LocalGet, 4),
                                                                                  Instruction(I64Const, 65535),
                                                                                  Instruction(I64And),
                                                                                  Instruction(LocalSet, 4),
                                                                                  Instruction(Br, 3)]

    decrypten_load[5].args.instrs[0].args.instrs[8].args.instrs[0].args.instrs[0].args.instrs = \
        [Instruction(Block, BlockArgs(-64, [Instruction(LocalGet, 3),
                                            Instruction(BrTable, BrTableArgs([0, 1, 2], 3))])),
         Instruction(LocalGet, 4),
         Instruction(I64Const, 255),
         Instruction(I64And),
         Instruction(LocalSet, 4),
         Instruction(Br, 4)]

    decrypten_load[5].args.instrs[1].args.instrs = [Instruction(Block, BlockArgs(-64)),
                                                    Instruction(LocalGet, 4),
                                                    Instruction(I64Const, 4294967295),
                                                    Instruction(I64And),
                                                    Instruction(I64Extend32S),
                                                    Instruction(LocalSet, 4),
                                                    Instruction(Br, 1)]
    decrypten_load[5].args.instrs[1].args.instrs[0].args.instrs = [Instruction(Block, BlockArgs(-64)),
                                                                   Instruction(LocalGet, 4),
                                                                   Instruction(I64Const, 65535),
                                                                   Instruction(I64And),
                                                                   Instruction(I64Extend16S),
                                                                   Instruction(LocalSet, 4),
                                                                   Instruction(Br, 2)]
    decrypten_load[5].args.instrs[1].args.instrs[0].args.instrs[0].args.instrs = [
        Instruction(Block, BlockArgs(-64, [Instruction(LocalGet, 3),
                                           Instruction(BrTable, BrTableArgs([0, 1, 2], 3))])),
        Instruction(LocalGet, 4),
        Instruction(I64Const, 255),
        Instruction(I64And),
        Instruction(I64Extend8S),
        Instruction(LocalSet, 4),
        Instruction(Br, 3)]
    return decrypten_load


def compare_range_instrs(start, end):
    instrs = [Instruction(LocalGet, 0),
              Instruction(I32Const, end),
              Instruction(I32LeU),
              Instruction(LocalGet, 0),
              Instruction(I32Const, start),
              Instruction(I32GeU),
              Instruction(I32Add),
              Instruction(I32Const, 2),
              Instruction(I32Eq),
              Instruction(BrIf, 0)]
    return instrs



Random_get_functype = FuncType(0x60, [], [ValTypeI32])
Random_get_locals_val = [Locals(2, ValTypeI32)]

Xor_shift_instrs_template = [
    Instruction(LocalGet, 0),
    Instruction(I32Const, 13),
    Instruction(I32Shl),
    Instruction(LocalGet, 0),
    Instruction(I32Xor),
    Instruction(LocalSet, 0),

    Instruction(LocalGet, 0),
    Instruction(I32Const, 7),
    Instruction(I32ShrU),
    Instruction(LocalGet, 0),
    Instruction(I32Xor),
    Instruction(LocalSet, 0),

    Instruction(LocalGet, 0),
    Instruction(I32Const, 17),
    Instruction(I32Shl),
    Instruction(LocalGet, 0),
    Instruction(I32Xor),
    Instruction(LocalSet, 0),

    Instruction(LocalGet, 0),
    Instruction(Return)
]

Xor_shift_functype = FuncType(0x60, [ValTypeI32], [ValTypeI32])

Compute_stack_memory = [Instruction(LocalGet, 0),
                        Instruction(LocalGet, 1),
                        Instruction(I32Sub),
                        Instruction(LocalSet, 2),
                        Instruction(I32Const, 0),
                        Instruction(LocalSet, 3),
                        Instruction(Block, BlockArgs(-64)),
                        Instruction(LocalGet, 3)]
Compute_stack_memory[6].args.instrs = [Instruction(Loop, BlockArgs(-64))]
Compute_stack_memory[6].args.instrs[0].args.instrs = [Instruction(LocalGet, 0),
                                                      Instruction(I32Const, 4),
                                                      Instruction(I32Sub),
                                                      Instruction(LocalSet, 0),
                                                      Instruction(LocalGet, 0),
                                                      Instruction(LocalGet, 2),
                                                      Instruction(I32LtS),
                                                      Instruction(BrIf, 1),
                                                      Instruction(LocalGet, 0),
                                                      Instruction(I32Load, MemArg(2, 0)),
                                                      Instruction(LocalGet, 3),
                                                      Instruction(I32Add),
                                                      Instruction(LocalSet, 3),
                                                      Instruction(Br, 0)]
Compute_stack_memory_functype = FuncType(0x60, [ValTypeI32, ValTypeI32], [ValTypeI32])
Compute_stack_memory_locals_val = [Locals(2, ValTypeI32)]