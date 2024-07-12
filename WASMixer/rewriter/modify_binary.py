import os
import struct

from BREWasm.parser.module import SecDataCountID
from leb128 import LEB128U, LEB128S
from shutil import copyfile
from WASMixer.parser import reader
from WASMixer.parser.instruction import Instruction
from WASMixer.parser.module import *
from WASMixer.parser.opcodes import *
from WASMixer.parser.types import val_type_to_str, GlobalType


class ModifyBinary:

    def __init__(self, path: str, module=None):
        if module is None:
            module, err = reader.decode_file(path)
            if err is not None:
                print(err.args)
                print("=================================")
                raise Exception("Failed to read the wasm file!  " + err.args)

            self.module = module
            self.module.path = path

            self.func_name = []
            for custom in self.module.custom_secs:
                if custom.name == "name":
                    if custom.name_data.funcNameSubSec is not None:

                        for func_name_item in custom.name_data.funcNameSubSec[self.get_import_func_num():]:
                            self.func_name.append(func_name_item.name)
        else:
            self.module = module
            self.module.path = path

    def emit_binary(self, path):
        file_path = self.module.path

        if os.path.isfile(path):
            if not os.path.samefile(self.module.path, path):
                os.remove(path)

        file_path = path
        with open(path, "wb+") as f:
            magic_version_number = struct.pack("II", self.module.magic, self.module.version)
            f.write(magic_version_number)
            f.close()

        self.modify_custom_name_section(self.module.custom_secs, file_path)
        self.modify_type_section(self.module.type_sec, file_path)
        self.modify_import_section(self.module.import_sec, file_path)
        self.modify_func_section(self.module.func_sec, file_path)
        self.modify_table_section(self.module.table_sec, file_path)
        self.modify_memory_section(self.module.mem_sec, file_path)
        self.modify_global_section(self.module.global_sec, file_path)
        self.modify_export_section(self.module.export_sec, file_path)
        self.modify_start_section(self.module.start_sec, file_path)
        self.modify_elem_section(self.module.elem_sec, file_path)
        self.modify_code_section(self.module.code_sec, file_path)
        self.modify_data_section(self.module.data_sec, file_path)



    def get_import_func_list(self):
        import_func_list = []
        for import_item in self.module.import_sec:
            if import_item.desc.func_type is not None:
                import_func_list.append(import_item)

        return import_func_list

    def get_import_func_num(self):

        num = 0
        for _, import_item in enumerate(self.module.import_sec):
            if import_item.desc.func_type != None:
                num += 1

        return num

    def dump_functions(self, func_id=None):

        if func_id is not None:
            self.print_function(func_id)
            return

        for code_idx in range(len(self.module.code_sec)):
            self.print_function(code_idx)

    def print_function(self, func_id):

        type_id = self.module.func_sec[func_id]
        if len(self.func_name) == 0:
            print("(func %d (type %d) " % (func_id, type_id), end="")
        else:

            print("(func %s (type %d) " % (self.func_name[func_id], type_id), end="")
        param_types_str = ""
        result_types_str = ""
        print("=======" + str(type_id))
        if self.module.type_sec[type_id].param_types:
            for i in self.module.type_sec[type_id].param_types:
                param_types_str += (val_type_to_str(i) + " ")
        if self.module.type_sec[type_id].result_types:
            for i in self.module.type_sec[type_id].result_types:
                result_types_str += (val_type_to_str(i) + " ")

        print("(param %s)" % param_types_str, end="")
        print("(result %s)" % result_types_str)

        if self.module.code_sec[func_id].locals is not None:
            print("(locals", end=" ")
            for local in self.module.code_sec[func_id].locals:
                print((val_type_to_str(local.type) + " ") * local.n, end="")
            print(")")
        self.dump_expr("    ", self.module.code_sec[func_id].expr)
        print(")")

    def add_import(self, import_func_item, import_func_type):

        for i, import_item in enumerate(self.module.import_sec):
            if import_item.module == import_func_item.module and import_item.name == import_func_item.name:
                return i

        functype_id = self.add_functype_for_import(import_func_type)

        import_func_item.desc.func_type = functype_id

        self.module.import_sec.append(import_func_item)

        import_func_id = len(self.module.import_sec) - 1

        for _, code in enumerate(self.module.code_sec):
            self.fix_instruction_from_expr(code.expr, import_func_id, functype_id, False)

        self.fix_elem_section(import_func_id)

        self.fix_export_section_for_import(import_func_id)

        self.modify_type_section(self.module.type_sec)

        self.modify_import_section(self.module.import_sec)

        return import_func_id

    def add_function(self, functype, local_vec, func_instrs, obfuscated_func_id=None):

        is_new_functype = False
        functype_id = get_functype_idx(self.module, functype)
        if functype_id is None:
            is_new_functype = True
            functype_id = self.add_functype(functype)
        if obfuscated_func_id is not None:

            func_id = self.add_func_sec_type(functype_id, is_new_functype, obfuscated_func_id)
        else:

            func_id = self.add_func_sec_type(functype_id, is_new_functype)
        return self.insert_function(functype_id, func_id, local_vec, func_instrs, is_new_functype)

    def insert_function(self, type_id, func_id, local_vec, func_instrs, is_new_functype):

        insert_code = Code(local_vec, func_instrs)
        import_func_num = self.get_import_func_num()

        for _, code in enumerate(self.module.code_sec):
            self.fix_instruction_from_expr(code.expr, func_id + import_func_num, type_id, is_new_functype)

        self.fix_elem_section(func_id + import_func_num)

        self.module.code_sec.insert(func_id, insert_code)

        self.modify_code_section(self.module.code_sec)
        return (func_id + import_func_num)

    def add_functype(self, functype):

        functype_len = len(self.module.type_sec)

        insert_index = len(self.module.type_sec)
        self.module.type_sec.append(functype)

        self.modify_type_section(self.module.type_sec)
        return insert_index

    def append_global_variable(self, valtype, value):
        global_type = GlobalType(mut=1, val_type=valtype)
        global_variable = Global(global_type=global_type, init=[Instruction(I64Const, value)])
        self.module.global_sec.append(global_variable)

        import_global_variable_num = 0
        for import_item in self.module.import_sec:
            if import_item.desc.global_type is not None:
                import_global_variable_num += 1

        return import_global_variable_num + len(self.module.global_sec) - 1

    def add_functype_for_import(self, functype):

        for _, bt in enumerate(self.module.type_sec):
            if functype == bt:
                return _

        self.module.type_sec.append(functype)
        return len(self.module.type_sec) - 1

    def add_func_sec_type(self, func_sec_type, is_new_funcType, obfuscated_func_id=None):

        func_count = len(self.module.func_sec)

        func_id = func_count

        if is_new_funcType is True:
            self.fix_func_section(func_sec_type)

        self.fix_export_section(func_id)
        if func_id == func_count:
            self.module.func_sec.append(func_sec_type)
        else:
            self.module.func_sec.insert(func_id, func_sec_type)

        self.modify_func_section(self.module.func_sec)

        return func_id

    def fix_export_section(self, func_id):

        for export_item in self.module.export_sec:
            if export_item.desc.tag == 0 and export_item.desc.idx >= (func_id + self.get_import_func_num()):
                export_item.desc.idx += 1

        self.modify_export_section(self.module.export_sec)

    def fix_export_section_for_import(self, func_id):

        for export_item in self.module.export_sec:
            if export_item.desc.tag == 0 and export_item.desc.idx >= func_id:
                export_item.desc.idx += 1

        self.modify_export_section(self.module.export_sec)

    def add_new_local_to_func(self, func_id, local_type):
        self.module.code_sec[func_id].locals.append(Locals(1, local_type))

        locals_num = 0
        for item in self.module.code_sec[func_id].locals:
            locals_num += item.n

        return len(self.module.type_sec[self.module.func_sec[func_id]].param_types) + locals_num - 1

    def dump_expr(self, indentation, expr):

        for _, instr in enumerate(expr):
            if instr.opcode in [Block, Loop]:
                args = instr.args
                bt = self.module.get_block_type(args.bt)
                print("%s%s %s" % (indentation, instr.get_opname(), bt))
                self.dump_expr(indentation + "  ", args.instrs)
                print("%s%s" % (indentation, "end"))
            elif instr.opcode == If:
                args = instr.args
                bt = self.module.get_block_type(args.bt)
                print("%s%s %s" % (indentation, "if", bt))
                self.dump_expr(indentation + "  ", args.instrs1)
                print("%s%s" % (indentation, "else"))
                self.dump_expr(indentation + "  ", args.instrs2)
                print("%s%s" % (indentation, "end"))
            else:
                if instr.args is not None:
                    if 0x36 <= instr.opcode <= 0x3E or 0x28 <= instr.opcode <= 0x35:
                        print("{}{} align={} offset={} ".format(indentation, instr.get_opname(), instr.args.align,
                                                                instr.args.offset))
                    else:
                        print("{}{} {}".format(indentation, instr.get_opname(), instr.args))
                elif instr.args is None:
                    print("{}{}".format(indentation, instr.get_opname()))

    def get_instruction(self, func_id, instr_idx):

        instr, expr = self.get_instruction_from_expr(self.module.code_sec[func_id].expr, instr_idx + 1)
        return instr

    def insert_instructions(self, func_id, instr_idx, instr):

        if type(instr) is not list:
            target_instr, expr = self.get_instruction_from_expr(self.module.code_sec[func_id].expr, instr_idx + 1)
            instr_position = expr.index(target_instr)
            expr.insert(instr_position, instr)
        elif type(instr) is list:
            if instr_idx >= len(self.module.code_sec[func_id].expr):
                return
            target_instr, expr = self.get_instruction_from_expr(self.module.code_sec[func_id].expr, instr_idx + 1)
            instr_position = expr.index(target_instr)
            for i in instr:
                expr.insert(instr_position, i)
                instr_position += 1

    def get_instruction_from_expr(self, expr, instr_idx, current_instr_idx=0):

        for _, instr in enumerate(expr):
            current_instr_idx += 1
            if instr.opcode in [Block, Loop]:
                if instr_idx == current_instr_idx:
                    raise Exception("block can not be changed")
                args = instr.args
                return self.get_instruction_from_expr(args.instrs, instr_idx, current_instr_idx=current_instr_idx)

                current_instr_idx += 1
                if instr_idx == current_instr_idx:
                    raise Exception("end can not be changed")
            elif instr.opcode == If:
                if instr_idx == current_instr_idx:
                    raise Exception("if can not be changed")
                args = instr.args
                return self.get_instruction_from_expr(args.instrs1, instr_idx, current_instr_idx=current_instr_idx)

                current_instr_idx += 1
                if instr_idx == current_instr_idx:
                    raise Exception("else can not be changed")
                return self.get_instruction_from_expr(args.instrs2, instr_idx, current_instr_idx=current_instr_idx)

                current_instr_idx += 1
                if instr_idx == current_instr_idx:
                    raise Exception("end can not be changed")
            else:
                if current_instr_idx == instr_idx:
                    return instr, expr

    def fix_func_section(self, func_sec_type):

        for _, func_type in enumerate(self.module.func_sec):
            if func_type >= func_sec_type:
                self.module.func_sec[_] += 1

    def fix_elem_section(self, func_id):

        for elem in self.module.elem_sec:
            for _, func_idx in enumerate(elem.init):
                if func_idx >= func_id:
                    elem.init[_] += 1
        self.modify_elem_section(self.module.elem_sec)

    def fix_instruction_from_expr(self, expr, func_id, type_id, is_new_functype):

        for _, instr in enumerate(expr):
            if instr.opcode in [Block, Loop]:
                args = instr.args
                self.fix_instruction_from_expr(args.instrs, func_id, type_id, is_new_functype)
            elif instr.opcode == If:
                args = instr.args
                self.fix_instruction_from_expr(args.instrs1, func_id, type_id, is_new_functype)
                self.fix_instruction_from_expr(args.instrs2, func_id, type_id, is_new_functype)
            else:
                if instr.args is not None:
                    if (instr.opcode == Call and instr.args >= func_id):
                        print(instr.args)
                        print(func_id)
                        instr.args += 1
                    elif instr.opcode == CallIndirect and instr.args >= type_id and is_new_functype is True:
                        print("type=======")
                        print(instr.args)
                        print(func_id)
                        instr.args += 1

    def hook_call_from_expr(self, expr, func_id, new_func_id=None):

        for _, instr in enumerate(expr):
            if instr.opcode in [Block, Loop]:
                args = instr.args
                return self.hook_call_from_expr(args.instrs, func_id, new_func_id)
            elif instr.opcode == If:
                args = instr.args
                return self.hook_call_from_expr(args.instrs1, func_id, new_func_id)
                return self.hook_call_from_expr(args.instrs2, func_id, new_func_id)
            else:
                if instr.args is not None:
                    if instr.opcode == Call and instr.args == func_id and new_func_id is not None:
                        print(instr.args)
                        print(func_id)
                        instr.args = new_func_id

    def fix_import_sec(self, type_id):

        for i in self.module.import_sec:
            if i.desc.func_type >= type_id:
                i.desc.func_type += 1
        self.modify_import_section(self.module.import_sec)

    def fix_section_range(self, sec_id, change, start, custom_sec_id=None):

        if sec_id != SecCustomID:
            for i in range(sec_id + 1, 12):
                if self.module.section_range[i].start != self.module.section_range[i].end:
                    self.module.section_range[i].start += change
                    self.module.section_range[i].end += change

            if self.module.section_range[0] != []:
                for custom in self.module.section_range[0]:
                    if start <= custom.start:
                        custom.start += change
                        custom.end += change
        elif sec_id == SecCustomID:
            for i in range(1, 12):
                if self.module.section_range[i].start != self.module.section_range[i].end and start <= \
                        self.module.section_range[i].start:
                    self.module.section_range[i].start += change
                    self.module.section_range[i].end += change
            for _, custom in enumerate(self.module.section_range[0]):
                if _ != custom_sec_id and start <= custom.start:
                    custom.start += change
                    custom.end += change

    def modify_custom_name_section(self, custom_vec: list, file_path=None):
        if file_path == None:
            file_path = self.module.path

        for _, custom in enumerate(custom_vec):
            if custom.name == "name":
                name_section_bytes = bytes()
                name_section_bytes += LEB128U.encode(len(custom.name))
                name_section_bytes += bytes(custom.name, encoding="utf-8")
                if custom.name_data.moduleNameSubSec != None:
                    name_section_bytes += bytes([0x00])
                    name_section_bytes += LEB128U.encode(len(custom.name_data.moduleNameSubSec))
                    name_section_bytes += custom.name_data.moduleNameSubSec
                if custom.name_data.funcNameSubSec != []:

                    funcname_bytes = bytes()
                    funcname_bytes += LEB128U.encode(len(custom.name_data.funcNameSubSec))
                    for funcname in custom.name_data.funcNameSubSec:
                        funcname_bytes += LEB128U.encode(funcname.idx)
                        funcname_bytes += LEB128U.encode(len(funcname.name))
                        funcname_bytes += bytes(funcname.name, encoding="utf-8")
                    name_section_bytes += (bytes([0x01]) + LEB128U.encode(len(funcname_bytes))) + funcname_bytes

                if custom.name_data.localNameSubSec != None:
                    name_section_bytes += bytes([0x02])
                    name_section_bytes += LEB128U.encode(len(custom.name_data.localNameSubSec))
                    name_section_bytes += custom.name_data.localNameSubSec
                if custom.name_data.labelsNameSubSec != None:
                    name_section_bytes += bytes([0x03])
                    name_section_bytes += LEB128U.encode(len(custom.name_data.labelsNameSubSec))
                    name_section_bytes += custom.name_data.labelsNameSubSec
                if custom.name_data.typeNameSubSec != None:
                    name_section_bytes += bytes([0x04])
                    name_section_bytes += LEB128U.encode(len(custom.name_data.typeNameSubSec))
                    name_section_bytes += custom.name_data.typeNameSubSec
                if custom.name_data.tableNameSubSec != []:
                    tablename_bytes = bytes()
                    tablename_bytes += LEB128U.encode(len(custom.name_data.tableNameSubSec))
                    for tablename in custom.name_data.tableNameSubSec:
                        tablename_bytes += LEB128U.encode(tablename.idx)
                        tablename_bytes += LEB128U.encode(len(tablename.name))
                        tablename_bytes += bytes(tablename.name, encoding="utf-8")
                    name_section_bytes += (bytes([0x05]) + LEB128U.encode(len(tablename_bytes))) + tablename_bytes
                if custom.name_data.memoryNameSubSec != None:
                    name_section_bytes += bytes([0x06])
                    name_section_bytes += LEB128U.encode(len(custom.name_data.memoryNameSubSec))
                    name_section_bytes += custom.name_data.memoryNameSubSec
                if custom.name_data.globalNameSubSec != []:
                    globalname_bytes = bytes()
                    globalname_bytes += LEB128U.encode(len(custom.name_data.globalNameSubSec))
                    for globalname in custom.name_data.globalNameSubSec:
                        globalname_bytes += LEB128U.encode(globalname.idx)
                        globalname_bytes += LEB128U.encode(len(globalname.name))
                        globalname_bytes += bytes(globalname.name, encoding="utf-8")
                    name_section_bytes += (bytes([0x07]) + LEB128U.encode(len(globalname_bytes))) + globalname_bytes
                if custom.name_data.elemNameSubSec != None:
                    name_section_bytes += bytes([0x08])
                    name_section_bytes += LEB128U.encode(len(custom.name_data.elemNameSubSec))
                    name_section_bytes += custom.name_data.elemNameSubSec
                if custom.name_data.dataNameSubSec != []:
                    dataname_bytes = bytes()
                    dataname_bytes += LEB128U.encode(len(custom.name_data.dataNameSubSec))
                    for dataname in custom.name_data.dataNameSubSec:
                        dataname_bytes += LEB128U.encode(dataname.idx)
                        dataname_bytes += LEB128U.encode(len(dataname.name))
                        dataname_bytes += bytes(dataname.name, encoding="utf-8")
                    name_section_bytes += (bytes([0x09]) + LEB128U.encode(len(dataname_bytes))) + dataname_bytes

                if os.path.isfile(file_path):
                    f = open(file_path, "r+b")
                else:
                    f = open(file_path, "w+b")
                file_bytes = f.read()
                custom = self.module.section_range[SecCustomID][_]
                start = custom.start
                end = custom.end
                name_section_bytes = bytes([0x00]) + LEB128U.encode(len(name_section_bytes)) + name_section_bytes
                file_new_bytes = file_bytes[:start] + name_section_bytes + file_bytes[end:]
                change = len(name_section_bytes) - (end - start)

                custom.end = custom.start + len(name_section_bytes)
                self.fix_section_range(SecCustomID, change, custom.start, _)
                f.seek(0)
                f.truncate()
                f.write(file_new_bytes)
                f.close()
            else:
                custom_section_bytes = bytes()
                custom_section_bytes += LEB128U.encode(len(custom.name))
                custom_section_bytes += bytes(custom.name, encoding="utf-8")
                custom_section_bytes += custom.custom_sec_data

                if os.path.isfile(file_path):
                    f = open(file_path, "r+b")
                else:
                    f = open(file_path, "w+b")
                file_bytes = f.read()
                custom = self.module.section_range[SecCustomID][_]
                start = custom.start
                end = custom.end
                custom_section_bytes = bytes([0x00]) + LEB128U.encode(
                    len(custom_section_bytes)) + custom_section_bytes
                file_new_bytes = file_bytes[:start] + custom_section_bytes + file_bytes[end:]
                change = len(custom_section_bytes) - (end - start)

                custom.end = custom.start + len(custom_section_bytes)
                self.fix_section_range(SecCustomID, change, custom.start, _)
                f.seek(0)
                f.truncate()
                f.write(file_new_bytes)
                f.close()
        return None

    def modify_import_section(self, import_vec: list, file_path=None):
        if file_path == None:
            file_path = self.module.path

        import_vec_len = len(import_vec)
        import_vec_len_bytes = LEB128U.encode(import_vec_len)
        import_vec_bytes = bytes()
        import_vec_bytes += import_vec_len_bytes
        if import_vec == []:
            return
        for i in import_vec:
            import_vec_bytes += LEB128U.encode(len(i.module))
            import_vec_bytes += bytes(i.module, encoding="utf-8")
            import_vec_bytes += LEB128U.encode(len(i.name))
            import_vec_bytes += bytes(i.name, encoding="utf-8")
            import_vec_bytes += LEB128U.encode(i.desc.tag)
            if i.desc.func_type is not None:
                import_vec_bytes += LEB128U.encode(i.desc.func_type)
            elif i.desc.table is not None:
                import_vec_bytes += self.write_table_type(i.desc.table)
            elif i.desc.mem is not None:
                import_vec_bytes += self.write_limits(i.desc.mem)
            elif i.desc.global_type is not None:
                import_vec_bytes += self.write_global_type(i.desc.global_type)
        import_section_bytes = bytes([0x02]) + LEB128U.encode(len(import_vec_bytes)) + import_vec_bytes

        if os.path.isfile(file_path):
            f = open(file_path, "r+b")
        else:
            f = open(file_path, "w+b")
        file_bytes = f.read()
        file_new_bytes = file_bytes[
                         :self.module.section_range[SecImportID].start] + import_section_bytes + file_bytes[
                                                                                                 self.module.section_range[
                                                                                                     SecImportID].end:]
        change = len(import_section_bytes) - (
                self.module.section_range[SecImportID].end - self.module.section_range[SecImportID].start)

        self.module.section_range[SecImportID].end = self.module.section_range[SecImportID].start + len(
            import_section_bytes)
        self.fix_section_range(SecImportID, change, self.module.section_range[SecImportID].start)
        f.seek(0)
        f.truncate()
        f.write(file_new_bytes)

        f.close()
        return import_section_bytes

    def modify_export_section(self, export_vec: list, file_path=None):
        if file_path == None:
            file_path = self.module.path

        export_vec_len = len(export_vec)
        export_vec_len_bytes = LEB128U.encode(export_vec_len)
        export_vec_bytes = bytes()
        export_vec_bytes += export_vec_len_bytes
        if export_vec == []:
            return
        for export_item in export_vec:
            export_vec_bytes += LEB128U.encode(len(export_item.name))
            export_vec_bytes += bytes(export_item.name, encoding="utf-8")
            export_vec_bytes += LEB128U.encode(export_item.desc.tag)
            export_vec_bytes += LEB128U.encode(export_item.desc.idx)

        export_section_bytes = bytes([0x07]) + LEB128U.encode(len(export_vec_bytes)) + export_vec_bytes

        if os.path.isfile(file_path):
            f = open(file_path, "r+b")
        else:
            f = open(file_path, "w+b")
        file_bytes = f.read()
        file_new_bytes = file_bytes[
                         :self.module.section_range[SecExportID].start] + export_section_bytes + file_bytes[
                                                                                                 self.module.section_range[
                                                                                                     SecExportID].end:]
        change = len(export_section_bytes) - (
                self.module.section_range[SecExportID].end - self.module.section_range[SecExportID].start)

        self.module.section_range[SecExportID].end = self.module.section_range[SecExportID].start + len(
            export_section_bytes)
        self.fix_section_range(SecExportID, change, self.module.section_range[SecExportID].start)
        f.seek(0)
        f.truncate()
        f.write(file_new_bytes)
        f.close()
        return export_section_bytes

    def modify_start_section(self, start_funcid: list, file_path=None):
        if file_path == None:
            file_path = self.module.path

        if start_funcid != None:
            start_funcid_bytes = LEB128U.encode(start_funcid)
            start_section_bytes = bytes([0x08]) + LEB128U.encode(len(start_funcid_bytes)) + start_funcid_bytes

            if os.path.isfile(file_path):
                f = open(file_path, "r+b")
            else:
                f = open(file_path, "w+b")
            file_bytes = f.read()
            file_new_bytes = file_bytes[
                             :self.module.section_range[SecStartID].start] + start_section_bytes + file_bytes[
                                                                                                     self.module.section_range[
                                                                                                         SecStartID].end:]
            change = len(start_section_bytes) - (
                    self.module.section_range[SecStartID].end - self.module.section_range[SecStartID].start)

            self.module.section_range[SecStartID].end = self.module.section_range[SecStartID].start + len(
                start_section_bytes)
            self.fix_section_range(SecStartID, change, self.module.section_range[SecStartID].start)
            f.seek(0)
            f.truncate()
            f.write(file_new_bytes)
            f.close()
            return start_section_bytes

    def modify_memory_section(self, memory_vec: list, file_path=None):
        if file_path == None:
            file_path = self.module.path

        memory_vec_len = len(memory_vec)
        memory_vec_len_bytes = LEB128U.encode(memory_vec_len)
        memory_vec_bytes = bytes()
        memory_vec_bytes += memory_vec_len_bytes
        if memory_vec == []:
            return
        for memory_item in memory_vec:
            memory_item_bytes = bytes()
            memory_item_bytes += bytes([memory_item.tag])
            memory_item_bytes += LEB128U.encode(memory_item.min)
            if memory_item.max != 0:
                memory_item_bytes += LEB128U.encode(memory_item.max)
            memory_vec_bytes += memory_item_bytes

        memroy_section_bytes = bytes([SecMemID]) + LEB128U.encode(len(memory_vec_bytes)) + memory_vec_bytes

        if os.path.isfile(file_path):
            f = open(file_path, "r+b")
        else:
            f = open(file_path, "w+b")
        file_bytes = f.read()
        file_new_bytes = file_bytes[
                         :self.module.section_range[SecMemID].start] + memroy_section_bytes + file_bytes[
                                                                                              self.module.section_range[
                                                                                                  SecMemID].end:]
        change = len(memroy_section_bytes) - (
                self.module.section_range[SecMemID].end - self.module.section_range[SecMemID].start)

        self.module.section_range[SecMemID].end = self.module.section_range[SecMemID].start + len(
            memroy_section_bytes)
        self.fix_section_range(SecMemID, change, self.module.section_range[SecMemID].start)
        f.seek(0)
        f.truncate()
        f.write(file_new_bytes)
        f.close()
        return memroy_section_bytes

    def modify_data_section(self, data_vec: list, file_path=None):
        if file_path == None:
            file_path = self.module.path

        data_vec_len = len(data_vec)
        data_vec_len_bytes = LEB128U.encode(data_vec_len)
        data_vec_bytes = bytes()
        data_vec_bytes += data_vec_len_bytes
        if not data_vec:
            return
        for data_item in data_vec:
            data_item_bytes = bytes()
            data_item_bytes += LEB128U.encode(data_item.mem)
            data_item_bytes += self.write_expr(data_item.offset)
            data_item_bytes += LEB128U.encode(len(data_item.init))
            data_item_bytes += data_item.init

            data_vec_bytes += data_item_bytes

        data_section_bytes = bytes([SecDataID]) + LEB128U.encode(len(data_vec_bytes)) + data_vec_bytes

        if os.path.isfile(file_path):
            f = open(file_path, "r+b")
        else:
            f = open(file_path, "w+b")
        file_bytes = f.read()
        file_new_bytes = file_bytes[
                         :self.module.section_range[SecDataID].start] + data_section_bytes + file_bytes[
                                                                                             self.module.section_range[
                                                                                                 SecDataID].end:]
        change = len(data_section_bytes) - (
                self.module.section_range[SecDataID].end - self.module.section_range[SecDataID].start)

        self.module.section_range[SecDataID].end = self.module.section_range[SecDataID].start + len(
            data_section_bytes)
        self.fix_section_range(SecDataID, change, self.module.section_range[SecDataID].start)
        f.seek(0)
        f.truncate()
        f.write(file_new_bytes)
        f.close()
        return data_section_bytes

    def modify_datacount_section(self, datacount: int, file_path=None):
        if file_path == None:
            file_path = self.module.path

        if datacount != None:
            datacount_bytes = LEB128U.encode(datacount)
            datacount_section_bytes = bytes([SecDataCountID]) + LEB128U.encode(len(datacount_bytes)) + datacount_bytes

            if os.path.isfile(file_path):
                f = open(file_path, "r+b")
            else:
                f = open(file_path, "w+b")
            file_bytes = f.read()
            file_new_bytes = file_bytes[
                             :self.module.section_range[SecDataCountID].start] + datacount_section_bytes + file_bytes[
                                                                                                     self.module.section_range[
                                                                                                         SecDataCountID].end:]
            change = len(datacount_section_bytes) - (
                    self.module.section_range[SecDataCountID].end - self.module.section_range[SecDataCountID].start)

            self.module.section_range[SecDataCountID].end = self.module.section_range[SecDataCountID].start + len(
                datacount_section_bytes)
            self.fix_section_range(SecDataCountID, change, self.module.section_range[SecDataCountID].start)
            f.seek(0)
            f.truncate()
            f.write(file_new_bytes)
            f.close()
            return datacount_section_bytes

    def modify_elem_section(self, elem_vec: list, file_path=None):
        if file_path == None:
            file_path = self.module.path

        elem_vec_len = len(elem_vec)
        elem_vec_len_bytes = LEB128U.encode(elem_vec_len)
        elem_vec_bytes = bytes()
        elem_vec_bytes += elem_vec_len_bytes
        if elem_vec == []:
            return
        for elem in elem_vec:
            elem_vec_bytes += LEB128U.encode(elem.table)
            elem_vec_bytes += self.write_expr(elem.offset)
            elem_vec_bytes += LEB128U.encode(len(elem.init))
            for func_idx in elem.init:
                elem_vec_bytes += LEB128U.encode(func_idx)
        elem_section_bytes = bytes([SecElemID]) + LEB128U.encode(len(elem_vec_bytes)) + elem_vec_bytes

        if os.path.isfile(file_path):
            f = open(file_path, "r+b")
        else:
            f = open(file_path, "w+b")
        file_bytes = f.read()
        binary_start = self.module.section_range[SecElemID].start
        binary_end = self.module.section_range[SecElemID].end
        if binary_start == binary_end:
            for i in reversed(range(SecElemID)):
                if self.module.section_range[i].start != self.module.section_range[i].end:
                    file_new_bytes = file_bytes[
                                     :self.module.section_range[i].end] + elem_section_bytes + file_bytes[
                                                                                               self.module.section_range[
                                                                                                   i].end:]
                    change = len(elem_section_bytes) - (
                            self.module.section_range[SecElemID].end - self.module.section_range[SecElemID].start)
                    self.module.section_range[SecElemID].start = self.module.section_range[i].end
                    self.module.section_range[SecElemID].end = self.module.section_range[i].end + len(
                        elem_section_bytes)
                    self.fix_section_range(SecElemID, change, self.module.section_range[SecElemID].start)
                    f.seek(0)
                    f.truncate()
                    f.write(file_new_bytes)
                    break
        else:
            file_new_bytes = file_bytes[
                             :self.module.section_range[SecElemID].start] + elem_section_bytes + file_bytes[
                                                                                                 self.module.section_range[
                                                                                                     SecElemID].end:]
            change = len(elem_section_bytes) - (
                    self.module.section_range[SecElemID].end - self.module.section_range[SecElemID].start)

            self.module.section_range[SecElemID].end = self.module.section_range[SecElemID].start + len(
                elem_section_bytes)
            self.fix_section_range(SecElemID, change, self.module.section_range[SecElemID].start)
            f.seek(0)
            f.truncate()
            f.write(file_new_bytes)
        f.close()
        return elem_section_bytes

    def modify_type_section(self, functype_vec: list, file_path=None):
        if file_path == None:
            file_path = self.module.path

        functype_vec_len = len(functype_vec)
        functype_vec_len_bytes = LEB128U.encode(functype_vec_len)
        functype_vec_bytes = bytes()
        functype_vec_bytes += functype_vec_len_bytes
        if functype_vec == []:
            return
        for functype in functype_vec:
            functype_bytes = bytes()
            functype_bytes += bytes([0x60])
            functype_bytes += self.write_val_types(functype.param_types)
            functype_bytes += self.write_val_types(functype.result_types)
            functype_vec_bytes += functype_bytes
        type_section_bytes = bytes([0x01]) + LEB128U.encode(len(functype_vec_bytes)) + functype_vec_bytes

        if os.path.isfile(file_path):
            f = open(file_path, "r+b")
        else:
            f = open(file_path, "w+b")


        file_bytes = f.read()
        file_new_bytes = file_bytes[:self.module.section_range[SecTypeID].start] + type_section_bytes + file_bytes[
                                                                                                        self.module.section_range[
                                                                                                            SecTypeID].end:]
        change = len(type_section_bytes) - (
                self.module.section_range[SecTypeID].end - self.module.section_range[SecTypeID].start)

        self.module.section_range[SecTypeID].end = self.module.section_range[SecTypeID].start + len(
            type_section_bytes)
        self.fix_section_range(SecTypeID, change, self.module.section_range[SecTypeID].start)
        f.seek(0)
        f.truncate()
        f.write(file_new_bytes)
        f.close()
        return type_section_bytes

    def modify_global_section(self, global_vec: list, file_path=None):
        if file_path == None:
            file_path = self.module.path

        global_vec_len = len(global_vec)
        global_vec_len_bytes = LEB128U.encode(global_vec_len)
        global_vec_bytes = bytes()
        global_vec_bytes += global_vec_len_bytes
        if global_vec == []:
            return
        for global_item in global_vec:
            global_bytes = bytes()
            global_bytes += self.write_global(global_item)
            global_vec_bytes += global_bytes

        global_section_bytes = bytes([0x06]) + LEB128U.encode(len(global_vec_bytes)) + global_vec_bytes

        if os.path.isfile(file_path):
            f = open(file_path, "r+b")
        else:
            f = open(file_path, "w+b")
        file_bytes = f.read()
        if self.module.section_range[SecGlobalID].start == 0:
            for section in range(1, SecGlobalID):
                if self.module.section_range[section].start != 0:
                    self.module.section_range[SecGlobalID].start = self.module.section_range[section].end
                    self.module.section_range[SecGlobalID].end = self.module.section_range[SecGlobalID].start
        file_new_bytes = file_bytes[
                         :self.module.section_range[SecGlobalID].start] + global_section_bytes + file_bytes[
                                                                                                 self.module.section_range[
                                                                                                     SecGlobalID].end:]
        change = len(global_section_bytes) - (
                self.module.section_range[SecGlobalID].end - self.module.section_range[SecGlobalID].start)

        self.module.section_range[SecGlobalID].end = self.module.section_range[SecGlobalID].start + len(
            global_section_bytes)
        self.fix_section_range(SecGlobalID, change, self.module.section_range[SecGlobalID].start)
        f.seek(0)
        f.truncate()
        f.write(file_new_bytes)
        f.close()
        return global_section_bytes

    def modify_func_section(self, type_vec, file_path=None):
        if file_path == None:
            file_path = self.module.path

        type_vec_len = len(type_vec)
        type_vec_len_bytes = LEB128U.encode(type_vec_len)
        type_vec_bytes = bytes()
        type_vec_bytes += type_vec_len_bytes
        if type_vec == []:
            return
        for type_item in type_vec:
            type_vec_bytes += LEB128U.encode(type_item)

        func_section_bytes = bytes([0x03]) + LEB128U.encode(len(type_vec_bytes)) + type_vec_bytes
        if os.path.isfile(file_path):
            f = open(file_path, "r+b")
        else:
            f = open(file_path, "w+b")
        file_bytes = f.read()
        file_new_bytes = file_bytes[:self.module.section_range[SecFuncID].start] + func_section_bytes + file_bytes[
                                                                                                        self.module.section_range[
                                                                                                            SecFuncID].end:]
        change = len(func_section_bytes) - (
                self.module.section_range[SecFuncID].end - self.module.section_range[SecFuncID].start)

        self.module.section_range[SecFuncID].end = self.module.section_range[SecFuncID].start + len(
            func_section_bytes)
        self.fix_section_range(SecFuncID, change, self.module.section_range[SecFuncID].start)
        f.seek(0)
        f.truncate()
        f.write(file_new_bytes)
        f.close()
        return func_section_bytes

    def modify_code_section(self, code_vec: list, file_path=None):
        if file_path == None:
            file_path = self.module.path

        code_vec_len = len(code_vec)
        code_vec_len_bytes = LEB128U.encode(code_vec_len)
        code_vec_bytes = bytes()
        code_vec_bytes += code_vec_len_bytes
        if code_vec == []:
            return
        for code in code_vec:
            code_bytes = bytes()
            locals_vec_len = len(code.locals)
            locals_vec_len_bytes = LEB128U.encode(locals_vec_len)
            locals_vec_bytes = bytes()
            expr_bytes = bytes()

            for local in code.locals:
                local_count = local.n
                local_type = local.type
                locals_vec_bytes += LEB128U.encode(local_count)
                locals_vec_bytes += bytes([local_type])

            expr_bytes += self.write_expr(code.expr)
            code_bytes += (locals_vec_len_bytes + locals_vec_bytes + expr_bytes)
            code_vec_bytes += LEB128U.encode(len(code_bytes)) + code_bytes
        code_section_bytes = bytes([0x0A]) + LEB128U.encode(len(code_vec_bytes)) + code_vec_bytes

        if os.path.isfile(file_path):
            f = open(file_path, "r+b")
        else:
            f = open(file_path, "w+b")
        file_bytes = f.read()
        file_new_bytes = file_bytes[:self.module.section_range[SecCodeID].start] + code_section_bytes + file_bytes[
                                                                                                        self.module.section_range[
                                                                                                            SecCodeID].end:]
        change = len(code_section_bytes) - (
                self.module.section_range[SecCodeID].end - self.module.section_range[SecCodeID].start)

        self.module.section_range[SecCodeID].end = self.module.section_range[SecCodeID].start + len(
            code_section_bytes)
        self.fix_section_range(SecCodeID, change, self.module.section_range[SecCodeID].start)
        f.seek(0)
        f.truncate()
        f.write(file_new_bytes)
        f.close()
        return code_section_bytes

    def modify_table_section(self, table_vec: list, file_path=None):
        if file_path == None:
            file_path = self.module.path

        table_vec_len = len(table_vec)
        table_vec_len_bytes = LEB128U.encode(table_vec_len)
        table_vec_bytes = bytes()
        table_vec_bytes += table_vec_len_bytes
        if table_vec == []:
            return
        for table_type in table_vec:
            table_type_bytes = bytes()
            table_type_bytes += bytes([table_type.elem_type])
            table_type_bytes += bytes([table_type.limits.tag])
            table_type_bytes += LEB128U.encode(table_type.limits.min)
            if 0 != table_type.limits.max:
                table_type_bytes += LEB128U.encode(table_type.limits.max)
            table_vec_bytes += table_type_bytes

        table_section_bytes = bytes([0x04]) + LEB128U.encode(len(table_vec_bytes)) + table_vec_bytes

        if os.path.isfile(file_path):
            f = open(file_path, "r+b")
        else:
            f = open(file_path, "w+b")
        file_bytes = f.read()
        binary_start = self.module.section_range[SecTableID].start
        binary_end = self.module.section_range[SecTableID].end
        if binary_start == binary_end:
            for i in reversed(range(SecTableID)):
                if self.module.section_range[i].start != self.module.section_range[i].end:
                    file_new_bytes = file_bytes[
                                     :self.module.section_range[i].end] + table_section_bytes + file_bytes[
                                                                                                self.module.section_range[
                                                                                                    i].end:]
                    change = len(table_section_bytes) - (
                            self.module.section_range[SecTableID].end - self.module.section_range[
                        SecTableID].start)
                    self.module.section_range[SecTableID].start = self.module.section_range[i].end
                    self.module.section_range[SecTableID].end = self.module.section_range[i].end + len(
                        table_section_bytes)
                    self.fix_section_range(SecTableID, change, self.module.section_range[SecTableID].start)
                    f.seek(0)
                    f.truncate()
                    f.write(file_new_bytes)
                    break
        else:
            file_new_bytes = file_bytes[
                             :self.module.section_range[SecTableID].start] + table_section_bytes + file_bytes[
                                                                                                   self.module.section_range[
                                                                                                       SecTableID].end:]
            change = len(table_section_bytes) - (
                    self.module.section_range[SecTableID].end - self.module.section_range[SecTableID].start)

            self.module.section_range[SecTableID].end = self.module.section_range[SecTableID].start + len(
                table_section_bytes)
            self.fix_section_range(SecTableID, change, self.module.section_range[SecTableID].start)
            f.seek(0)
            f.truncate()
            f.write(file_new_bytes)
        f.close()

        return table_section_bytes

    def write_expr(self, expr: list):

        instructions_bytes = self.write_instructions(expr)
        expr_bytes = instructions_bytes + bytes([0x0b])

        return expr_bytes

    def write_instructions(self, expr: list):

        instructions_bytes = bytes()
        for index in range(len(expr)):
            instructions_bytes += self.write_instruction(expr[index])

        return instructions_bytes

    def write_instruction(self, instr):

        binary_data = bytes()

        if instr.opcode < 0xFC:
            binary_data += bytes([instr.opcode])


        elif instr.opcode <= 0xFD7F:
            binary_data += instr.opcode.to_bytes(2, 'big')


        elif instr.opcode <= 0xFDFF01:
            binary_data += instr.opcode.to_bytes(3, 'big')

        else:
            raise Exception("Invalid opcode: 0x%02x" % instr.opcode)

        args_bytes = self.write_args(instr)
        if args_bytes != None:
            binary_data += args_bytes

        return binary_data

    def write_args(self, instr):

        opcode = instr.opcode
        if opcode in [Block, Loop]:
            return self.write_block_args(instr)
        elif opcode == If:
            return self.write_if_args(instr)
        elif opcode in [Br, BrIf]:
            return LEB128U.encode(instr.args)
        elif opcode == BrTable:
            return self.write_br_table_args(instr)
        elif opcode == Call:
            return LEB128U.encode(instr.args)
        elif opcode == CallIndirect:
            return self.write_call_indirect_args(instr)
        elif opcode in [LocalGet, LocalSet, LocalTee]:
            return LEB128U.encode(instr.args)
        elif opcode in [GlobalGet, GlobalSet]:
            return LEB128U.encode(instr.args)
        elif opcode in [MemorySize, MemoryGrow]:
            return bytes([0x00])
        elif opcode == I32Const:
            return LEB128S.encode(instr.args)  # u32
        elif opcode == I64Const:
            return LEB128S.encode(instr.args)  # u64
        elif opcode == F32Const:
            return struct.pack('<f', instr.args)
        elif opcode == F64Const:
            return struct.pack('<d', instr.args)
        elif opcode == V128Const:
            return instr.args.to_bytes(16, 'little')  # v128
        elif opcode == I8x16Shuffle:
            return instr.args.to_bytes(16, 'little')  # v128
        elif I8x16ExtractLaneS <= opcode <= F64x2ReplaceLane:
            return bytes([instr.args])
        elif opcode in [RefNull, RefFunc]:
            return LEB128U.encode(instr.args)
        elif opcode in [MemoryInit, DataDrop, ElemDrop, TableGrow, TableSize, TableFill]:
            return LEB128U.encode(instr.args)
        elif opcode in [TableInit, TableCopy]:
            x = LEB128U.encode(instr.args.x)
            y = LEB128U.encode(instr.args.y)
            return x + y
        elif V128Load <= opcode <= V128Store or opcode in [V128Load32Zero, V128Load64Zero]:
            return self.write_mem_arg(instr)
        elif I32Load <= instr.opcode <= I64Store32:
            return self.write_mem_arg(instr)
        else:
            return None

    def write_block_args(self, instr):

        args_bytes = bytes()
        args_bytes += LEB128S.encode(instr.args.bt)
        args_bytes += self.write_instructions(instr.args.instrs)
        args_bytes += bytes([0x0b])

        return args_bytes

    def write_if_args(self, instr):

        args_bytes = bytes()
        args_bytes += LEB128S.encode(instr.args.bt)
        args_bytes += self.write_instructions(instr.args.instrs1)
        if instr.args.instrs2:
            args_bytes += bytes([0x05])
            args_bytes += self.write_instructions(instr.args.instrs2)
            args_bytes += bytes([0x0b])
        else:
            args_bytes += bytes([0x0b])

        return args_bytes

    @staticmethod
    def write_br_table_args(instr):

        args_bytes = bytes()
        args_bytes += LEB128U.encode(len(instr.args.labels))
        for label in instr.args.labels:
            args_bytes += LEB128U.encode(label)
        args_bytes += LEB128U.encode(instr.args.default)

        return args_bytes

    @staticmethod
    def write_call_indirect_args(instr):

        args_bytes = bytes()
        args_bytes += LEB128U.encode(instr.args)
        args_bytes += bytes([0x00])

        return args_bytes

    @staticmethod
    def write_mem_arg(instr):

        args_bytes = bytes()
        args_bytes += LEB128U.encode(instr.args.align)
        args_bytes += LEB128U.encode(instr.args.offset)

        return args_bytes

    @staticmethod
    def write_val_types(val_types):

        val_types_bytes = bytes()
        val_types_bytes += LEB128U.encode(len(val_types))
        for val in val_types:
            val_types_bytes += bytes([val])

        return val_types_bytes

    @staticmethod
    def write_global_type(global_type):

        global_type_bytes = bytes()
        global_type_bytes += bytes([global_type.val_type])
        global_type_bytes += bytes([global_type.mut])
        return global_type_bytes

    @staticmethod
    def write_limits(mem):

        mem_bytes = bytes()
        mem_bytes += bytes([mem.tag])
        mem_bytes += LEB128U.encode(mem.min)
        if mem.tag == 1:
            mem_bytes += LEB128U.encode(mem.max)
        return mem_bytes

    @staticmethod
    def write_table_type(table_type):

        table_type_bytes = bytes()
        table_type_bytes += bytes([table_type.elem_type])
        table_type_bytes += bytes([table_type.limits.tag])
        if table_type.limits.min != 0:
            table_type_bytes += LEB128U.encode(table_type.limits.min)
        if table_type.limits.max != 0:
            table_type_bytes += LEB128U.encode(table_type.limits.max)
        return table_type_bytes

    def write_global(self, global_item):
        global_bytes = bytes()
        global_bytes += self.write_global_type(global_item.type)
        global_bytes += self.write_expr(global_item.init)
        return global_bytes


def get_functype_idx(module, functype):
    functype_id = None
    for _, i in enumerate(module.type_sec):
        if i.equal(functype) is True:
            functype_id = _
    return functype_id
