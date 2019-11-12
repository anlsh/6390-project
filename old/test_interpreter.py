import pytest

from old.interpreter import evaluate
from dsl_parser import dsl_parse
import language as lang
from typecheck_errors import BindingUndefinedError
from env import Env


def base_env():
    return Env(outer=Env(defaults=lang.builtin_fn_vals))

# TODO Raise error if variable not initialized? Currently raises TypeError
def test_define_variable():
    prog = dsl_parse("(defvar x (un val footype) 3)")
    assert evaluate(base_env(), prog) == lang.T_UNIT


def test_var_access():
    prog = dsl_parse("( (defvar x (lin val footype) 0) (set x 3)  x )")
    assert evaluate(base_env(), prog) == 3

    prog = dsl_parse("( (defvar x (aff val footype) 0) (set x 4) (set x 3) 3)")
    assert evaluate(base_env(), prog) == 3


def test_calling_functions():
    prog = dsl_parse("(apply + 3 4)")
    assert evaluate(base_env(), prog) == 7

    prog = dsl_parse("(apply <= 5 4)")
    assert evaluate(base_env(), prog) == False


def test_defining_functions():
    prog = dsl_parse("( (defun add-3 (un val int) ((x (un val int))) (apply + x 3))  (apply add-3 7) )")
    assert evaluate(base_env(), prog) == 10

    prog = dsl_parse("( (defvar x (un val foobar) 0) "
                     "(set x 1000) "
                     "(defun add-3 (un val int) ((x (un val int))) (apply + x 3))"
                     "(apply add-3 7))")
    assert evaluate(base_env(), prog) == 10

    prog = dsl_parse("( (defvar x (un val foobar) 0) "
                     "(set x 1000) "
                     "(defun add-3 (un val int) ((x (un val int))) (apply + x 3))"
                     "(apply add-3 7) x)")
    assert evaluate(base_env(), prog) == 1000

    prog = dsl_parse("( (defvar x (un val foobar) 0) "
                     "(set x 1000) "
                     "(defun add-3 (un val int) ((x (un val int))) (apply + x 3))"
                     "(add-3 x))")
    assert evaluate(base_env(), prog) == 1003

    prog = dsl_parse("( (defun add-3 (un val int) ((x (un val int))) (apply + x 3))  "
                     "(defun add-4 (un val int) ((x (un val int))) (apply add-3 (apply + x 1)))"
                     "(apply add-4 6) )")
    assert evaluate(base_env(), prog) == 10


def test_if_statement():
    prog = dsl_parse("( if true 10 12 )")
    assert evaluate(base_env(), prog) == 10

    prog = dsl_parse("(  (defvar x (un val foobar) 0) "
                 "    (set x 1000)  "
                 "    (defun add-3 (un val int) ((x (un val int))) (apply + x 3))"
                 "    (if (apply = 3 3) (apply add-3 x) (apply add-3 (apply add-3 x)))"
                 ")")
    assert evaluate(base_env(), prog) == 1003

    prog = dsl_parse("(  (defvar x (un val foobar) 0) "
                 "    (set x 1000)  "
                 "    (defun add-3 (un val int) ((x (un val int))) (apply + x 3))"
                 "    (if (apply = 3 4) (apply add-3 x) (apply add-3 (apply add-3 x)))"
                 ")")
    assert evaluate(base_env(), prog) == 1006

    prog = dsl_parse("(  (defvar x (lin val foobar) 0) "
                 "    (set x 1000)  "
                 "    (defun add-3 (un val int) ((x (un val int))) (apply + x 3))"
                 "    (if (apply = 3 4) "
                     "((defvar z (un val foobar)) (set z 10) (apply add-3 x)) "
                     "(apply add-3 (apply add-3 z)))"
                 ")")
    with pytest.raises(BindingUndefinedError):
        evaluate(base_env(), prog)

    prog = dsl_parse("(  (defvar x (aff val foobar) 0) "
                 "    (set x 1000)  "
                 "    (defun add-3 (un val int) ((x (un val int))) (apply + x 3))"
                 "    (if (apply = 3 4) "
                     "(apply add-3 x) "
                     "(((defvar z (un val foobar) 0) (set z 10))  (apply add-3 (apply add-3 z)))) z"
                 ")")
    with pytest.raises(BindingUndefinedError):
        evaluate(base_env(), prog)


def test_while_statement():
    prog = dsl_parse("( (defvar x (un val foobar) 0) "
                 "  (defvar y (un val foobar) 10) "
                 "  (while (apply < x 10) -2 (  (set y (apply + y 1)) (set x (apply + x 1)) y)  ))")
    assert evaluate(base_env(), prog) == 20

    prog = dsl_parse("( (defvar x (un val foobar) 0) "
                 "  (defvar y (un val foobar) 10) "
                 "  (while (apply < x -4) -2 (  (set y (apply + y 1)) (set x (apply + x 1)) y)  ))")
    assert evaluate(base_env(), prog) == -2

    prog = dsl_parse("( (defvar x (un val foobar) 0) "
                 "  (defvar y (un val foobar) 10) "
                 "  (while (apply < x -4) -2 ((defvar z (un val foobar) 10) "
                 "               (  (set y (apply + y 1)) (set x (apply + x 1)) y)  )) z)")
    with pytest.raises(BindingUndefinedError):
        evaluate(base_env(), prog)

    prog = dsl_parse("( (defvar x (un val foobar) 0) "
                 "  (defvar y (un val foobar) 10) "
                 "  (while (apply < x -4) -2 ((defvar z (un val foobar) 10) "
                 "               ( (defvar 1 (un val foobar) 10) (set y (apply + y 1)) (set x (apply + x 1)) y)  )) q)")
    with pytest.raises(BindingUndefinedError):
        evaluate(base_env(), prog)
