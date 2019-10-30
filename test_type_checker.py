import pytest
from interpreter import evaluate
from our_parser import parse
from type_checker import *


def test_type_checking_functions():
    prog = parse("( (defun (add-3 un int) ((x un int)) (+ x 3))  (add-3 7.2) )")
    with pytest.raises(FunctionArgumentTypeError):
        evaluate(prog)

    prog = parse("( (defun (add-3 un int) ((x un int)) (+ x 3.2))  (add-3 7) )")
    with pytest.raises(FunctionReturnTypeError):
        evaluate(prog)
