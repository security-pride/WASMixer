ValTypeI32 = 0x7F

ValTypeI64 = 0x7E

ValTypeF32 = 0x7D

ValTypeF64 = 0x7C

ValTypeV128 = 0x7B

ValTypeAny = 0x7C

BlockTypeI32 = -1
BlockTypeI64 = -2
BlockTypeF32 = -3
BlockTypeF64 = -4
BlockTypeV128 = -5
BlockTypeEmpty = -64

FtTag = 0x60
FuncRef = 0x70
ExternRef = 0x6F

MutConst = 0
MutVar = 1


class FuncType:

    def __init__(self, tag=0, param_types=None, result_types=None):
        if result_types is None:
            result_types = []
        if param_types is None:
            param_types = []
        self.tag = tag

        self.param_types = param_types

        self.result_types = result_types

    def equal(self, ft2) -> bool:
        if len(self.param_types) != len(ft2.param_types) \
                or len(self.result_types) != len(ft2.result_types):
            return False
        for i, vt in enumerate(self.param_types):
            if vt != ft2.param_types[i]:
                return False
        for i, vt in enumerate(self.result_types):
            if vt != ft2.result_types[i]:
                return False
        return True

    def print_signature(self) -> str:
        sb = "("
        sb += ",".join([val_type_to_str(vt) for vt in self.param_types])
        sb += ")->("
        sb += ",".join([val_type_to_str(vt) for vt in self.result_types])
        sb += ")"
        return sb

    def get_signature(self):
        arg_types = []
        ret_types = []
        for valtype in self.param_types:
            if valtype == ValTypeI32:
                arg_types.append("i32")
            elif valtype == ValTypeI64:
                arg_types.append("i64")
            elif valtype == ValTypeF32:
                arg_types.append("f32")
            elif valtype == ValTypeF64:
                arg_types.append("f64")
        for valtype in self.result_types:
            if valtype == ValTypeI32:
                ret_types.append("i32")
            elif valtype == ValTypeI64:
                ret_types.append("i64")
            elif valtype == ValTypeF32:
                ret_types.append("f32")
            elif valtype == ValTypeF64:
                ret_types.append("f64")
        return arg_types, ret_types

    def __str__(self):
        return self.print_signature()


class Limits:

    def __init__(self, tag=0, min=0, max=0):
        self.tag = tag
        self.min = min
        self.max = max

    def __str__(self):
        return "{min: %d, max: %d}" % (self.min, self.max)


MemType = Limits


class TableType:

    def __init__(self, elem_type=0x70, limits=None):
        self.elem_type = elem_type

        self.limits = limits


class GlobalType:

    def __init__(self, val_type=0, mut=0):
        self.val_type = val_type

        self.mut = mut

    def __str__(self):
        return "{type: %s, mut: %d}" % (val_type_to_str(self.val_type), self.mut)


class NameAssoc:

    def __init__(self, idx=0, name=None):
        self.idx = idx

        self.name = name

    def __str__(self):
        return "{id: %d, name: %s}" % (self.idx, self.name)


def val_type_to_str(vt) -> str:
    if vt == ValTypeI32:
        return "i32"
    elif vt == ValTypeI64:
        return "i64"
    elif vt == ValTypeF32:
        return "f32"
    elif vt == ValTypeF64:
        return "f64"
    else:
        raise Exception("invalid valtype: %d" % vt)
