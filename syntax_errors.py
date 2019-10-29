class VariableUndefinedError(Exception):
    pass


class VariableUnsetAccessError(Exception):
    pass


class BindingRedefinitionError(Exception):
    pass


class TypeRedefinitionError(Exception):
    pass


class TypeUndefinedError(Exception):
    pass


class DeallocatedEnvironmentError(Exception):
    pass


class DeallocatedVariableError(Exception):
    pass
