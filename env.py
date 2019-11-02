from syntax_errors import *
from typing import Any
from typing import Tuple


class BindingUndefinedError(Exception):
    pass


class BindingRedefinitionError(Exception):
    pass


class Env:

    """
    Class for mapping binds to values, creating binds, and all that jazz. Type checker will map them to types, and
    the interpreter will map them to actual values.
    """

    def __init__(self, outer=None):
        self.bindings = {}
        self.outer = outer

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
