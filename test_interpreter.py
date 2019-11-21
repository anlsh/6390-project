import pytest

from interpreter import evaluate
from dsl_parser import dsl_parse
import language as lang
from typecheck_errors import BindingUndefinedError
from env import Env


def base_env():
    return Env(defaults=lang.builtin_fn_vals)

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
                     "(apply add-3 x))")
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
                     "((defvar z (un val foobar) 10) (apply add-3 x)) "
                     "(apply add-3 (apply add-3 z)))"
                 ")")
    with pytest.raises(BindingUndefinedError):
        evaluate(base_env(), prog)

    prog = dsl_parse("(  (defvar x (aff val foobar) 0) "
                 "    (set x 1000)  "
                 "    (defun add-3 (un val int) ((x (un val int))) (apply + x 3))"
                 "    (if (apply = 3 4) "
                     "(apply add-3 x) "
                     "((defvar z (un val foobar) 10) (apply add-3 (apply add-3 z)))) z"
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


def test_ref():
    prog = dsl_parse("((defvar x (un val int) 3)"
                     "(defvar xref (un ref (un val int)) (mkref x)) "
                     "(setrefval xref (apply + (deref xref) 1))"
                     "x)")
    assert evaluate(base_env(), prog) == 4


def test_ref_fun():
    prog = dsl_parse("((defvar x (un val int) 3)"
                     "(defvar xref (un ref (un val int)) (mkref x)) "
                     "(defun foo (un val int) ((y (un ref (un val int)))) (setrefval y (apply + (deref y) 1)))"
                     "(apply foo xref)"
                     "x)")
    assert evaluate(base_env(), prog) == 4


def test_recursive_fun():
    prog = dsl_parse("("
                     "(defun fib (un val int) ((n (un val int))) "
                     "    (defvar ret (un val int) 0) "
                     "    (if (apply = 0 n) (set ret 0) "
                     "    (if (apply = 1 n) (set ret 1) "
                     "            (set ret (apply +  (apply fib (apply - n 1))  (apply fib (apply - n 2))  ))))"
                     "     ret"
                     ")"
                     "(apply fib 0))")
    assert evaluate(base_env(), prog) == 0

    prog = dsl_parse("("
                     "(defun fib (un val int) ((n (un val int))) "
                     "    (defvar ret (un val int) 0) "
                     "    (if (apply = 0 n) "
                     "         (set ret 0) "
                     "         (if (apply = 1 n) "
                     "                 (set ret 1) "
                     "                 (set ret (apply +  (apply fib (apply - n 1))  (apply fib (apply - n 2))  ))))"
                     "     ret"
                     ")"
                     "(apply fib 2))")
    assert evaluate(base_env(), prog) == 1

    prog = dsl_parse("("
                     "(defun fib (un val int) ((n (un val int))) "
                     "    (defvar ret (un val int) 0) "
                     "    (if (apply = 0 n) "
                     "         (set ret 0) "
                     "         (if (apply = 1 n) "
                     "                 (set ret 1) "
                     "                 (set ret (apply +  (apply fib (apply - n 1))  (apply fib (apply - n 2))  ))))"
                     "     ret"
                     ")"
                     "(apply fib 4))")
    assert evaluate(base_env(), prog) == 3
