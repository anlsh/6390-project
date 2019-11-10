import operator as op
from dsl_types import FunType, ValType, Tmod

MACRO_NAMES = ["defun", "deftype", "defvar", "apply", "if", "while", "set", "ref", "dref", "mutref"]
bool_map = {"true": True, "false": False}

builtin_fn_vals = {
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le,
        'print': print
}

T_NIL = ValType(mod=Tmod.un, args='nil')
T_UNIT = ValType(mod=Tmod.un, args='unit')
T_BOOL = ValType(mod=Tmod.un, args='bool')
T_LIN_BOOL = ValType(mod=Tmod.lin, args='bool')

T_INT = ValType(mod=Tmod.un, args='int')
T_LIN_INT = ValType(mod=Tmod.lin, args='int')

builtin_fn_types = {
    "+": FunType(mod=Tmod.un, retT=T_INT, argTs=(T_LIN_INT, T_LIN_INT)),
    "-": FunType(mod=Tmod.un, retT=T_INT, argTs=(T_LIN_INT, T_LIN_INT)),
    "not": FunType(mod=Tmod.un, retT=T_BOOL, argTs=(T_BOOL,)),
}

