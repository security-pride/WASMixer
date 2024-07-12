from ..parser.types import BlockTypeI32, BlockTypeI64, BlockTypeF32, BlockTypeF64, BlockTypeEmpty, FuncType, \
    ValTypeI32, ValTypeI64, ValTypeF32, ValTypeF64

MagicNumber = 0x6D736100

Version = 0x00000001

SecCustomID = 0

SecTypeID = 1

SecImportID = 2

SecFuncID = 3

SecTableID = 4

SecMemID = 5

SecGlobalID = 6

SecExportID = 7

SecStartID = 8

SecElemID = 9

SecCodeID = 10

SecDataID = 11

ImportTagFunc = 0
ImportTagTable = 1
ImportTagMem = 2
ImportTagGlobal = 3

ExportTagFunc = 0
ExportTagTable = 1
ExportTagMem = 2
ExportTagGlobal = 3

TypeIdx = int

FuncIdx = int

TableIdx = int
MemIdx = int

GlobalIdx = int

LocalIdx = int

LabelIdx = int


class Module:

    def __init__(self, magic=None, version=None):

        if magic:
            self.magic = magic
        else:
            self.magic = 0

        if version:
            self.version = version
        else:
            self.version = 0

        self.custom_secs = []

        self.type_sec = []

        self.import_sec = []

        self.func_sec = []

        self.table_sec = []

        self.mem_sec = []

        self.global_sec = []

        self.export_sec = []

        self.start_sec = None

        self.elem_sec = []

        self.code_sec = []

        self.data_sec = []

        self.section_range = []
        self.section_range.append([])
        for i in range(11):
            self.section_range.append(SectionRange())

    def get_block_type(self, bt):

        if bt == BlockTypeI32:
            return FuncType(result_types=[ValTypeI32])
        elif bt == BlockTypeI64:
            return FuncType(result_types=[ValTypeI64])
        elif bt == BlockTypeF32:
            return FuncType(result_types=[ValTypeF32])
        elif bt == BlockTypeF64:
            return FuncType(result_types=[ValTypeF64])
        elif bt == BlockTypeEmpty:
            return FuncType()
        else:
            return self.type_sec[bt]


class SectionRange:

    def __init__(self, start=0, end=0, name=None):
        self.start = start
        self.end = end

        self.name = name


class CustomSec:

    def __init__(self, name="", custom_sec_data=None, name_data=None):
        self.name = name
        self.custom_sec_data = custom_sec_data
        self.name_data = name_data


class NameData:

    def __init__(self, moduleNameSubSec=None, funcNameSubSec=None, globalNameSubSec=None, dataNameSubSec=None,
                 tableNameSubSec=None,
                 local_bytes=None, labels_bytes=None, type_bytes=None, memory_bytes=None, elem_bytes=None):

        self.moduleNameSubSec = None
        self.localNameSubSec = None
        self.labelsNameSubSec = None
        self.typeNameSubSec = None
        self.memoryNameSubSec = None
        self.elemNameSubSec = None

        if not funcNameSubSec is None:
            self.funcNameSubSec = funcNameSubSec
        if not globalNameSubSec is None:
            self.globalNameSubSec = globalNameSubSec
        if not dataNameSubSec is None:
            self.dataNameSubSec = dataNameSubSec
        if not tableNameSubSec is None:
            self.tableNameSubSec = tableNameSubSec

        if not moduleNameSubSec is None:
            self.moduleNameSubSec = moduleNameSubSec
        if not local_bytes is None:
            self.localNameSubSec = local_bytes
        if not labels_bytes is None:
            self.labelsNameSubSec = labels_bytes
        if not type_bytes is None:
            self.typeNameSubSec = type_bytes
        if not memory_bytes is None:
            self.memoryNameSubSec = memory_bytes
        if not elem_bytes is None:
            self.elemNameSubSec = elem_bytes


class Import:
    """
    导入类型：函数、表、内存、全局变量
    import_sec: 0x02|byte_count|vec<import>
    import     : module_name|member_name|import_desc
    """

    def __init__(self, module="", name="", desc=None):
        self.module = module

        self.name = name

        self.desc = desc


class ImportDesc:

    def __init__(self, tag, func_type=None, table=None, mem=None, global_type=None):
        self.tag = tag
        self.func_type = func_type
        self.table = table
        self.mem = mem
        self.global_type = global_type


class Global:

    def __init__(self, global_type=None, init=None):
        self.type = global_type
        self.init = init


class Export:

    def __init__(self, name="", export_desc=None):
        self.name = name
        self.desc = export_desc


class ExportDesc:

    def __init__(self, tag=0, idx=0):
        self.tag = tag
        self.idx = idx


class Elem:

    def __init__(self, table_idx=0, offset_expr=None, vec_init=None):
        if vec_init is None:
            vec_init = []
        self.table = table_idx
        self.offset = offset_expr
        self.init = vec_init


class Code:

    def __init__(self, locals_vec=None, expr=None):
        if locals_vec is None:
            locals_vec = []
        self.locals = locals_vec
        self.expr = expr

    def get_local_count(self) -> int:
        n = 0
        for locals_item in self.locals:
            n += locals_item.n
        return n


class Locals:

    def __init__(self, local_count=0, val_type=0):
        self.n = local_count
        self.type = val_type

    def convert_locals(self):
        local_vec = [self.type] * self.n
        return local_vec

    def __str__(self):
        return "{type: %d, n: %d}" % (self.type, self.n)


class Data:

    def __init__(self, mem_idx=0, offset_expr=None, vec_init=None):
        if vec_init is None:
            vec_init = []
        self.mem = mem_idx
        self.offset = offset_expr
        self.init = vec_init
