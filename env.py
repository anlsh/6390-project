from typing import Any
from typing import Tuple
from dsl_types import Type


class BindingUndefinedError(Exception):
    pass


class BindingRedefinitionError(Exception):
    pass


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
            raise BindingUndefinedError
        else:
            if name in self.bindings:
                return self.bindings[name]
            else:
                return self.outer.get_bind(name)

    def get_bind_val(self, name: str) -> Any:
        val, defining_env = self.get_bind(name)
        return val

    def set_bind_val(self, name: str, val: Any,) -> None:
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
        return super().get_bind_val(name=name)

    def get_bind_val(self, name: str) -> Type:
        return super().get_bind_val(name=name)

    def set_bind_val(self, name: str, val: Type,) -> None:
        return super().set_bind_val(name=name, val=val)