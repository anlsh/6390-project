from syntax_errors import *
from typing import Tuple

UNIT = "unit-type-repr"


class Environment:

    i_type = 0
    i_val = 1
    i_wasset = 2

    def __init__(self, outer=None):
        # Bindings maps a name to a 3-tuple (type, value,)
        self.bindings = {}
        self.types = set()
        self.allocated = True
        self.outer = outer

    def contains_bind(self, name):
        if name in self.bindings:
            return True
        else:
            return (self.outer is not None) and self.outer.contains_bind(name)

    def contains_type(self, name):
        if name in self.bindings:
            return True
        else:
            return (self.outer is not None) and self.outer.contains_type(name)

    def define_type(self, base_name):
        if not self.allocated:
            raise DeallocatedEnvironmentError
        elif self.contains_type(base_name):
            raise TypeRedefinitionError(f'Attempting to redefine type {base_name}')
        else:
            self.types.add(base_name)

    def define_bind(self, name, type):
        if self.contains_bind(name):
            raise BindingRedefinitionError(f"Attempting to redefine {name}")
        self.bindings[name] = None
        self.set_bind_val(name, None, bind_type=type)

    def get_bind(self, name):
        if not self.allocated:
            raise DeallocatedEnvironmentError()
        elif not self.contains_bind(name):
            raise VariableUndefinedError
        else:
            if name in self.bindings:
                return self.bindings[name], self

    def get_bind_type(self, name):
        vinfo, defining_env = self.get_bind(name)
        return vinfo[Environment.i_type]

    def get_bind_val(self, name):
        vinfo, defining_env = self.get_bind(name)
        if not vinfo[Environment.i_wasset]:
            raise VariableUnsetAccessError()

        return vinfo[Environment.i_val]

    def get_bind_wasset(self, name):
        vinfo, defining_env = self.get_bind(name)
        return vinfo[Environment.i_wasset]

    def set_bind_val(self, name, val, bind_type=None):
        vinfo, defining_env = self.get_bind(name)

        if bind_type is None:
            curr_vtype, _ = vinfo
        else:
            curr_vtype = bind_type

        defining_env.bindings[name] = (curr_vtype, val, True), self

    def deallocate(self):
        print("Base environment de-allocated")
        self.allocated = False


def eval(env: Environment, code_tree):
    return None, None


def eval_if(env: Environment, when_c, then_c, else_c, ):
    """
    Take in when, then, and else ASTs and execute the if statement
    """
    when_result = eval(env, when_c)
    inner_env = Environment(env)
    if when_result:
        eval(inner_env, then_c)
    else:
        eval(inner_env, else_c)
    inner_env.deallocate()
    return UNIT


class Function_Evaluator:
    def __init__(self, argnames, fn_body):
        self.


def eval_defun(env: Environment, fun_name, fun_rettype_spec, fun_args_typespec_list, *fun_body):
    # TODO Have to evaluate this
    env.define_bind(fun_name, )


def eval_while(env: Environment, test_c, body_c):

    inner_env = Environment(env)
    while True:
        test_result = eval(env, test_c)
        if test_result:
             eval(inner_env, body_c)
        else:
            return UNIT


def eval_defvar(env: Environment, var_name, type_mod, base_type):
    env.define_bind(var_name, type_mod, base_type)
    return UNIT


def eval_set(env: Environment, var_name, val):
    env.set_bind_val(var_name, val)
    return val


def eval_mut_ref(env: Environment, var_name):
    # TODO
    raise NotImplementedError


def eval_ref(env: Environment, var_name):
    # TODO
    raise NotImplementedError


def eval_deftype(env: Environment, base_type):
    env.define_type(base_type)
    return base_type


