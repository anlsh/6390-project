import pytest

from syntax import check_syntax
from syntax_errors import *
from dsl_parser import dsl_parse


def test_undefined_var_access():
    program = "(set foo-t 3)"

    code = dsl_parse(program)
    with pytest.raises(VariableUndefinedError):
        check_syntax(code)


def test_type_def():
    program = "((deftype integer) (defvar qq un integer))"
    code = dsl_parse(program)
    check_syntax(code)

    program = "(defvar qq un integer)"
    code = dsl_parse(program)
    with pytest.raises(TypeUndefinedError):
        check_syntax(code)


def test_functions():
    program = "(defun (fname un bool) ((arg1 un bool) (arg2 un bool)) (arg1))"
    code = dsl_parse(program)
    with pytest.raises(TypeUndefinedError):
        check_syntax(code)

    program = "((deftype bool) (defun (fname un bool) ((arg1 un bool) (arg2 un bool)) (arg1)))"
    code = dsl_parse(program)
    check_syntax(code)


def test_sealed_function_scope1():
    program = "((deftype bool) (defun (fname un bool) ((arg1 un bool) " \
              "(arg2 un bool)) (arg1 (defvar qq un bool)))  (arg1) )"
    code = dsl_parse(program)
    with pytest.raises(VariableUndefinedError):
        check_syntax(code)


def test_sealed_function_scope2():
    program = "((deftype bool) (defun (fname un bool) ((arg1 un bool) " \
              "(arg2 un bool)) (arg1 (defvar qq un bool)))  (qq) )"
    code = dsl_parse(program)
    with pytest.raises(VariableUndefinedError):
        check_syntax(code)

    program = "((deftype bool) (defun (fname un bool) ((arg1 un bool) " \
              "(arg2 un bool)) (qq))  )"
    code = dsl_parse(program)
    with pytest.raises(VariableUndefinedError):
        check_syntax(code)

    program = "((deftype bool) (defvar qq un bool) (defun (fname un bool) ((arg1 un bool) " \
              "(qq un bool)) ())  (qq))"
    code = dsl_parse(program)
    check_syntax(code)
