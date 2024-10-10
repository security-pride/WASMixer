from WASMixer.obfuscator.utils import *


class CodeObfuscator:

    def __init__(self, binary):
        self.wasm_binary = binary

    def instr_flatten(self, instr_list, split_num, block_type, func_id, Collatz_func_id=None):

        return_exist = False
        if instr_list[len(instr_list) - 1].opcode == Return:
            return_exist = True

        jump_flag_local = self.wasm_binary.add_new_local_to_func(func_id, ValTypeI32)

        code_blocks, new_local_i32, new_local_i64, new_local_f32, new_local_f64 = code_block_splitting(self.wasm_binary, instr_list, split_num, func_id)

        basic_blocks = []
        for cb in code_blocks:
            basic_blocks.append(cb['instrs'])

        # Build distribution block
        br_table_list = list(range(len(basic_blocks) + 1))
        dispatcher_instrs = [Instruction(LocalGet, jump_flag_local),
                             Instruction(BrTable, BrTableArgs(br_table_list, 0))]

        dispatcher_block = Instruction(Block, BlockArgs(BlockTypeEmpty, dispatcher_instrs))

        for _, bb in enumerate(basic_blocks):
            for instr in bb:
                if instr.opcode in [Br, BrIf]:
                    instr.args += len(basic_blocks) - _ + 1 + 1
                # elif instr.opcode == BrTable:
                #     for label_id in instr.args.labels:
                #         instr.args.labels[label_id] += len(basic_blocks) - _ + 1 + 1
                #     if instr.args.default is not None:
                #         instr.args.default += len(basic_blocks) - _ + 1 + 1

            # Wrap the instructions with block instruction
            basic_blocks[_] = Instruction(Block, BlockArgs(BlockTypeEmpty, bb))

        for _, bb in enumerate(basic_blocks):

            # Build next jump
            if code_blocks[_]['id'] == (len(code_blocks) - 1):
                param_type_list = block_type.param_types

                if param_type_list != [] and Collatz_func_id is not None:
                    jump_flag = len(code_blocks)
                    collatz_code = []

                    for param_id, param_type in enumerate(param_type_list):
                        if param_type == 127:
                            collatz_code.extend([
                                Instruction(LocalGet, param_id),
                                Instruction(I32Const, random.randint(1, 1000)),
                                Instruction(I32Mul)])
                        elif param_type == 126:
                            collatz_code.extend([
                                Instruction(LocalGet, param_id),
                                Instruction(I64Const, random.randint(1, 1000)),
                                Instruction(I64Mul),
                                Instruction(I32WrapI64)])
                        elif param_type == 125:
                            collatz_code.extend([
                                Instruction(LocalGet, param_id),
                                Instruction(F32Const, random.randint(1, 1000)),
                                Instruction(F32Mul),
                                Instruction(I32ReinterpretF32)])
                        elif param_type == 124:
                            collatz_code.extend([
                                Instruction(LocalGet, param_id),
                                Instruction(F64Const, random.randint(1, 1000)),
                                Instruction(F64Mul),
                                Instruction(I64ReinterpretF64),
                                Instruction(I32WrapI64)])
                        if param_id != 0:
                            collatz_code.append(Instruction(I32Add))

                    collatz_code.extend([
                        Instruction(I32Const, random.randint(1050, 2000)),
                        Instruction(I32Add),
                        Instruction(I32Const, random.randint(1, 2000)),
                        Instruction(Call, Collatz_func_id),
                        Instruction(I32Const, jump_flag - 1),
                        Instruction(I32Add),
                        Instruction(LocalSet, jump_flag_local),

                        # Jump to distribution block
                        Instruction(Br, len(code_blocks) - _),
                    ])
                    bb.args.instrs.extend(collatz_code)
                else:
                    bb.args.instrs.append(Instruction(I32Const, len(code_blocks)))
                    bb.args.instrs.append(Instruction(LocalSet, jump_flag_local))
                    bb.args.instrs.append(Instruction(Br, len(code_blocks) - _))
            else:
                for next_id, cb in enumerate(code_blocks):
                    if cb['id'] == (code_blocks[_]['id'] + 1):
                        param_type_list = block_type.param_types

                        if param_type_list != [] and Collatz_func_id is not None:
                            collatz_code = []
                            for param_id, param_type in enumerate(param_type_list):
                                if param_type == 127:
                                    collatz_code.extend([
                                        Instruction(LocalGet, param_id),
                                        Instruction(I32Const, random.randint(1, 1000)),
                                        Instruction(I32Mul)])
                                elif param_type == 126:
                                    collatz_code.extend([
                                        Instruction(LocalGet, param_id),
                                        Instruction(I64Const, random.randint(1, 1000)),
                                        Instruction(I64Mul),
                                        Instruction(I32WrapI64)])
                                elif param_type == 125:
                                    collatz_code.extend([
                                        Instruction(LocalGet, param_id),
                                        Instruction(F32Const, random.randint(1, 1000)),
                                        Instruction(F32Mul),
                                        Instruction(I32ReinterpretF32)])
                                elif param_type == 124:
                                    collatz_code.extend([
                                        Instruction(LocalGet, param_id),
                                        Instruction(F64Const, random.randint(1, 1000)),
                                        Instruction(F64Mul),
                                        Instruction(I64ReinterpretF64),
                                        Instruction(I32WrapI64)])
                                if param_id != 0:
                                    collatz_code.append(Instruction(I32Add))

                            if next_id == 0:
                                collatz_code.extend([
                                    Instruction(I32Const, random.randint(1050, 2000)),
                                    Instruction(I32Add),
                                    Instruction(I32Const, random.randint(1, 2000)),
                                    Instruction(Call, Collatz_func_id),
                                    Instruction(I32Const, 1),
                                    Instruction(I32Sub),
                                    Instruction(LocalSet, jump_flag_local),

                                    # Jump to distribution block
                                    Instruction(Br, len(basic_blocks) - _),
                                ])
                            elif next_id == 1:
                                collatz_code.extend([
                                    Instruction(I32Const, random.randint(1050, 2000)),
                                    Instruction(I32Add),
                                    Instruction(I32Const, random.randint(1, 2000)),
                                    Instruction(Call, Collatz_func_id),
                                    Instruction(LocalSet, jump_flag_local),

                                    # Jump to distribution block
                                    Instruction(Br, len(basic_blocks) - _),
                                ])
                            # jump flag = next id
                            else:
                                collatz_code.extend([
                                    Instruction(I32Const, random.randint(1050, 2000)),
                                    Instruction(I32Add),
                                    Instruction(I32Const, random.randint(1050, 2000)),
                                    Instruction(Call, Collatz_func_id),
                                    Instruction(I32Const, next_id - 1),
                                    Instruction(I32Add),
                                    Instruction(LocalSet, jump_flag_local),

                                    # Jump to distribution block
                                    Instruction(Br, len(basic_blocks) - _),
                                ])

                            bb.args.instrs.extend(collatz_code)
                        else:
                            bb.args.instrs.append(Instruction(I32Const, next_id))
                            bb.args.instrs.append(Instruction(LocalSet, jump_flag_local))
                            bb.args.instrs.append(Instruction(Br, len(basic_blocks) - _))

        # Construct outer blocks
        for _, bb in enumerate(basic_blocks):
            # Insert the distribution block at the beginning of the innermost block
            if _ == 0:
                bb.args.instrs.insert(0, dispatcher_block)
            else:
                bb.args.instrs.insert(0, basic_blocks[_ - 1])

        # Build loop block
        loop_block = Instruction(Loop, BlockArgs(BlockTypeEmpty, [basic_blocks[len(basic_blocks) - 1]]))

        loop_block.args.instrs.append(Instruction(Br, 1))

        # Build the outermost block
        out_block = Instruction(Block, BlockArgs(BlockTypeEmpty, []))

        # Find the first execution basic block as the entry point
        for _, cb in enumerate(code_blocks):
            if cb['id'] == 0:
                out_block.args.instrs.append(Instruction(I32Const, _))
                out_block.args.instrs.append(Instruction(LocalSet, jump_flag_local))
        out_block.args.instrs.append(loop_block)

        # Add operands at the end to maintain stack balance
        final_instrs = []
        final_instrs.append(out_block)

        if return_exist:
            for i, result_type in enumerate(
                    self.wasm_binary.module.type_sec[self.wasm_binary.module.func_sec[func_id]].result_types):
                if result_type == ValTypeI32:
                    final_instrs.append(Instruction(LocalGet, new_local_i32[i]))
                elif result_type == ValTypeI64:
                    final_instrs.append(Instruction(LocalGet, new_local_i64[i]))
                elif result_type == ValTypeF32:
                    final_instrs.append(Instruction(LocalGet, new_local_f32[i]))
                elif result_type == ValTypeF64:
                    final_instrs.append(Instruction(LocalGet, new_local_f64[i]))
                else:
                    raise Exception("error")

            final_instrs.append(Instruction(Return))
            return final_instrs
        else:
            for i, result_type in enumerate(
                    self.wasm_binary.module.type_sec[self.wasm_binary.module.func_sec[func_id]].result_types):
                if result_type == ValTypeI32:
                    final_instrs.append(Instruction(LocalGet, new_local_i32[i]))
                elif result_type == ValTypeI64:
                    final_instrs.append(Instruction(LocalGet, new_local_i64[i]))
                elif result_type == ValTypeF32:
                    final_instrs.append(Instruction(LocalGet, new_local_f32[i]))
                elif result_type == ValTypeF64:
                    final_instrs.append(Instruction(LocalGet, new_local_f64[i]))
                else:
                    raise Exception("error")
            return final_instrs

    def alias_disruption(self):

        # Get the list of function ids called indirectly before obfuscation
        origin_funcref_list = []
        for elem in self.wasm_binary.module.elem_sec:
            origin_funcref_list.extend(elem.init)

        # Remove function ids that have been called indirectly from all function id lists
        rest_func_id_list = list(
            range(0, (self.wasm_binary.get_import_func_num() + len(self.wasm_binary.module.func_sec))))
        for i in range(len(rest_func_id_list)):
            if i in origin_funcref_list:
                rest_func_id_list.remove(i)

        # Adjust the limits of funcref elem in the table element
        add_table_funcref_limits(self.wasm_binary, len(rest_func_id_list))

        # Disrupt the list of function ids that are not indirectly called
        random.shuffle(rest_func_id_list)
        # Add a list of function ids that are not indirectly called in the elem segment
        if not self.wasm_binary.module.elem_sec:
            self.wasm_binary.module.elem_sec.append(Elem(0, [Instruction(I32Const, 1)], rest_func_id_list))
        else:
            self.wasm_binary.module.elem_sec[0].init.extend(rest_func_id_list)

        for _, func in enumerate(self.wasm_binary.module.code_sec):
            self.call_to_indirect_call(func.expr)

        # Modify the table segment, elem segment and code segment
        self.wasm_binary.modify_table_section(self.wasm_binary.module.table_sec)
        self.wasm_binary.modify_elem_section(self.wasm_binary.module.elem_sec)
        self.wasm_binary.modify_code_section(self.wasm_binary.module.code_sec)

    def call_to_indirect_call(self, expr):
        for _, instr in enumerate(expr):
            if instr.opcode == Call:
                # Get this function type id
                func_id = instr.args
                import_func_num = self.wasm_binary.get_import_func_num()
                if func_id <= (import_func_num - 1):
                    import_func_list = self.wasm_binary.get_import_func_list()
                    func_type_id = import_func_list[func_id].desc.func_type
                else:
                    func_type_id = self.wasm_binary.module.func_sec[func_id - self.wasm_binary.get_import_func_num()]
                # Build call_indirect instruction
                expr[_] = Instruction(CallIndirect, func_type_id)
                # Get the index of this function in funcref
                funcref_id = self.wasm_binary.module.elem_sec[0].init.index(func_id) + \
                             self.wasm_binary.module.elem_sec[0].offset[0].args
                # Push the funcref index on the stack
                expr.insert(_, Instruction(I32Const, funcref_id))

            # Recursive call
            elif instr.opcode in [Block, Loop]:
                self.call_to_indirect_call(instr.args.instrs)

    def alias_disruption_collatz(self, Collatz_func_id):

        # Get the list of function ids called indirectly before obfuscation
        origin_funcref_list = []
        for elem in self.wasm_binary.module.elem_sec:
            origin_funcref_list.extend(elem.init)

        # Remove function ids that have been called indirectly from all function id lists
        rest_func_id_list = list(
            range(0, (self.wasm_binary.get_import_func_num() + len(self.wasm_binary.module.func_sec))))
        for i in range(len(rest_func_id_list)):
            if i in origin_funcref_list:
                rest_func_id_list.remove(i)

            # Adjust the limits of funcref elem in the table
            add_table_funcref_limits(self.wasm_binary, len(rest_func_id_list))

            # Disrupt the list of function ids that are not indirectly called
            random.shuffle(rest_func_id_list)
            # Add a list of function ids that are not indirectly called in the elem segment
            if not self.wasm_binary.module.elem_sec:
                self.wasm_binary.module.elem_sec.append(Elem(0, [Instruction(I32Const, 1)], rest_func_id_list))
            else:
                self.wasm_binary.module.elem_sec[0].init.extend(rest_func_id_list)

            for i, func in enumerate(self.wasm_binary.module.code_sec):
                func_type = self.wasm_binary.module.type_sec[self.wasm_binary.module.func_sec[i]]
                param_type_list = func_type.param_types

                if param_type_list != [] and i != (Collatz_func_id - self.wasm_binary.get_import_func_num()):

                    stack_length = get_function_memory_stack_length(self.wasm_binary, i)
                    expr = self.wasm_binary.module.code_sec[i].expr

                    self.call_to_indirect_call_collatz(expr, Collatz_func_id,
                                                       param_type_list, stack_length)

            self.wasm_binary.modify_table_section(self.wasm_binary.module.table_sec)
            self.wasm_binary.modify_elem_section(self.wasm_binary.module.elem_sec)
            self.wasm_binary.modify_code_section(self.wasm_binary.module.code_sec)

    def call_to_indirect_call_collatz(self, expr, Collatz_func_id, param_type_list, stack_length):
        _ = 0
        while _ < len(expr):
            if expr[_].opcode == Call:
                # Get this function type id
                func_id = expr[_].args
                import_func_num = self.wasm_binary.get_import_func_num()
                if func_id <= (import_func_num - 1):
                    func_type_id = self.wasm_binary.module.import_sec[func_id].desc.func_type
                else:
                    func_type_id = self.wasm_binary.module.func_sec[func_id - self.wasm_binary.get_import_func_num()]
                # Build call_indirect instruction
                expr[_] = Instruction(CallIndirect, func_type_id)
                # Get the index of this function in funcref
                funcref_id = self.wasm_binary.module.elem_sec[0].init.index(func_id) + \
                             self.wasm_binary.module.elem_sec[0].offset[0].args

                jump_flag = funcref_id

                Br_flag_Collatz_template = []

                for param_id, param_type in enumerate(param_type_list):

                    if param_type == 127:
                        Br_flag_Collatz_template.extend([
                            Instruction(LocalGet, param_id),
                            Instruction(I32Const, random.randint(1, 1000)),
                            Instruction(I32Mul)])
                    elif param_type == 126:
                        Br_flag_Collatz_template.extend([
                            Instruction(LocalGet, param_id),
                            Instruction(I64Const, random.randint(1, 1000)),
                            Instruction(I64Mul),
                            Instruction(I32WrapI64)])
                    elif param_type == 125:
                        Br_flag_Collatz_template.extend([
                            Instruction(LocalGet, param_id),
                            Instruction(F32Const, random.randint(1, 1000)),
                            Instruction(F32Mul),
                            Instruction(I32ReinterpretF32)])
                    elif param_type == 124:
                        Br_flag_Collatz_template.extend([
                            Instruction(LocalGet, param_id),
                            Instruction(F64Const, random.randint(1, 1000)),
                            Instruction(F64Mul),
                            Instruction(I64ReinterpretF64),
                            Instruction(I32WrapI64)])
                    if param_id != 0:
                        Br_flag_Collatz_template.append(Instruction(I32Add))


                Br_flag_Collatz_template.extend([
                    Instruction(I32Const, random.randint(1050, 2000)),
                    Instruction(Call, Collatz_func_id),
                    Instruction(I32Const, jump_flag - 1),
                    Instruction(I32Add)
                ])

                Br_flag_Collatz_template[-2].args = jump_flag - 1

                Br_flag_Collatz = copy.deepcopy(Br_flag_Collatz_template)
                print(id(Br_flag_Collatz))
                for i in reversed(Br_flag_Collatz):
                    expr.insert(_, i)

                _ += (len(Br_flag_Collatz_template) + 1)
            # Recursive call
            elif expr[_].opcode in [Block, Loop]:
                self.call_to_indirect_call_collatz(expr[_].args.instrs, Collatz_func_id,
                                                   param_type_list, stack_length)
                _ += 1
            else:
                _ += 1

    def memory_encrypten_obfuscation(self, key=None):

        if self.wasm_binary.module.data_sec == []:
            return

        if key is None:
            key = random.randint(1, 128)

        global_key = bytes([key, key, key, key])
        global_key = int.from_bytes(global_key, byteorder='little')
        global_key_id = self.wasm_binary.append_global_variable(ValTypeI64, global_key)
        self.wasm_binary.modify_global_section(self.wasm_binary.module.global_sec)

        decrypten_load_funcbody = get_decrypten_load()
        decrypten_load_funcbody[4].args.instrs[3].args = global_key_id

        encrypten_store_funcbody = get_encrypten_store()
        encrypten_store_funcbody[4].args.instrs[2].args = global_key_id

        # encrypten memory data
        for data in self.wasm_binary.module.data_sec:
            memory_data = data.init
            start = data.offset[0].args
            end = start + len(data.init) - 1
            instrs = compare_range_instrs(start, end)
            encrypten_store_funcbody[4].args.instrs[0].args.instrs = instrs + encrypten_store_funcbody[4].args.instrs[
                0].args.instrs
            decrypten_load_funcbody[4].args.instrs[0].args.instrs = instrs + decrypten_load_funcbody[4].args.instrs[
                0].args.instrs
            for _, byte in enumerate(memory_data):
                memory_data[_] = key ^ memory_data[_]
        self.wasm_binary.modify_data_section(self.wasm_binary.module.data_sec)

        decrypten_load_functype = FuncType(param_types=[ValTypeI32, ValTypeI32, ValTypeI32, ValTypeI32],
                                           result_types=[ValTypeI64])
        decrypten_load_locals = Locals(1, ValTypeI64)
        decrypten_load_funcid = self.wasm_binary.add_function(decrypten_load_functype,
                                                              [decrypten_load_locals],
                                                              decrypten_load_funcbody)

        encrypten_store_functype = FuncType(param_types=[ValTypeI32, ValTypeI64, ValTypeI32, ValTypeI32],
                                            result_types=[])
        encrypten_store_funcid = self.wasm_binary.add_function(encrypten_store_functype, [],
                                                               encrypten_store_funcbody)

        if encrypten_store_funcid <= decrypten_load_funcid:
            decrypten_load_funcid += 1

        for _, code in enumerate(self.wasm_binary.module.code_sec):
            import_func_num = self.wasm_binary.get_import_func_num()
            if _ not in [decrypten_load_funcid - import_func_num, encrypten_store_funcid - import_func_num]:
                self.hook_load_store_instr(code.expr, decrypten_load_funcid, encrypten_store_funcid)

        self.wasm_binary.emit_binary()

    def hook_load_store_instr(self, instrs, decrypten_load_funcid, encrypten_store_funcid):
        for _, i in enumerate(instrs):
            if i.opcode in [Block, Loop]:
                self.hook_load_store_instr(i.args.instrs, decrypten_load_funcid, encrypten_store_funcid)
            elif i.opcode == If:
                self.hook_load_store_instr(i.args.instrs1, decrypten_load_funcid, encrypten_store_funcid)
                self.hook_load_store_instr(i.args.instrs2, decrypten_load_funcid, encrypten_store_funcid)
            else:
                match i.opcode:
                    case LoadInstr.I32Load.value:
                        offset = i.args.offset
                        signed = 2
                        length = random.randint(1, 100)
                        instrs.insert(_ + 1, Instruction(I32WrapI64))
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 5
                    case LoadInstr.I64Load.value:
                        offset = i.args.offset
                        signed = 2
                        length = random.randint(1, 100)
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 4
                    case LoadInstr.F32Load.value:
                        offset = i.args.offset
                        signed = 2
                        length = random.randint(1, 100)
                        instrs.insert(_ + 1, Instruction(F32ReinterpretI32))
                        instrs.insert(_ + 1, Instruction(I32WrapI64))
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 6
                    case LoadInstr.F64Load.value:
                        offset = i.args.offset
                        signed = 2
                        length = random.randint(1, 100)
                        instrs.insert(_ + 1, Instruction(F64ReinterpretI64))
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 5
                    case LoadInstr.I32Load8S.value:
                        offset = i.args.offset
                        signed = 1
                        length = 0
                        instrs.insert(_ + 1, Instruction(I32WrapI64))
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 5
                    case LoadInstr.I32Load8U.value:
                        offset = i.args.offset
                        signed = 0
                        length = 0
                        instrs.insert(_ + 1, Instruction(I32WrapI64))
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 5
                    case LoadInstr.I32Load16S.value:
                        offset = i.args.offset
                        signed = 1
                        length = 1
                        instrs.insert(_ + 1, Instruction(I32WrapI64))
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 5
                    case LoadInstr.I32Load16U.value:
                        offset = i.args.offset
                        signed = 0
                        length = 1
                        instrs.insert(_ + 1, Instruction(I32WrapI64))
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 5
                    case LoadInstr.I64Load8S.value:
                        offset = i.args.offset
                        signed = 1
                        length = 0
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 4
                    case LoadInstr.I64Load8U.value:
                        offset = i.args.offset
                        signed = 0
                        length = 0
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 4
                    case LoadInstr.I64Load16S.value:
                        offset = i.args.offset
                        signed = 1
                        length = 1
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 4
                    case LoadInstr.I64Load16U.value:
                        offset = i.args.offset
                        signed = 0
                        length = 1
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 4
                    case LoadInstr.I64Load32S.value:
                        offset = i.args.offset
                        signed = 1
                        length = 2
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 4
                    case LoadInstr.I64Load32U.value:
                        offset = i.args.offset
                        signed = 0
                        length = 2
                        instrs[_] = Instruction(Call, decrypten_load_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, signed))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 4
                    # store
                    case StoreInstr.I32Store.value:
                        offset = i.args.offset
                        length = 2
                        instrs[_] = Instruction(Call, encrypten_store_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, offset))
                        instrs.insert(_, Instruction(I64ExtendI32U))
                        _ += 4
                    case StoreInstr.I64Store.value:
                        offset = i.args.offset
                        length = 3
                        instrs[_] = Instruction(Call, encrypten_store_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 3
                    case StoreInstr.F32Store.value:
                        offset = i.args.offset
                        length = 2
                        instrs[_] = Instruction(Call, encrypten_store_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, offset))
                        instrs.insert(_, Instruction(I64ExtendI32U))
                        instrs.insert(_, Instruction(I32ReinterpretF32))
                        _ += 5
                    case StoreInstr.F64Store.value:
                        offset = i.args.offset
                        length = 3
                        instrs[_] = Instruction(Call, encrypten_store_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, offset))
                        instrs.insert(_, Instruction(I64ReinterpretF64))
                        _ += 4
                    case StoreInstr.I32Store8.value:
                        offset = i.args.offset
                        length = 0
                        instrs[_] = Instruction(Call, encrypten_store_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, offset))
                        instrs.insert(_, Instruction(I64ExtendI32U))
                        _ += 4
                    case StoreInstr.I32Store16.value:
                        offset = i.args.offset
                        length = 1
                        instrs[_] = Instruction(Call, encrypten_store_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, offset))
                        instrs.insert(_, Instruction(I64ExtendI32U))
                        _ += 4
                    case StoreInstr.I64Store8.value:
                        offset = i.args.offset
                        length = 0
                        instrs[_] = Instruction(Call, encrypten_store_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 3
                    case StoreInstr.I64Store16.value:
                        offset = i.args.offset
                        length = 1
                        instrs[_] = Instruction(Call, encrypten_store_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 3
                    case StoreInstr.I64Store32.value:
                        offset = i.args.offset
                        length = 2
                        instrs[_] = Instruction(Call, encrypten_store_funcid)
                        instrs.insert(_, Instruction(I32Const, length))
                        instrs.insert(_, Instruction(I32Const, offset))
                        _ += 3
                    case _:
                        _ += 1
