import pytest
import language as lang
from affine_checker import AffineTypeChecker as ATC, TypeMismatchError, UnusedLinVariableError
from env import Env, BindingRedefinitionError
from parser import parse


@pytest.fixture
def base_env():
    return Env(outer=Env(defaults=lang.builtin_fn_types))


def test_declare_variable(base_env):
    prog = parse("(defvar x (un val int) 3)")
    ret_type = ATC.type_check(base_env, prog)
    assert ret_type == lang.T_UNIT
    assert base_env.get_bind_val('x') == lang.tparse(parse("(aff ref (un val int))"))


def test_plus_type_checks_correct_args(base_env):
    prog = parse("(apply + 3 3)")
    ret_type = ATC.type_check(base_env, prog)
    assert ret_type == lang.T_INT


def test_plus_type_checks_incorrect_args(base_env):
    prog = parse("(apply + true 3)")
    with pytest.raises(TypeMismatchError):
        ATC.type_check(base_env, prog)


def test_variables_redeclare(base_env):
    with pytest.raises(BindingRedefinitionError):
        prog = parse("((defvar x (un val int) 3) (defvar x (un val int) 3) )")
        ATC.type_check(base_env, prog)


def test_decl_var1(base_env):
    prog = parse("((defvar x (un val int) 3) (defvar y (un val int) 3) )")
    ATC.type_check(base_env, prog)


def test_decl_var2(base_env):
    prog = parse("((defvar x (un val int) 3) (set x 3))")
    T = ATC.type_check(base_env, prog)
    assert T == lang.T_INT


def test_decl_var3(base_env):
    # TODO Should we be able to set multiple values like this?
    prog = parse("((defvar x (un val int) 3) (set x 3) (set x 4))")
    T = ATC.type_check(base_env, prog)
    assert T == lang.T_INT
    # assert ctx['x'] == lang.tparse(parse("(aff ref (un val int))"))


def test_decl_var4(base_env):
    # TODO Do we need to care about this?
    prog = parse("((defvar x (un val int) 3) (set x 3) (set x (+ x 1)))")
    T = ATC.type_check(base_env, prog)
    assert T == lang.T_INT
    # assert ctx['x'] == tparse(parse("(aff ref (un val int))"))


def test_unused_linint_errs(base_env):
    # TODO Do we need to care about this?
    prog = parse("(defvar x (lin val int) 3)")
    with pytest.raises(UnusedLinVariableError):
        T = ATC.type_check(base_env, prog, descope=True)