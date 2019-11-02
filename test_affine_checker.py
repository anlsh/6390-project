import pytest
from affine_checker import *
from parser import parse
from copy import deepcopy

@pytest.fixture
def fbase_context():
    return deepcopy(base_context)


def test_declare_variable(fbase_context):
    prog = parse("(defvar x (un val int) 3)")
    ctx, ret_type = type_check(fbase_context, prog)
    assert ret_type == T_UNIT
    assert ctx['x'] == tparse(parse("(aff ref (un val int))"))


def test_plus_type_checks_correct_args(fbase_context):
    prog = parse("(+ 3 3)")
    ctx, ret_type = type_check(fbase_context, prog)
    assert ret_type == T_INT


def test_plus_type_checks_incorrect_args(fbase_context):
    prog = parse("(apply + true 3)")
    with pytest.raises(TypeMismatchError):
        ctx, ret_type = type_check(fbase_context, prog)


def test_variables_work(fbase_context):
    with pytest.raises(VariableRedefinitionError):
        prog = parse("((defvar x (un val int) 3) (defvar x (un val int) 3) )")
        _ = type_check(fbase_context, prog)

    prog = parse("((defvar x (un val int) 3) (defvar y (un val int) 3) )")
    _ = type_check(fbase_context, prog)

    prog = parse("((defvar x (un val int) 3) (set x 3))")
    ctx, T = type_check(fbase_context, prog)
    assert T == T_UNIT
    assert ctx['x'] == tparse(parse("(aff ref (un val int))"))

    # TODO Should we be able to set multiple values like this?
    prog = parse("((defvar x (un val int) 3) (set x 3) (set x 4))")
    ctx, T = type_check(fbase_context, prog)
    assert T == T_UNIT
    assert ctx['x'] == tparse(parse("(aff ref (un val int))"))

    # TODO Do we need to care about this?
    prog = parse("((defvar x (un val int) 3) (set x 3) (set x (+ x 1)))")
    ctx, T = type_check(fbase_context, prog)
    assert T == T_UNIT
    assert ctx['x'] == tparse(parse("(aff ref (un val int))"))