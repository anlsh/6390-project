import operator as op
from typing import Tuple, Union
from enum import Enum


def str_in_enum(key: str, EType) -> bool:
    return key in [x.value for x in EType]


class T_mod(Enum):
    un = "un"
    lin = "lin"
    aff = "aff"


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

        if not str_in_enum(self.mod, T_mod):
            raise RuntimeError(f"Unrecognized type {self.mod}")
        elif not str_in_enum(self.type_enum, type_enum):
            raise RuntimeError(f'Unrecognized type {self.type_enum}')

    def __eq__(self, other):
        return (self.mod == other.mod) and (self.type_enum == other.type_enum) and (self.type_args == other.type_args)


def tparse(type_prog: Union[str, Tuple]) -> Type:
    """
    Given a program tree generated via the CFG defined in language spec, create the corresponding Type object
    """
    mod, enum, args = type_prog
    if enum == T_cat.fun:
        ret_type, arg_types = args
        parsed_arg_types = tuple(tparse(a) for a in arg_types)
        return Type(mod, enum, (Type(*ret_type), parsed_arg_types))
    elif enum == T_cat.ref:
        return Type(mod, enum, tparse(args))
    elif enum == T_cat.val:
        return Type(mod, enum, args)
    else:
        raise RuntimeError("Unrecognized type code!")


builtin_fn_vals = {
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'print': print
}

builtin_fn_types = {
        "+": tparse((T_mod.un, T_cat.fun, ((T_mod.un, T_cat.val, 'int'),
                                           ((T_mod.un, T_cat.val, 'int'), (T_mod.un, T_cat.val, 'int'))))),
        "not": tparse((T_mod.un, T_cat.fun, ((T_mod.un, T_cat.val, 'bool'),
                                             ((T_mod.un, T_cat.val, 'bool'),))))
}

T_NIL = Type(T_mod.un, T_cat.val, 'nil')
T_UNIT = Type(T_mod.un, T_cat.val, 'unit')
T_BOOL = Type(T_mod.un, T_cat.val, 'bool')
T_INT = Type(T_mod.un, T_cat.val, 'int')