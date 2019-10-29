from syntax_errors import *
from language import *


class Env:

    i_type = 0
    i_val = 1
    i_wasset = 2

    def __init__(self, outer=None):
        # Bindings maps a name to a tuple ((type, value, wasset), defining_env)
        # TODO Have to define all the types on these!
        self.bindings = {fname: ((None, builtin_fns[fname], True), self) for fname in builtin_fns}
        self.types = set()
        self.allocated = True
        self.outer = outer

    def contains_bind(self, name):
        if name in self.bindings:
            return True
        else:
            return (self.outer is not None) and self.outer.contains_bind(name)

    def contains_type(self, name):
        if name in self.types:
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

    def define_bind(self, name, vtype):
        if self.contains_bind(name):
            raise BindingRedefinitionError(f"Attempting to redefine {name}")

        ######################################################################################################
        # Important! Make sure that this line and the one in set_bind_val are in *exact* agreement on format #
        ######################################################################################################
        self.bindings[name] = (vtype, None, False), self

    def get_bind(self, name):
        if not self.allocated:
            raise DeallocatedEnvironmentError()
        elif not self.contains_bind(name):
            raise VariableUndefinedError
        else:
            if name in self.bindings:
                return self.bindings[name]
            else:
                return self.outer.get_bind(name)

    def get_bind_type(self, name):
        vinfo, defining_env = self.get_bind(name)
        return vinfo[Env.i_type]

    def get_bind_val(self, name):
        vinfo, defining_env = self.get_bind(name)
        if not vinfo[Env.i_wasset]:
            raise VariableUnsetAccessError()

        return vinfo[Env.i_val]

    def get_bind_wasset(self, name):
        vinfo, defining_env = self.get_bind(name)
        return vinfo[Env.i_wasset]

    def set_bind_val(self, name, val,):
        vinfo, defining_env = self.get_bind(name)

        curr_vtype, _, _ = vinfo

        ######################################################################################################
        # Important! Make sure that this line and the one in define_bind_ are in *exact* agreement on format #
        ######################################################################################################
        defining_env.bindings[name] = (curr_vtype, val, True), defining_env

    def deallocate(self):
        self.allocated = False
