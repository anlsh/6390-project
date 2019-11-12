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


class BorrowedValueUseError(RuntimeError):
    pass


class DeallocatedEnvError(RuntimeError):
    pass


class ReferenceNoEffectError(RuntimeError):
    pass


class DestructiveReturnOfOwnership(RuntimeError):
    pass
