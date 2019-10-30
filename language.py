import operator as op

UNIT = "unit-type-repr"
NIL = "nil-type-repr"

MACRO_NAMES = ["defun", "deftype", "defvar", "apply", "if", "while", "set", "ref", "dref", "mutref"]

builtin_fns = {
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'print': print
}

builtin_fn_types = {
        '+': ["int", "float"],
        '-': ["int", "float"],
        '*': ["int", "float"],
        '/': ["int", "float"],
        '>': "bool",
        '<': "bool",
        '>=': "bool",
        '<=': "bool",
        '=': "bool",
        # what return type is print?
        'print': NIL
}
