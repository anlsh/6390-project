import operator as op
import dsl_types as dslT
from dsl_types import FunType, ValType, Tmod

MACRO_NAMES = ["defun", "defvar", "apply", "if", "while", "set", "mkref", "setref", "deref", "setrefval"]
bool_map = {"true": True, "false": False}

builtin_fn_vals = {
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'not': op.not_
}

T_NIL = ValType(mod=Tmod.un, tname='nil')
T_UNIT = ValType(mod=Tmod.un, tname='unit')
T_BOOL = ValType(mod=Tmod.un, tname='bool')
T_LIN_BOOL = ValType(mod=Tmod.lin, tname='bool')
T_FILE = ValType(mod=Tmod.lin, tname='file')

T_INT = ValType(mod=Tmod.un, tname='int')
T_LIN_INT = ValType(mod=Tmod.lin, tname='int')

builtin_fn_types = {
    "+": FunType(mod=Tmod.un, retT=T_INT, argTs=(T_LIN_INT, T_LIN_INT)),
    "-": FunType(mod=Tmod.un, retT=T_INT, argTs=(T_LIN_INT, T_LIN_INT)),
    "/": FunType(mod=Tmod.un, retT=T_INT, argTs=(T_LIN_INT, T_LIN_INT)),
    ">": FunType(mod=Tmod.un, retT=T_BOOL, argTs=(T_LIN_INT, T_LIN_INT)),
    "<": FunType(mod=Tmod.un, retT=T_BOOL, argTs=(T_LIN_INT, T_LIN_INT)),
    ">=": FunType(mod=Tmod.un, retT=T_BOOL, argTs=(T_LIN_INT, T_LIN_INT)),
    "<=": FunType(mod=Tmod.un, retT=T_BOOL, argTs=(T_LIN_INT, T_LIN_INT)),
    "=": FunType(mod=Tmod.un, retT=T_BOOL, argTs=(T_LIN_INT, T_LIN_INT)),
    "not": FunType(mod=Tmod.un, retT=T_BOOL, argTs=(T_LIN_BOOL,)),
    "fopen": FunType(mod=Tmod.un, retT=T_FILE, argTs=(T_LIN_INT,)),
    "fwrite": FunType(mod=Tmod.un, retT=T_UNIT, argTs=(dslT.RefType(mod=Tmod.un, ref_type=T_FILE),
                                                       T_LIN_INT),),
    "fclose": FunType(mod=Tmod.un, retT=T_UNIT, argTs=(T_FILE,))
}
