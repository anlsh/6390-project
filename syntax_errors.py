class UndefinedVariableError(Exception):
    pass


class RedefiningVariableError(Exception):
    pass


class UndefinedTypeError(Exception):
    pass


class RedefiningTypeError(Exception):
    pass


class DeallocatedEnvironmentError(Exception):
    pass


class DeallocatedVariableError(Exception):
    pass

class TypeRedefinitionError(Exception):
    pass