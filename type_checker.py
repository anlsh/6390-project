from context import *

class FunctionArgumentTypeError(Exception):
    pass


class FunctionReturnTypeError(Exception):
    pass


def check_function(fun, fun_signature):
    """
    Checks that a function's argument types and return type match the defined function signature
    :param fun:
    :param fun_signature:
    :return:
    """
    fun_name_called, args = fun[0], fun[1:]
    fun_name_spec, ret_tspec, arg_bindings, body = fun_signature[0], fun_signature[1], fun_signature[2], fun_signature[3]
    assert fun_name_called == fun_name_spec
    for arg, arg_binding in args, arg_bindings:
        received_type = contains_type(arg)
        expected_type = (arg_bindings[1], arg_bindings[2])
        if received_type != expected_type:
            raise FunctionArgumentTypeError(f"{arg_bindings[0]}: Expected {expected_type}, Received: {received_type} ")
    return_type = contains_type(fun)
    if return_type != ret_tspec:
        raise FunctionReturnTypeError(f"{fun_name_spec} does not return value of type {ret_tspec}")
