import operator as op
from typing import Tuple, Union
from enum import Enum
from parser import parse


def str_in_enum(key: str, EType) -> bool:
    return key in [x.value for x in EType]


class T_mod(Enum):
    un = "un"
    lin = "lin"
    aff = "aff"

    @classmethod
    def restriction_hierarchy(cls,):
        """
        A appearing before B in the hierarchy means that A is less restrictive than B
        :return:
        """
        return [cls.un, cls.aff, cls.lin]


class T_cat(Enum):
    ref = 'ref'
    fun = 'fun'
    val = 'val'


MACRO_NAMES = ["defun", "deftype", "defvar", "apply", "if", "while", "set", "ref", "dref", "mutref"]


class Type:
    def __init__(self, mod, type_enum, type_args):
        self.mod = mod
        self.type_enum = type_enum
        self.type_args = type_args

    def __eq__(self, other):
        return (self.mod == other.mod) and (self.type_enum == other.type_enum) and (self.type_args == other.type_args)

    def less_restrictive(self, other):
        self_mod = self.mod
        other_mod = other.mod
        p1 = T_mod.restriction_hierarchy().index(self_mod) <= T_mod.restriction_hierarchy().index(other_mod)
        # WARNING Code duplicated from above
        return p1 and (self.type_enum == other.type_enum) and (self.type_args == other.type_args)


def tparse(type_prog: Union[str, Tuple]) -> Type:
    """
    Given a program tree generated via the CFG defined in language spec, create the corresponding Type object
    """
    modstr, enumstr, args = type_prog
    mod, enum = T_mod[modstr], T_cat[enumstr]

    if enum == T_cat.fun:
        ret_tprog, arg_tprog_ls = args
        ret_t = tparse(ret_tprog)
        parsed_arg_types = tuple(tparse(a) for a in arg_tprog_ls)
        return Type(mod, enum, (ret_t, parsed_arg_types))
    elif enum == T_cat.ref:
        return Type(mod, enum, tparse(args))
    elif enum == T_cat.val:
        return Type(mod, enum, args)
    else:
        raise RuntimeError("Unrecognized type code!")


def tparse_from_string(prog_code: str) -> Type:
    return tparse(parse(prog_code))


builtin_fn_vals = {
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'print': print
}

builtin_fn_types = {
        "+":  tparse((T_mod.un.value, T_cat.fun.value,
                      ((T_mod.un.value, T_cat.val.value, 'int'),
                        ((T_mod.un.value, T_cat.val.value, 'int'),
                         (T_mod.un.value, T_cat.val.value, 'int')))
                      )),
        "not": tparse((T_mod.un.value, T_cat.fun.value, ((T_mod.un.value, T_cat.val.value, 'bool'),
                                             ((T_mod.un.value, T_cat.val.value, 'bool'),))))
}

T_NIL = Type(T_mod.un, T_cat.val, 'nil')
T_UNIT = Type(T_mod.un, T_cat.val, 'unit')
T_BOOL = Type(T_mod.un, T_cat.val, 'bool')
T_INT = Type(T_mod.un, T_cat.val, 'int')