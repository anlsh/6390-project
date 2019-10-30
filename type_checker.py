from env import Env


class FunctionArgumentTypeError(Exception):
    pass


class FunctionReturnTypeError(Exception):
    pass


def check_type_of_evaluated(env: Env, prog):
    if isinstance(prog, bool):
        return "bool"
    elif isinstance(prog, int):
        return "int"
    elif isinstance(prog, float):
        return "float"

    return env.get_bind_type(prog)
