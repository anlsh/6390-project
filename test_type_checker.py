import pytest
from interpreter import evaluate
from our_parser import parse
from type_checker import *
import operator as op


def test_type_checking_functions():
    prog = parse("( (defun (add-3 un int) ((x un int)) (+ x 3))  (add-3 7.2) )")
    with pytest.raises(FunctionArgumentTypeError):
        evaluate(prog)

    prog = parse("( (defun (add-3 un int) ((x un int)) (+ x 3.2))  (add-3 7) )")
    with pytest.raises(FunctionReturnTypeError):
        evaluate(prog)

    prog = parse("((deftype fancy_int) "
                 "(defun (add-3 un int) ((x un fancy_int)) (+ x 3))  "
                 "(add-3 3) )")
    with pytest.raises(FunctionArgumentTypeError):
        evaluate(prog)

    prog = parse("((deftype fancy_int) "
                 "(defvar y un fancy_int) "
                 "(set y 3) "
                 "(defun (add-3 un int) ((x un int)) (+ x 3))  "
                 "(add-3 y) )")
    with pytest.raises(FunctionArgumentTypeError):
        evaluate(prog)

    prog = parse("((deftype fancy_int) "
                 "(defvar y un fancy_int) "
                 "(set y 3) "
                 "(defun (add-3 un int) ((x un fancy_int)) (+ x 3))  "
                 "(add-3 y) )")
    evaluate(prog)
