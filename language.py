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
T_INT = ValType(mod=Tmod.un, args='int')

builtin_fn_types = {
        "+": FunType(mod=Tmod.un, retT=T_INT, argTs=(T_INT, T_INT)),
        "not": FunType(mod=Tmod.un, retT=T_BOOL, argTs=(T_BOOL,))
}