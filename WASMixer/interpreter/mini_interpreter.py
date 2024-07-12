from .instructions import *


class MiniInterpreter:

    def __init__(self, instr_list: list, wasm_binary, inner_func_id):
        self.instr_list = instr_list
        self.val_stack = []
        self.wasm_binary = wasm_binary
        self.inner_func_id = inner_func_id

    def get_stack_snapshot(self, instr_index: int):
        instr_list = self.instr_list[0:instr_index]
        stack = []
        for i in range(instr_index):
            instr = self.instr_list[i]
            instr_table[instr.opcode](self, instr.args, stack)

        return stack
