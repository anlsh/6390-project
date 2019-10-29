from syntax_errors import *

UNIT = "unit-type-repr"


class BaseEnvironment:

    i_type = 0
    i_val = 1
    i_alloc = 2

    def __init__(self):
        # Bindings maps a name to a 3-tuple (type, value, allocated)
        self.bindings = {}
        self.types = set()
        self.allocated = True

    def define_type(self, base_name):
        if not self.allocated:
            raise DeallocatedEnvironmentError
        elif self.contains_type(base_name):
            raise TypeRedefinitionError(f'Attempting to redefine type {base_name}')
        else:
            self.types.add(base_name)

    def define_bind(self, name, type):
        if self.contains_bind(name):
            raise RedefiningVariableError(f"Attempting to redefine {name}")
        self.set_bind_val(name, type, raw_alloc=True, bind_type=type)

    def set_bind_val(self, name, val, raw_alloc=False, bind_type=None):
        """
        Set a variable in the environment
        """
        if not self.allocated:
            raise DeallocatedEnvironmentError
        elif self.contains_bind(name):
            raise UndefinedVariableError
        elif (not raw_alloc) and (not self.bindings[name][BaseEnvironment.i_alloc]):
            raise DeallocatedVariableError
        else:
            bind_type = bind_type if raw_alloc else self.bindings[name][BaseEnvironment.i_type]
            self.bindings[name] = (name, bind_type, val, not raw_alloc,)

    def get_bind(self, name):
        """
        Get the value of variable in the environment, checking to make sure that it exists first
        :param name:
        :param value:
        :return:
        """
        if not self.allocated:
            raise DeallocatedEnvironmentError
        elif self.contains_bind(name):
            raise UndefinedVariableError
        elif not self.bindings[name][BaseEnvironment.i_alloc]:
            raise DeallocatedVariableError
        else:
            return self.bindings[name]

    def contains_bind(self, name):
        return name in self.bindings

    def contains_type(self, name):
        return name in self.types

    def deallocate(self):
        print("Base environment de-allocated")
        pass


class DerivedEnvironment(BaseEnvironment):

    def __init__(self, outer: BaseEnvironment):
        super().__init__()
        self.outer = outer

    def contains_bind(self, name):
        return (name in self.bindings) or self.outer.contains_bind(name)

    def contains_type(self, name):
        return (name in self.bindings) or self.outer.contains_type(name)

    def set_bind_val(self, name, val, raw_alloc=False, bind_type=None):
        if not self.contains_bind(name):
            raise UndefinedVariableError(f"Cannot set undefined variable {name}")
        if name in self.bindings:
            bind_type = bind_type if raw_alloc else self.bindings[name][BaseEnvironment.i_type]
            self.bindings[name] = (name, bind_type, val, not raw_alloc,)
        else:
            self.outer.set_bind_val(name, val)

    def get_bind(self, name):
        if not self.contains_bind(name):
            raise UndefinedVariableError(f"Cannot access undefined variable {name}")

        if name in self.bindings:
            return self.bindings[name]
        else:
            return self.outer.get_bind(name)


def eval(env: BaseEnvironment, code_tree):
    return None, None


def eval_if(env: BaseEnvironment, when_c, then_c, else_c,):
    """
    Take in when, then, and else ASTs and execute the if statement
    """
    when_result = eval(env, when_c)
    inner_env = DerivedEnvironment(env)
    ret = None
    if when_result:
        eval(inner_env, then_c)
    else:
        eval(inner_env, else_c)
    inner_env.deallocate()
    return UNIT


def eval_defun(env: BaseEnvironment, fun_name, fun_rettype_spec, fun_args_typespec_list, *fun_body):
    # TODO Have to evaluate this
    env.define_bind(fun_name, )


def eval_while(env: BaseEnvironment, test_c, body_c):

    inner_env = DerivedEnvironment(env)
    while True:
        test_result = eval(env, test_c)
        if test_result:
             eval(inner_env, body_c)
        else:
            return UNIT


def eval_defvar(env: BaseEnvironment, var_name, type_mod, base_type):
    env.define_bind(var_name, type_mod, base_type)
    return UNIT


def eval_set(env: BaseEnvironment, var_name, val):
    env.set_bind_val(var_name, val)
    return val


def eval_mut_ref(env: BaseEnvironment, var_name):
    raise NotImplementedError


def eval_ref(env: BaseEnvironment, var_name):
    raise NotImplementedError


def eval_deftype(env: BaseEnvironment, base_type):
    env.define_type(base_type)
    return base_type


