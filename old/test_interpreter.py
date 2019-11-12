import pytest

from old.interpreter import evaluate
from dsl_parser import dsl_parse


def test_define_variable():
    prog = dsl_parse("(defvar x un footype)")
    assert evaluate(prog) == UNIT


def test_var_access():
    prog = dsl_parse("( (defvar x lin footype) (set x 3)  x )")
    assert evaluate(prog) == 3

    prog = dsl_parse("( (defvar x aff footype) (set x 4) (set x 3) 3)")
    assert evaluate(prog) == 3


def test_calling_functions():
    prog = dsl_parse("(+ 3 4)")
    assert evaluate(prog) == 7

    prog = dsl_parse("(<= 5 4)")
    assert evaluate(prog) == False


def test_defining_functions():
    prog = dsl_parse("( (defun (add-3 un int) ((x un int)) (+ x 3))  (add-3 7) )")
    assert evaluate(prog) == 10

    prog = dsl_parse("( (defvar x un foobar) (set x 1000) (defun (add-3 un int) ((x un int)) (+ x 3))  (add-3 7) )")
    assert evaluate(prog) == 10

    prog = dsl_parse("( (defvar x fun oobar) (set x 1000) (defun (add-3 un int) ((x un int)) (+ x 3))  (add-3 7) x)")
    assert evaluate(prog) == 1000

    prog = dsl_parse("( (defvar x un foobar) (set x 1000) (defun (add-3 un int) ((x un int)) (+ x 3))  (add-3 x))")
    assert evaluate(prog) == 1003


def test_if_statement():
    prog = dsl_parse("( if true 10 12 )")
    assert evaluate(prog) == 10

    prog = dsl_parse("(  (defvar x un foobar) "
                 "    (set x 1000)  "
                 "    (defun (add-3 un int) ((x un int)) (+ x 3))"
                 "    (if (= 3 3) (add-3 x) (add-3 (add-3 x)))"
                 ")")
    assert evaluate(prog) == 1003

    prog = dsl_parse("(  (defvar x un foobar) "
                 "    (set x 1000)  "
                 "    (defun (add-3 un int) ((x un int)) (+ x 3))"
                 "    (if (= 3 4) (add-3 x) (add-3 (add-3 x)))"
                 ")")
    assert evaluate(prog) == 1006

    prog = dsl_parse("(  (defvar x lin foobar) "
                 "    (set x 1000)  "
                 "    (defun (add-3 un int) ((x un int)) (+ x 3))"
                 "    (if (= 3 4) ((defvar z un foobar) (set z 10) (add-3 x)) (add-3 (add-3 z)))"
                 ")")
    with pytest.raises(VariableUndefinedError):
        evaluate(prog)

    prog = dsl_parse("(  (defvar x aff foobar) "
                 "    (set x 1000)  "
                 "    (defun (add-3 un int) ((x un int)) (+ x 3))"
                 "    (if (= 3 4) (add-3 x) (((defvar z un foobar) (set z 10))  (add-3 (add-3 z)))) z"
                 ")")
    with pytest.raises(VariableUndefinedError):
        evaluate(prog)


def test_while_statement():
    prog = dsl_parse("( (defvar x un foobar) (set x 0) "
                 "  (defvar y un foobar) (set y 10)"
                 "  (while (< x 10) -2 (  (set y (+ y 1)) (set x (+ x 1)) y)  ))")
    assert evaluate(prog) == 20

    prog = dsl_parse("( (defvar x un foobar) (set x 0) "
                 "  (defvar y un foobar) (set y 10)"
                 "  (while (< x -4) -2 (  (set y (+ y 1)) (set x (+ x 1)) y)  ))")
    assert evaluate(prog) == -2

    prog = dsl_parse("( (defvar x un foobar) (set x 0) "
                 "  (defvar y un foobar) (set y 10)"
                 "  (while (< x -4) ((defvar z un foobar) (set z 10)) "
                 "               (  (set y (+ y 1)) (set x (+ x 1)) y)  ) z)")
    with pytest.raises(VariableUndefinedError):
        evaluate(prog)

    prog = dsl_parse("( (defvar x un foobar) (set x 0) "
                 "  (defvar y un foobar) (set y 10)"
                 "  (while (< x -4) ((defvar z un foobar) (set z 10)) "
                 "               ( (defvar 1 un foobar) (set 1 10) (set y (+ y 1)) (set x (+ x 1)) y)  ) q)")
    with pytest.raises(VariableUndefinedError):
        evaluate(prog)
