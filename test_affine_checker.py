import pytest
import language as lang
import typecheck_errors as tc_err
from affine_checker import AffineTypeChecker as ATC
import dsl_types as dslT
from env import TypeCheckEnv, deepcopy_env
from dsl_parser import dsl_parse


def base_tcheck_env():
    return TypeCheckEnv(outer=TypeCheckEnv(defaults=lang.builtin_fn_types))


def test_reference():
    prog = dsl_parse("("
                     "(defvar x (un val int) 0)"
                     "(defvar xref (un ref (un val int)) (mkref x))"
                     "xref"
                     ")")
    env = base_tcheck_env()
    T = ATC.type_check(env, prog)
    assert isinstance(T, dslT.RefType)
    assert T.referenced_type() == lang.T_INT


def test_reference_no_effect():
    prog = dsl_parse("("
                     "(defvar x (un val int) 0)"
                     "(mkref x)"
                     ")")
    env = base_tcheck_env()
    with pytest.raises(tc_err.ReferenceNoEffectError):
        ATC.type_check(env, prog)


def test_env_copy_works():
    prog = dsl_parse("(  "
                     "    (defvar x (un val int) 0) "
                     "    (defvar y (un val int) 0)  "
                     "    (while (apply < x 3) 0 ((set x (apply + x 1)) x))"
                     ")")
    env = base_tcheck_env()
    ATC.type_check(env, prog, descope=False)
    env_cp = deepcopy_env(env)
    assert env == env_cp


def test_unrestricted_variables():

    # Declaring an unrestricted value works...
    prog = dsl_parse("(defvar x (un val int) 3)")
    env = base_tcheck_env()
    ret_type = ATC.type_check(env, prog)
    assert ret_type == lang.T_UNIT
    assert env.get_bind_val('x') == dslT.tparse(dsl_parse("(un val int)"))

    # But you're not allowed to defvar a name twice, even with same type
    prog = dsl_parse("((defvar x (un val int) 3) (defvar x (un val int) 4))")
    env = base_tcheck_env()
    with pytest.raises(tc_err.BindingRedefinitionError):
        ATC.type_check(env, prog)

    # Unrestricted values can be used multiple times
    prog = dsl_parse("((defvar x (un val int) 3) x x)")
    env = base_tcheck_env()
    ret_type = ATC.type_check(env, prog)
    assert ret_type == lang.T_INT

    # Can turn an unrestricted value into an affine one
    prog = dsl_parse("((defvar x (aff val int) 3))")
    env = base_tcheck_env()
    ret_type = ATC.type_check(env, prog)
    assert ret_type == lang.T_UNIT

    # But you can't make an affine value unrestricted
    prog = dsl_parse("((defvar x (aff val int) 3) (defvar y (un val int) x))")
    env = base_tcheck_env()
    with pytest.raises(tc_err.TypeMismatchError):
        ATC.type_check(env, prog)


def test_affine_variables():

    # An affine value can be used once
    prog = dsl_parse("((defvar x (aff val int) 3) x)")
    env = base_tcheck_env()
    ret_type = ATC.type_check(env, prog)
    assert dslT.Tmod.less_restrictive(lang.T_INT.tmod, ret_type.tmod)

    # ...but not twice
    prog = dsl_parse("((defvar x (aff val int) 3) x x)")
    env = base_tcheck_env()
    with pytest.raises(tc_err.LinAffineVariableReuseError):
        ATC.type_check(env, prog)

    # Can't circumvent this through use of variables either...
    prog = dsl_parse("((defvar x (aff val int) 3) (defvar y (aff val int) x) x)")
    env = base_tcheck_env()
    with pytest.raises(tc_err.LinAffineVariableReuseError):
        ATC.type_check(env, prog)


def test_linear_variables():
    ################
    # Linear stuff #
    ################

    # Linear variables must be used *exactly* once, so just declaring it won't work
    prog = dsl_parse("((defvar x (lin val int) 3))")
    env = base_tcheck_env()
    with pytest.raises(tc_err.UnusedLinVariableError):
        # We have to make sure that the type-checker knows top-level environment will be descoped
        ATC.type_check(env, prog, descope=True)

    # But declaring and then using it actually will
    prog = dsl_parse("((defvar x (lin val int) 3) (apply + 42 x))")
    env = base_tcheck_env()
    ATC.type_check(env, prog, descope=True)

    # Declaring and then using it twice, on the other hand, is a big no-no
    prog = dsl_parse("((defvar x (lin val int) 3) (apply + 42 x) (apply + 42 x))")
    env = base_tcheck_env()
    with pytest.raises(tc_err.LinAffineVariableReuseError):
        ATC.type_check(env, prog, descope=True)


def test_function_typechecking_correct_args():
    prog = dsl_parse("(apply + 3 3)")
    ret_type = ATC.type_check(base_tcheck_env(), prog)
    assert ret_type == lang.T_INT


def test_plus_type_checks_incorrect_args():
    prog = dsl_parse("(apply + true 3)")
    with pytest.raises(tc_err.TypeMismatchError):
        ATC.type_check(base_tcheck_env(), prog)


def test_variables_redeclare():
    with pytest.raises(tc_err.BindingRedefinitionError):
        prog = dsl_parse("((defvar x (un val int) 3) (defvar x (un val int) 3) )")
        ATC.type_check(base_tcheck_env(), prog)


def test_decl_var1():
    prog = dsl_parse("((defvar x (un val int) 3) (defvar y (un val int) 3) )")
    ATC.type_check(base_tcheck_env(), prog)


def test_decl_var2():
    prog = dsl_parse("((defvar x (un val int) 3) (set x 3))")
    t = ATC.type_check(base_tcheck_env(), prog)
    assert t == lang.T_UNIT


def test_decl_var3():
    # TODO Should we be able to set multiple values like this?
    prog = dsl_parse("((defvar x (un val int) 3) (set x 3) (set x 4))")
    t = ATC.type_check(base_tcheck_env(), prog)
    assert t == lang.T_UNIT
    # assert ctx['x'] == lang.tparse(parse("(aff ref (un val int))"))


def test_decl_var4():
    # TODO Do we need to care about this?
    prog = dsl_parse("((defvar x (un val int) 3) (set x 3) (set x (+ x 1)))")
    t = ATC.type_check(base_tcheck_env(), prog)
    assert t == lang.T_UNIT
    # assert ctx['x'] == tparse(parse("(aff ref (un val int))"))


def test_unused_linint_errs():
    # TODO Do we need to care about this?
    prog = dsl_parse("(defvar x (lin val int) 3)")
    with pytest.raises(tc_err.UnusedLinVariableError):
        ATC.type_check(base_tcheck_env(), prog, descope=True)


def test_unused_affint_fine():
    # TODO Do we need to care about this?
    prog = dsl_parse("(defvar x (aff val int) 3)")
    ATC.type_check(base_tcheck_env(), prog, descope=True)


def test_oneuse_affint_fine():
    # TODO Do we need to care about this?
    prog = dsl_parse("((defvar x (aff val int) 3) x)")
    ATC.type_check(base_tcheck_env(), prog, descope=True)


def test_twouse_affint_errs():
    # TODO Do we need to care about this?
    prog = dsl_parse("((defvar x (aff val int) 3) x x)")
    with pytest.raises(tc_err.LinAffineVariableReuseError):
        ATC.type_check(base_tcheck_env(), prog, descope=True)


def test_if1():
    prog = dsl_parse("(if true (defvar x (un val int) 3) x)")
    with pytest.raises(tc_err.BindingUndefinedError):
        ATC.type_check(base_tcheck_env(), prog, descope=True)


def test_if2():
    prog = dsl_parse("((defvar x (un val int) 3) (if true (set x (apply + x 1)) (set x (apply - x 1))))")
    ATC.type_check(base_tcheck_env(), prog, descope=True)


def test_if_lin():
    prog = dsl_parse("((defvar x (lin val int) 3) (if true (set x (apply + x 1)) (set x (apply + x 0))) (apply + x 1))")
    ATC.type_check(base_tcheck_env(), prog, descope=True)


def test_if_lin2():
    prog = dsl_parse("((defvar x (lin val int) 3) (if true ((apply + x 1) (apply + x 1)) (apply + x 2)))")
    with pytest.raises(tc_err.LinAffineVariableReuseError):
        ATC.type_check(base_tcheck_env(), prog)


def test_if_lin3():
    prog = dsl_parse("((defvar x (lin val int) 3) (if true (3) (apply + x 2)))")
    with pytest.raises(tc_err.EnvironmentMismatchError):
        ATC.type_check(base_tcheck_env(), prog)


def test_while():
    prog = dsl_parse("((defvar x (un val int) 0) (while (apply < x 3) -2 ((set x (apply + x 1)) x)))")
    ATC.type_check(base_tcheck_env(), prog, descope=False)


def test_ref_fun():
    prog = dsl_parse("((defvar x (un val int) 3) (defun (foo un int) ((x un ref)) (apply + x 1)) x)")
    ATC.type_check(base_tcheck_env(), prog)
