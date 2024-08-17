import copy
import random

from WASMixer.obfuscator.core import CodeObfuscator
from WASMixer.obfuscator.instruction_blocks import *
from WASMixer.rewriter.modify_binary import ModifyBinary

sys.setrecursionlimit(10000)


class WASMixer:

    def __init__(self, wasm_path):
        self.wasm_binary = ModifyBinary(wasm_path)
        self.code_obfuscator = CodeObfuscator(self.wasm_binary)

    def code_flatten(self, inner_func_id=None, split_num=None, collatz=False):
        """
        The code flattens function, which can choose whether to add methods against symbol execution.
        Args:
            inner_func_id: The inner function_id of the module
            split_num: The number of basic blocks
            collatz: Whether to add collatz conjecture obfuscation

        Returns:
        """

        if collatz is False:
            if inner_func_id is None:
                for func_id, func in enumerate(self.code_obfuscator.wasm_binary.module.code_sec):
                    block_num = split_num
                    if split_num is None:
                        block_num = int(len(func.expr) / 10)
                    if len(func.expr) <= 10 or len(func.expr) <= block_num:
                        continue

                    functype = self.wasm_binary.module.type_sec[self.wasm_binary.module.func_sec[func_id]]
                    flattened_instrs = self.code_obfuscator.instr_flatten(func.expr, block_num, functype, func_id)
                    self.code_obfuscator.wasm_binary.module.code_sec[func_id].expr = flattened_instrs

            else:
                func_expr = self.code_obfuscator.wasm_binary.module.code_sec[inner_func_id].expr
                if split_num is None:
                    split_num = int(len(func_expr) / 10)
                if len(func_expr) <= 10 or len(func_expr) <= split_num:
                    return

                functype = self.wasm_binary.module.type_sec[self.wasm_binary.module.func_sec[inner_func_id]]
                flattened_instrs = self.code_obfuscator.instr_flatten(func_expr, split_num, functype, inner_func_id)
                self.code_obfuscator.wasm_binary.module.code_sec[inner_func_id].expr = flattened_instrs


        elif collatz is True:
            collatz_instrs_template = [
                Instruction(Block, BlockArgs(-64, [])),
                Instruction(Block, BlockArgs(-64)),
                Instruction(LocalGet, 0),
                Instruction(Return)
            ]
            collatz_instrs_template[0].args.instrs = [
                Instruction(Block, BlockArgs(-64)),
                Instruction(I32Const, 32),
                Instruction(LocalSet, 0)
            ]
            collatz_instrs_template[0].args.instrs[0].args.instrs = [
                Instruction(I32Const, 282796222),
                Instruction(LocalGet, 0),
                Instruction(I32LeU),
                Instruction(BrIf, 0),
                Instruction(Br, 1)
            ]
            collatz_instrs_template[1].args.instrs = [Instruction(Loop, BlockArgs(-64))]
            collatz_instrs_template[1].args.instrs[0].args.instrs = [
                Instruction(LocalGet, 0),
                Instruction(I32Const, 1),
                Instruction(I32LeU),
                Instruction(BrIf, 1),
                Instruction(Block, BlockArgs(-64))
            ]
            collatz_instrs_template[1].args.instrs[0].args.instrs[4].args.instrs = [
                Instruction(Block, BlockArgs(-64)),
                Instruction(LocalGet, 0),
                Instruction(I32Const, 2),
                Instruction(I32DivU),
                Instruction(LocalSet, 0),
                Instruction(Br, 1)
            ]
            collatz_instrs_template[1].args.instrs[0].args.instrs[4].args.instrs[0].args.instrs = [
                Instruction(LocalGet, 0),
                Instruction(I32Const, 2),
                Instruction(I32RemU),
                Instruction(I32Eqz),
                Instruction(BrIf, 0),
                Instruction(LocalGet, 0),
                Instruction(I32Const, 3),
                Instruction(I32Mul),
                Instruction(I32Const, 1),
                Instruction(I32Add),
                Instruction(LocalSet, 0),
                Instruction(Br, 2)
            ]
            collatz_functype = FuncType(0x60, [ValTypeI32, ValTypeI32], [ValTypeI32])
            collatz_locals_val = [Locals(1, ValTypeI32)]
            collatz_func_id = self.code_obfuscator.wasm_binary.add_function(collatz_functype, collatz_locals_val,
                                                                            copy.deepcopy(collatz_instrs_template))

            if inner_func_id is None:
                for func_id, func in enumerate(self.code_obfuscator.wasm_binary.module.code_sec):
                    if (func_id + self.code_obfuscator.wasm_binary.get_import_func_num()) == collatz_func_id:
                        continue

                    block_num = split_num
                    if split_num is None:
                        block_num = int(len(func.expr) / 10)
                    if len(func.expr) <= 10 or len(func.expr) <= block_num:
                        continue

                    functype = self.wasm_binary.module.type_sec[self.wasm_binary.module.func_sec[func_id]]
                    flattened_instrs = self.code_obfuscator.instr_flatten(func.expr, block_num, functype,
                                                                          func_id, collatz_func_id)
                    self.code_obfuscator.wasm_binary.module.code_sec[func_id].expr = flattened_instrs


            else:
                func_expr = self.code_obfuscator.wasm_binary.module.code_sec[inner_func_id].expr
                if split_num is None:
                    split_num = int(len(func_expr) / 10)
                if len(func_expr) <= 10 or len(func_expr) <= split_num:
                    return

                functype = self.wasm_binary.module.type_sec[self.wasm_binary.module.func_sec[inner_func_id]]
                flattened_instrs = self.code_obfuscator.instr_flatten(func_expr, split_num, functype,
                                                                      inner_func_id, collatz_func_id)
                self.code_obfuscator.wasm_binary.module.code_sec[inner_func_id].expr = flattened_instrs

    def alias_disruption(self, collatz=False):
        """
        Obfuscate call instructions to call_indirect instructions in the wasm module,
        which can choose whether to add methods against symbol execution.
        Args:
            collatz: Whether to add collatz conjecture obfuscation

        Returns:

        """
        if collatz is False:
            self.code_obfuscator.alias_disruption()
        elif collatz is True:
            collatz_instrs_template = [
                Instruction(Block, BlockArgs(-64, [])),
                Instruction(Block, BlockArgs(-64)),
                Instruction(LocalGet, 0),
                Instruction(Return)
            ]
            collatz_instrs_template[0].args.instrs = [
                Instruction(Block, BlockArgs(-64)),
                Instruction(I32Const, 32),
                Instruction(LocalSet, 0)
            ]
            collatz_instrs_template[0].args.instrs[0].args.instrs = [
                Instruction(I32Const, 282796222),
                Instruction(LocalGet, 0),
                Instruction(I32LeU),
                Instruction(BrIf, 0),
                Instruction(Br, 1)
            ]
            collatz_instrs_template[1].args.instrs = [Instruction(Loop, BlockArgs(-64))]
            collatz_instrs_template[1].args.instrs[0].args.instrs = [
                Instruction(LocalGet, 0),
                Instruction(I32Const, 1),
                Instruction(I32LeU),
                Instruction(BrIf, 1),
                Instruction(Block, BlockArgs(-64))
            ]
            collatz_instrs_template[1].args.instrs[0].args.instrs[4].args.instrs = [
                Instruction(Block, BlockArgs(-64)),
                Instruction(LocalGet, 0),
                Instruction(I32Const, 2),
                Instruction(I32DivU),
                Instruction(LocalSet, 0),
                Instruction(Br, 1)
            ]
            collatz_instrs_template[1].args.instrs[0].args.instrs[4].args.instrs[0].args.instrs = [
                Instruction(LocalGet, 0),
                Instruction(I32Const, 2),
                Instruction(I32RemU),
                Instruction(I32Eqz),
                Instruction(BrIf, 0),
                Instruction(LocalGet, 0),
                Instruction(I32Const, 3),
                Instruction(I32Mul),
                Instruction(I32Const, 1),
                Instruction(I32Add),
                Instruction(LocalSet, 0),
                Instruction(Br, 2)
            ]
            collatz_functype = FuncType(0x60, [ValTypeI32, ValTypeI32], [ValTypeI32])
            collatz_locals_val = [Locals(1, ValTypeI32)]
            collatz_func_id = self.code_obfuscator.wasm_binary.add_function(collatz_functype, collatz_locals_val,
                                                                            copy.deepcopy(collatz_instrs_template))

            self.code_obfuscator.alias_disruption_collatz(collatz_func_id)

    def memory_obfuscation(self, key):
        """
        Obfuscate linear memory, the xor encryption algorithm is used by default, and the key is the encrypted key.
        Args:
            key: The encrypted key

        Returns:

        """
        self.code_obfuscator.memory_encrypten_obfuscation(key)

    def name_obfuscation(self):
        """
        Name obfuscation, obfuscate the readable strings in the import and export sections of wasm,
        and obfuscate the readable strings in the debugging information in the custom section
        Args:

        Returns:

        """

        # import export
        for item in self.wasm_binary.module.import_sec:
            if item.module != 'wasi_snapshot_preview1':
                item.module = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', len(item.module)))
                item.name = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', len(item.name)))
        for item in self.wasm_binary.module.export_sec:
            if item.name != '_start' and item.desc.tag == 0:
                item.name = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', len(item.name)))
        # debug information
        for custom in self.wasm_binary.module.custom_secs:
            if custom.name == 'name':
                if custom.name_data.funcNameSubSec != None:
                    for func_name in custom.name_data.funcNameSubSec:
                        func_name.name = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', len(func_name.name)))
                if custom.name_data.dataNameSubSec != None:
                    for data_name in custom.name_data.dataNameSubSec:
                        data_name.name = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', len(data_name.name)))
                if custom.name_data.globalNameSubSec != None:
                    for global_name in custom.name_data.globalNameSubSec:
                        global_name.name = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', len(global_name.name)))
            else:
                length = len(custom.custom_sec_data)
                custom.name = '.' + ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', len(custom.name)))
                custom.custom_sec_data = bytes([random.randint(1, 80)] * length)
