class TypeMismatchError(RuntimeError):
    pass


class LinAffineVariableReuseError(RuntimeError):
    pass


class UnusedLinVariableError(RuntimeError):
    pass


class BindingUndefinedError(Exception):
    pass


class BindingRedefinitionError(Exception):
    pass


class EnvironmentMismatchError(Exception):
    pass
