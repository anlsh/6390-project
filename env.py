from typing import Any
from typing import Tuple
from dsl_types import Type
from typecheck_errors import BindingRedefinitionError, BindingUndefinedError
from copy import deepcopy
from typing import Union


class Env:

    """
    Class for mapping binds to values, creating binds, and all that jazz. Type checker will map them to types, and
    the interpreter will map them to actual values.
    """

    def __init__(self, *, defaults=None, outer=None):

        if outer is not None:
            assert isinstance(outer, Env)

        self.bindings = {}
        self.outer = outer
        for k in (defaults or []):
            self.define_bind(k, defaults[k])

    def __eq__(self, other):
        if self.outer != other.outer:
            return False

        for k in self.bindings:
            self_val, self_def_env = self.bindings[k]
            other_val, other_def_env = other.bindings[k]

            if self_def_env is self:
                if other_def_env is not other:
                    return False
            else:
                if (self_val, self_def_env) != (other_val, other_def_env):
                    return False

        return True

    def __hash__(self):
        return id(self)

    def contains_bind(self, name: str) -> bool:
        """
        Check if the current env or any of its parents have a binding for name
        :param name:
        :return:
        """
        if name in self.bindings:
            return True
        else:
            return (self.outer is not None) and self.outer.contains_bind(name)

    def define_bind(self, name: str, val: Any) -> None:
        """
        Create a binding with a given value, raising an error if the binding already exists
        :param name:
        :param val:
        :return:
        """
        if self.contains_bind(name):
            raise BindingRedefinitionError(f"Attempting to redefine {name}")
        self.bindings[name] = None, self
        self.set_bind_val(name, val)

    def get_toplevel_binds(self, ) -> Tuple:
        return tuple([name for name in self.bindings])

    def get_bind(self, name: str) -> Tuple[Any, Any]:
        """
        Get a tuple (val, defining_env) given the name of a binding. defining_env is either the current Env or one
        of its parents.
        :param name:
        :return:
        """
        if not self.contains_bind(name):
            raise BindingUndefinedError(f'{name} is undefined')
        else:
            if name in self.bindings:
                return self.bindings[name]
            else:
                return self.outer.get_bind(name)

    def get_bind_val(self, name: str) -> Any:
        val, defining_env = self.get_bind(name)
        return val

    def set_bind_val(self, name: str, val: Any,):
        _, defining_env = self.get_bind(name)
        defining_env.bindings[name] = val, defining_env


class TypeCheckEnv(Env):
    """
    Just a regular old environment, but with Type annotations everywhere so that Pycharm can correctly hint it
    """
    def __init__(self, defaults=None, outer=None):
        if outer is not None:
            assert isinstance(outer, TypeCheckEnv)
        super().__init__(defaults=defaults, outer=outer)

    def define_bind(self, name: str, val: Type) -> None:
        return super().define_bind(name=name, val=val)

    def get_bind(self, name: str) -> Tuple[Type, Env]:
        return super().get_bind(name=name)

    def get_bind_val(self, name: str) -> Type:
        return super().get_bind_val(name=name)

    def set_bind_val(self, name: str, val: Type,) -> None:
        return super().set_bind_val(name=name, val=val)


def deepcopy_env(env: Env,) -> Env:
    def __deepcopy_env(env: Env, *, env2copy: dict = None) -> Union[None, Env]:

        if env is None:
            return None
        elif env2copy is None:
            env2copy = {}
        elif env in env2copy:
            return env2copy[env]

        outer_copy = __deepcopy_env(env.outer, env2copy=env2copy)
        env2copy[env] = deepcopy(env)
        env2copy[env].outer = outer_copy
        env2copy[env].bindings = {}

        for k in env.bindings:
            val, def_env = env.bindings[k]
            val = deepcopy(val)
            def_env = __deepcopy_env(def_env, env2copy=env2copy)

            env2copy[env].bindings[k] = val, def_env

        return env2copy[env]

    return __deepcopy_env(env, env2copy={})
