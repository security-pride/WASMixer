import ctypes
import struct

from ..parser.instruction import Instruction, BlockArgs, IfArgs, BrTableArgs, MemArg, TableArg, MemLaneArg
from ..parser.leb128 import *
from ..parser.module import Import, ImportDesc, ImportTagFunc, ImportTagTable, ImportTagMem, ImportTagGlobal, \
    Global, Export, ExportDesc, ExportTagFunc, ExportTagTable, ExportTagMem, ExportTagGlobal, Elem, Code, Locals, \
    Data, MagicNumber, Version, Module, SecCustomID, SecDataID, CustomSec, SecTypeID, SecImportID, SecFuncID, \
    SecTableID, SecMemID, SecGlobalID, SecExportID, SecStartID, SecElemID, SecCodeID, NameData, SectionRange
from ..parser.opcodes import *
from ..parser.opnames import opnames
from ..parser.types import ValTypeI32, ValTypeI64, ValTypeF32, ValTypeF64, ValTypeV128, FuncType, FtTag, TableType, \
    FuncRef, \
    GlobalType, MutConst, MutVar, Limits, BlockTypeI32, BlockTypeI64, BlockTypeF32, BlockTypeF64, BlockTypeEmpty, \
    NameAssoc, BlockTypeV128


def decode_file(file_name: str):
    data, err = None, None
    try:

        f = open(file_name, 'rb+')
        data = f.read()
        f.seek(0)
    except Exception as e:
        err = e

    if err is not None:
        return Module(), err

    return decode(data, f)


def decode(data, f):
    module, err = None, None
    try:
        module = Module()
        reader = WasmReader(data, f)
        reader.read_module(module)

        f.close()
    except Exception as e:
        err = e
    return module, err


class WasmReader:

    def __init__(self, data=None, reader=None):

        if data is None:
            data = []
        self.reader = reader
        self.data = data

    def remaining(self):

        return len(self.data) - self.reader.tell()

    def read_byte(self):

        if self.remaining() < 1:
            raise ErrUnexpectedEnd
        b = self.reader.read(1)
        return b[0]

    def read_u32(self):

        if self.remaining() < 4:
            raise ErrUnexpectedEnd
        b = int.from_bytes(self.reader.read(4), byteorder='little')
        return ctypes.c_int32(b).value

    def read_f32(self):

        if self.remaining() < 4:
            raise ErrUnexpectedEnd
        b = int.from_bytes(self.reader.read(4), byteorder='little')
        return struct.unpack('>f', struct.pack('>L', b))[0]

    def read_f64(self):

        if self.remaining() < 8:
            raise ErrUnexpectedEnd
        b = int.from_bytes(self.reader.read(8), byteorder='little')
        return struct.unpack('>d', struct.pack('>Q', b))[0]

    def read_v128(self):

        if self.remaining() < 16:
            raise ErrUnexpectedEnd
        b = int.from_bytes(self.reader.read(16), byteorder='little')
        return b

    def read_lane(self):

        if self.remaining() < 1:
            raise ErrUnexpectedEnd
        b = int.from_bytes(self.reader.read(1), byteorder='little')
        return ctypes.c_int32(b).value

    def read_var_u32(self):

        n, w = decode_var_uint(self.reader, 32)

        return n

    def read_var_s32(self):

        n, w = decode_var_int(self.reader, 32)

        return n

    def read_var_s64(self):

        n, w = decode_var_int(self.reader, 64)

        return n

    def read_bytes(self):

        n = self.read_var_u32()
        if self.remaining() < int(n):
            raise ErrUnexpectedEnd
        bytes_data = self.reader.read(n)
        return bytearray(bytes_data)

    def read_name(self):

        data = self.read_bytes()
        try:
            data.decode('utf-8')
        except Exception:
            raise Exception("malformed UTF-8 encoding")

        return str(data, 'utf-8')

    def read_module(self, module: Module):
        if self.remaining() < 4:
            raise Exception("unexpected end of magic header")

        module.magic = self.read_u32()
        if module.magic != MagicNumber:
            raise Exception("magic header not detected")
        if self.remaining() < 4:
            raise Exception("unexpected end of WASMaker version")

        module.version = self.read_u32()
        if module.version != Version:
            raise Exception("unknown WASMaker version: %d" % module.version)

        self.read_sections(module)
        if len(module.func_sec) != len(module.code_sec):
            raise Exception("function and code section have inconsistent lengths")
        if self.remaining() > 0:
            raise Exception("junk after last section")

    def read_sections(self, module: Module):

        prev_sec_id = 0
        while self.remaining() > 0:
            sec_id = self.read_byte()

            if sec_id == SecCustomID:
                n, w = decode_var_uint(self.reader, 32)

                start = self.reader.tell() - w - 1
                end = self.reader.tell() + n
                custom_sec, custom_sec_name = self.read_custom_sec(n)
                module.section_range[SecCustomID].append(SectionRange(start, end, custom_sec_name))
                module.custom_secs.append(custom_sec)
                continue

            if sec_id > SecDataID:
                raise Exception("malformed section id: %d" % sec_id)

            if sec_id <= prev_sec_id:
                raise Exception("junk after last section, id: %d" % sec_id)
            prev_sec_id = sec_id

            n, w = decode_var_uint(self.reader, 32)
            remaining_before_read = self.remaining()
            self.read_non_custom_sec(sec_id, module, n, w)

            remain = self.remaining()
            if remain + int(n) != remaining_before_read:
                raise Exception("section size mismatch, id: %d" % sec_id)

    def read_custom_sec(self, sec_size):
        name = self.read_name()

        if name != "name":
            self.reader.seek(self.reader.tell() - len(name) - 1)
            custom_sec_data = self.reader.read(sec_size)
            return CustomSec(name=name, custom_sec_data=custom_sec_data), name

        name_data = self.read_name_data(self.reader.read(sec_size - len(name) - 1))
        return CustomSec(name=name, name_data=name_data), name

    @staticmethod
    def read_name_data(data):

        funcname_map = []
        globalname_map = []
        dataname_map = []
        tablename_map = []
        module_bytes = None
        local_bytes = None
        labels_bytes = None
        type_bytes = None
        memory_bytes = None
        elem_bytes = None

        while len(data) != 0:
            sub_sec_id = data[:1]
            data = data[1:]
            if sub_sec_id[0] == 0:
                namesubsec_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                module_bytes = data[:namesubsec_size]
                data = data[namesubsec_size:]

            if sub_sec_id[0] == 1:
                funcnamesubsec_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                name_map_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                funcname_map = []
                for _ in range(name_map_size):
                    idx, w = decode_var_uint_from_data(data, 32)
                    data = data[w:]
                    name_size, w = decode_var_uint_from_data(data, 32)
                    data = data[w:]
                    name = data[:name_size]
                    name = bytearray(name).decode('utf-8')
                    data = data[name_size:]
                    name_assoc = NameAssoc(idx=idx, name=name)
                    funcname_map.append(name_assoc)
            if sub_sec_id[0] == 2:
                namesubsec_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                local_bytes = data[:namesubsec_size]
                data = data[namesubsec_size:]

            if sub_sec_id[0] == 3:
                namesubsec_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                labels_bytes = data[:namesubsec_size]
                data = data[namesubsec_size:]

            if sub_sec_id[0] == 4:
                namesubsec_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                type_bytes = data[:namesubsec_size]
                data = data[namesubsec_size:]

            if sub_sec_id[0] == 5:
                tablenamesubsec_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                name_map_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                tablename_map = []
                for _ in range(name_map_size):
                    idx, w = decode_var_uint_from_data(data, 32)
                    data = data[w:]
                    name_size, w = decode_var_uint_from_data(data, 32)
                    data = data[w:]
                    name = data[:name_size]
                    name = bytearray(name).decode('utf-8')
                    data = data[name_size:]
                    name_assoc = NameAssoc(idx=idx, name=name)
                    tablename_map.append(name_assoc)
            if sub_sec_id[0] == 6:
                namesubsec_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                memory_bytes = data[:namesubsec_size]
                data = data[namesubsec_size:]

            if sub_sec_id[0] == 7:
                globalnamesubsec_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                name_map_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                globalname_map = []
                for _ in range(name_map_size):
                    idx, w = decode_var_uint_from_data(data, 32)
                    data = data[w:]
                    name_size, w = decode_var_uint_from_data(data, 32)
                    data = data[w:]
                    name = data[:name_size]
                    name = bytearray(name).decode('utf-8')
                    data = data[name_size:]
                    name_assoc = NameAssoc(idx=idx, name=name)
                    globalname_map.append(name_assoc)
            if sub_sec_id[0] == 8:
                namesubsec_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                elem_bytes = data[:namesubsec_size]
                data = data[namesubsec_size:]

            if sub_sec_id[0] == 9:
                datanamesubsec_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                name_map_size, w = decode_var_uint_from_data(data, 32)
                data = data[w:]
                dataname_map = []
                for _ in range(name_map_size):
                    idx, w = decode_var_uint_from_data(data, 32)
                    data = data[w:]
                    name_size, w = decode_var_uint_from_data(data, 32)
                    data = data[w:]
                    name = data[:name_size]
                    name = bytearray(name).decode('utf-8')
                    data = data[name_size:]
                    name_assoc = NameAssoc(idx=idx, name=name)
                    dataname_map.append(name_assoc)

        name_data = NameData(module_bytes, funcname_map, globalname_map, dataname_map, tablename_map,
                             local_bytes, labels_bytes, type_bytes, memory_bytes, elem_bytes)
        return name_data

    def read_non_custom_sec(self, sec_id, module, sec_size, byte_count_size):

        if sec_id == SecTypeID:

            module.section_range[SecTypeID].start = self.reader.tell() - byte_count_size - 1
            module.section_range[SecTypeID].end = self.reader.tell() + sec_size
            print("type start=" + str(module.section_range[SecTypeID].start))
            print("type end=" + str(module.section_range[SecTypeID].end))

            module.type_sec = self.read_type_sec()
        elif sec_id == SecImportID:
            module.section_range[SecImportID].start = self.reader.tell() - byte_count_size - 1
            module.section_range[SecImportID].end = self.reader.tell() + sec_size
            print("import start=" + str(module.section_range[SecImportID].start))
            print("import end=" + str(module.section_range[SecImportID].end))

            module.import_sec = self.read_import_sec()
        elif sec_id == SecFuncID:
            module.section_range[SecFuncID].start = self.reader.tell() - byte_count_size - 1
            module.section_range[SecFuncID].end = self.reader.tell() + sec_size
            print("func start=" + str(module.section_range[SecFuncID].start))
            print("func end=" + str(module.section_range[SecFuncID].end))

            module.func_sec = self.read_indices()
        elif sec_id == SecTableID:
            module.section_range[SecTableID].start = self.reader.tell() - byte_count_size - 1
            module.section_range[SecTableID].end = self.reader.tell() + sec_size
            print("table start=" + str(module.section_range[SecTableID].start))
            print("table end=" + str(module.section_range[SecTableID].end))

            module.table_sec = self.read_table_sec()
        elif sec_id == SecMemID:
            module.section_range[SecMemID].start = self.reader.tell() - byte_count_size - 1
            module.section_range[SecMemID].end = self.reader.tell() + sec_size
            print("mem start=" + str(module.section_range[SecMemID].start))
            print("mem end=" + str(module.section_range[SecMemID].end))

            module.mem_sec = self.read_mem_sec()
        elif sec_id == SecGlobalID:
            module.section_range[SecGlobalID].start = self.reader.tell() - byte_count_size - 1
            module.section_range[SecGlobalID].end = self.reader.tell() + sec_size
            print("global start=" + str(module.section_range[SecGlobalID].start))
            print("global end=" + str(module.section_range[SecGlobalID].end))

            module.global_sec = self.read_global_sec()
        elif sec_id == SecExportID:
            module.section_range[SecExportID].start = self.reader.tell() - byte_count_size - 1
            module.section_range[SecExportID].end = self.reader.tell() + sec_size
            print("export start=" + str(module.section_range[SecExportID].start))
            print("export end=" + str(module.section_range[SecExportID].end))

            module.export_sec = self.read_export_sec()
        elif sec_id == SecStartID:
            module.section_range[SecStartID].start = self.reader.tell() - byte_count_size - 1
            module.section_range[SecStartID].end = self.reader.tell() + sec_size
            print("start start=" + str(module.section_range[SecStartID].start))
            print("start end=" + str(module.section_range[SecStartID].end))

            module.start_sec = self.read_start_sec()
        elif sec_id == SecElemID:
            module.section_range[SecElemID].start = self.reader.tell() - byte_count_size - 1
            module.section_range[SecElemID].end = self.reader.tell() + sec_size
            print("elem start=" + str(module.section_range[SecElemID].start))
            print("elem end=" + str(module.section_range[SecElemID].end))

            module.elem_sec = self.read_elem_sec()
        elif sec_id == SecCodeID:
            module.section_range[SecCodeID].start = self.reader.tell() - byte_count_size - 1
            module.section_range[SecCodeID].end = self.reader.tell() + sec_size
            print("code start=" + str(module.section_range[SecCodeID].start))
            print("code end=" + str(module.section_range[SecCodeID].end))

            module.code_sec = self.read_code_sec()
        elif sec_id == SecDataID:
            module.section_range[SecDataID].start = self.reader.tell() - byte_count_size - 1
            module.section_range[SecDataID].end = self.reader.tell() + sec_size
            print("data start=" + str(module.section_range[SecDataID].start))
            print("data end=" + str(module.section_range[SecDataID].end))

            module.data_sec = self.read_data_sec()

    def read_type_sec(self):

        vec = []
        for _ in range(self.read_var_u32()):
            vec.append(self.read_func_type())
        return vec

    def read_import_sec(self):

        vec = []
        for _ in range(self.read_var_u32()):
            vec.append(self.read_import())
        return vec

    def read_import(self):
        return Import(self.read_name(), self.read_name(), self.read_import_desc())

    def read_import_desc(self):
        desc = ImportDesc(self.read_byte())
        tag = desc.tag

        if tag == ImportTagFunc:
            desc.func_type = self.read_var_u32()


        elif tag == ImportTagTable:
            desc.table = self.read_table_type()


        elif tag == ImportTagMem:
            desc.mem = self.read_limits()


        elif tag == ImportTagGlobal:
            desc.global_type = self.read_global_type()
        else:
            raise Exception("invalid import desc tag: %d" % tag)
        return desc

    def read_table_sec(self):

        vec = []
        for _ in range(self.read_var_u32()):
            vec.append(self.read_table_type())
        return vec

    def read_mem_sec(self):

        vec = []
        for _ in range(self.read_var_u32()):
            vec.append(self.read_limits())
        return vec

    def read_global_sec(self):

        vec = []
        for _ in range(self.read_var_u32()):
            global_obj = Global(self.read_global_type(), self.read_expr())
            vec.append(global_obj)
        return vec

    def read_export_sec(self):

        vec = []
        for _ in range(self.read_var_u32()):
            vec.append(self.read_export())
        return vec

    def read_export(self):
        return Export(self.read_name(), self.read_export_desc())

    def read_export_desc(self):
        desc = ExportDesc(tag=self.read_byte(), idx=self.read_var_u32())
        tag = desc.tag
        if tag not in [ExportTagFunc, ExportTagTable, ExportTagMem, ExportTagGlobal]:
            raise Exception("invalid export desc tag: %d" % tag)
        return desc

    def read_start_sec(self):

        idx = self.read_var_u32()
        return idx

    def read_elem_sec(self):

        vec = []
        for _ in range(self.read_var_u32()):
            vec.append(self.read_elem())
        return vec

    def read_elem(self):
        return Elem(self.read_var_u32(), self.read_expr(), self.read_indices())

    def read_code_sec(self):

        vec = [Code()] * self.read_var_u32()
        for i in range(len(vec)):
            vec[i] = self.read_code(i)
        return vec

    def read_code(self, idx):
        n = self.read_var_u32()
        remaining_before_read = self.remaining()
        code = Code(self.read_locals_vec(), self.read_expr())
        if self.remaining() + int(n) != remaining_before_read:
            print("invalid code[%d]" % idx)
        if code.get_local_count() >= (1 << 32 - 1):
            raise Exception("too many locals: %d" % code.get_local_count())
        return code

    def read_locals_vec(self):
        vec = []
        for _ in range(self.read_var_u32()):
            vec.append(self.read_locals())
        return vec

    def read_locals(self):
        return Locals(self.read_var_u32(), self.read_val_type())

    def read_data_sec(self):

        vec = []
        for _ in range(self.read_var_u32()):
            vec.append(self.read_data())
        return vec

    def read_data(self):
        return Data(self.read_var_u32(), self.read_expr(), self.read_bytes())

    def read_val_types(self):
        vec = []
        for _ in range(self.read_var_u32()):
            vec.append(self.read_val_type())
        return vec

    def read_val_type(self):
        vt = self.read_byte()
        if vt not in [ValTypeI32, ValTypeI64, ValTypeF32, ValTypeF64, ValTypeV128]:
            raise Exception("malformed value type: %d" % vt)
        return vt

    def read_block_type(self):
        bt = self.read_var_s32()
        if bt < 0:
            if bt not in [BlockTypeI32, BlockTypeI64, BlockTypeF32, BlockTypeF64, BlockTypeV128, BlockTypeEmpty]:
                raise Exception("malformed block type: %d" % bt)

        return bt

    def read_func_type(self):
        ft = FuncType(self.read_byte(), self.read_val_types(), self.read_val_types())
        if ft.tag != FtTag:
            raise Exception("invalid functype tag: %d" % ft.tag)
        return ft

    def read_table_type(self):
        tt = TableType(self.read_byte(), self.read_limits())
        if tt.elem_type != FuncRef:
            raise Exception("invalid elemtype: %d" % tt.elem_type)
        return tt

    def read_global_type(self):

        gt = GlobalType(self.read_val_type(), self.read_byte())
        if gt.mut not in [MutConst, MutVar]:
            raise Exception("malformed mutability: %d" % gt.mut)
        return gt

    def read_limits(self):
        limits = Limits(self.read_byte(), self.read_var_u32())
        if limits.tag == 1:
            limits.max = self.read_var_u32()
        return limits

    def read_indices(self):
        vec = []
        for _ in range(self.read_var_u32()):
            vec.append(self.read_var_u32())
        return vec

    def read_expr(self):
        instrs, end = self.read_instructions()
        if end != End_:
            raise Exception("invalid expr end: %d" % end)
        return instrs

    def read_instructions(self):

        instrs = []
        while (True):
            instr = self.read_instruction()
            if instr.opcode == Else_ or instr.opcode == End_:
                end = instr.opcode
                return instrs, end

            instrs.append(instr)

    def read_instruction(self):

        instr = Instruction()
        instr.opcode = self.read_byte()

        if instr.opcode == 0xFC:
            instr.opcode = instr.opcode * 256 + self.read_byte()
        elif instr.opcode == 0xFD:
            second_byte = self.read_byte()

            if second_byte > 0x7F:
                instr.opcode = instr.opcode * 256 * 256 + second_byte * 256 + self.read_byte()

            else:
                instr.opcode = instr.opcode * 256 + second_byte

        if opnames[instr.opcode] == "":
            raise Exception("undefined opcode: 0x%02x" % instr.opcode)

        instr.args = self.read_args(instr.opcode)
        return instr

    def read_args(self, opcode):
        if opcode in [Block, Loop]:
            return self.read_block_args()
        elif opcode == If:
            return self.read_if_args()
        elif opcode in [Br, BrIf]:
            return self.read_var_u32()
        elif opcode == BrTable:
            return self.read_br_table_args()
        elif opcode == Call:
            return self.read_var_u32()
        elif opcode == CallIndirect:
            return self.read_call_indirect_args()
        elif opcode in [LocalGet, LocalSet, LocalTee]:
            return self.read_var_u32()
        elif opcode in [GlobalGet, GlobalSet]:
            return self.read_var_u32()
        elif opcode in [MemorySize, MemoryGrow]:
            return self.read_zero()
        elif opcode == I32Const:
            return self.read_var_s32()
        elif opcode == I64Const:
            return self.read_var_s64()
        elif opcode == F32Const:
            return self.read_f32()
        elif opcode == F64Const:
            return self.read_f64()
        elif opcode == V128Const:
            return self.read_v128()
        elif opcode == I8x16Shuffle:
            return self.read_v128()
        elif I8x16ExtractLaneS <= opcode <= F64x2ReplaceLane:
            return self.read_lane()
        elif opcode in [RefNull, RefFunc]:
            return self.read_var_u32()
        elif opcode in [MemoryInit, DataDrop, ElemDrop, TableGrow, TableSize, TableFill]:
            return self.read_var_u32()
        elif opcode in [TableInit, TableCopy]:
            x = self.read_var_u32()
            y = self.read_var_u32()
            return TableArg(x, y)
        elif V128Load <= opcode <= V128Store or opcode in [V128Load32Zero, V128Load64Zero]:
            return self.read_mem_arg()
        elif V128Load8Lane <= opcode <= V128Store64Lane:
            mem_arg = self.read_mem_arg()
            laneidx = self.read_lane()
            return MemLaneArg(mem_arg, laneidx)
        elif I32Load <= opcode <= I64Store32:
            return self.read_mem_arg()
        else:
            return None

    def read_block_args(self):

        args = BlockArgs()
        args.bt = self.read_block_type()
        args.instrs, end = self.read_instructions()
        if end != End_:
            raise Exception("invalid block end: %d" % end)
        return args

    def read_if_args(self):

        args = IfArgs()
        args.bt = self.read_block_type()
        args.instrs1, end = self.read_instructions()
        if end == Else_:
            args.instrs2, end = self.read_instructions()
            if end != End_:
                raise Exception("invalid block end: %d" % end)
        return args

    def read_br_table_args(self):

        return BrTableArgs(self.read_indices(), self.read_var_u32())

    def read_call_indirect_args(self):

        type_idx = self.read_var_u32()
        self.read_zero()
        return type_idx

    def read_mem_arg(self):

        return MemArg(self.read_var_u32(), self.read_var_u32())

    def read_zero(self):
        b = self.read_byte()
        if b != 0:
            raise Exception("zero flag expected, got %d" % b)
        return 0
