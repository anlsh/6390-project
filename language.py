import operator as op

mod_un = "un"
mod_lin = "lin"
mod_aff = "aff"
type_mods = [mod_un, mod_lin, mod_aff]

en_ref = 'ref'
en_fun = 'fun'
en_o = 'val'
type_enum = [en_ref, en_fun, en_o]

MACRO_NAMES = ["defun", "deftype", "defvar", "apply", "if", "while", "set", "ref", "dref", "mutref"]

builtin_fns = {
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'print': print
}