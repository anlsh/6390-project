from typing import Any
from typing import Tuple
import dsl_types as dslT
import typecheck_errors as tc_err
from copy import deepcopy
from typing import Union


def _requires_allocated(f):
    def f_meth(self, *args, **kwargs):
        if not self.allocated:
            raise tc_err.DeallocatedEnvError
        return f(self, *args, **kwargs)

    return f_meth


class Env:

    """
    Class for mapping binds to values, creating binds, and all that jazz. Type checker will map them to types, and
    the interpreter will map them to actual values.
    """

    def __init__(self, *, defaults=None, outer=None):

        if outer is not None:
            assert isinstance(outer, Env)

        self.bindings = {}
        self.functions = {}
        self.outer = outer
        self.allocated = True
        for k in (defaults or []):
            self.define_fun(k, defaults[k])

    def __eq__(self, other):

        if not isinstance(other, Env):
            return False

        if self.outer != other.outer:
            return False
        elif self.allocated != other.allocated:
            return False

        for k in self.bindings:
            self_val, self_def_env = self.bindings[k]
            other_val, other_def_env = other.bindings[k]

            if self_def_env is self:
                if other_def_env is not other:
                    return False
                if self_val != other_val:
                    return False
            else:
                if (self_val, self_def_env) != (other_val, other_def_env):
                    return False

        return True

    def __hash__(self):
        return id(self)

    @_requires_allocated
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

    @_requires_allocated
    def contains_fun(self, name: str) -> bool:
        if name in self.functions.keys():
            return True
        else:
            return (self.outer is not None) and self.outer.contains_fun(name)

    @_requires_allocated
    def define_bind(self, name: str, val: Any) -> None:
        """
        Create a binding with a given value, raising an error if the binding already exists
        :param name:
        :param val:
        :return:
        """
        if self.contains_bind(name):
            raise tc_err.BindingRedefinitionError(f"Attempting to redefine {name}")
        self.bindings[name] = None, self
        self.set_bind_val(name, val)

    @_requires_allocated
    def define_fun(self, name: str, val: Any) -> None:
        if self.contains_fun(name):
            raise tc_err.BindingRedefinitionError(f"Attempting to redefine {name}")
        self.functions[name] = val

    @_requires_allocated
    def get_toplevel_binds(self, ) -> Tuple:
        return tuple([name for name in self.bindings])

    @_requires_allocated
    def get_bind(self, name: str) -> Tuple[Any, Any]:
        """
        Get a tuple (val, defining_env) given the name of a binding. defining_env is either the current Env or one
        of its parents.
        :param name:
        :return:
        """
        if not self.contains_bind(name):
            raise tc_err.BindingUndefinedError(f'{name} is undefined')
        else:
            if name in self.bindings:
                return self.bindings[name]
            else:
                return self.outer.get_bind(name)

    @_requires_allocated
    def get_fun_def(self, name: str) -> Any:
        if not self.contains_fun(name):
            raise tc_err.BindingUndefinedError(f'{name} is undefined')
        else:
            if name in self.functions:
                return self.functions[name]
            else:
                return self.outer.get_fun_def(name)

    @_requires_allocated
    def get_bind_val(self, name: str) -> Any:
        val, defining_env = self.get_bind(name)
        return val

    @_requires_allocated
    def set_bind_val(self, name: str, val: Any,):
        _, defining_env = self.get_bind(name)
        defining_env.bindings[name] = val, defining_env

    @_requires_allocated
    def deallocate(self,):
        for name in self.bindings:
            val, defining_env = self.get_bind(name)
            if isinstance(val, dslT.RefType) and val.is_own() :
                original_binding_type = defining_env.get_bind_val(name)
                if original_binding_type.is_borrow():
                    original_binding_type.set_own()
                else:
                    raise tc_err.DestructiveReturnOfOwnership("Reference to variable is returning ownership at a point"
                                                              "when original variable again owns an object: this would"
                                                              "clobber current value of variable.")
        self.allocated = False


class TypeCheckEnv(Env):
    """
    Just a regular old environment, but with Type annotations everywhere so that Pycharm can correctly hint it
    """
    def __init__(self, defaults=None, outer=None):
        if outer is not None:
            assert isinstance(outer, TypeCheckEnv)
        super().__init__(defaults=defaults, outer=outer)

    def deallocate(self,):

        ######################################
        # Check for unused linear judgements #
        ######################################

        refs = tuple(filter(lambda name: isinstance(self.get_bind_val(name), dslT.RefType),
                      self.get_toplevel_binds()))
        for _ in range(len(refs)):
            for refname in refs:
                t = self.get_bind_val(refname)
                assert isinstance(t, dslT.RefType)
                if t.is_own():
                    t.return_reference()

        for name in self.get_toplevel_binds():
            name_t = self.get_bind_val(name)
            if name_t.is_lin() and name_t.is_own():
                raise tc_err.UnusedLinVariableError

        ##############################################
        # Make sure to call superclass to deallocate #
        ##############################################

        super().deallocate()

    def define_bind(self, name: str, val: dslT.Type) -> None:
        return super().define_bind(name=name, val=val)

    def get_bind(self, name: str) -> Tuple[dslT.Type, Env]:
        return super().get_bind(name=name)

    def get_bind_val(self, name: str) -> dslT.Type:
        return super().get_bind_val(name=name)

    def set_bind_val(self, name: str, val: dslT.Type,) -> None:
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
