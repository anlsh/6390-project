from enum import Enum
from typing import List, Union, Tuple


class Tmod(Enum):
    un = "un"
    lin = "lin"
    aff = "aff"

    @classmethod
    def restriction_hierarchy(cls, ) -> List:
        """
        A appearing before B in the hierarchy means that A is less restrictive than B
        :return:
        """
        return [cls.un, cls.aff, cls.lin]

    @classmethod
    def less_restrictive(cls, a, b) -> bool:
        return cls.restriction_hierarchy().index(a) <= cls.restriction_hierarchy().index(b)


class Tcat(Enum):
    val = 'val'
    fun = 'fun'
    ref = 'ref'


class Town(Enum):
    own = 'own'
    borrow = 'borrow'


class Type:
    def __init__(self, *,
                 category, mod, args):
        self._mod = mod
        self._type_args = args
        self._category = category

        self._ownership = Town.own

    def __eq__(self, other):
        assert isinstance(other, Type)
        return (self._mod == other._mod) and (self._category == other._category) \
            and (self._type_args == other._type_args) and (self._ownership == other._ownership)

    def set_borrow(self,):
        if self._ownership == Town.borrow:
            raise RuntimeError("Attempting to borrow from a borrowed value!")
        self._ownership = Town.borrow

    def set_own(self,):
        self._ownership = Town.own

    def is_borrow(self,) -> bool:
        return self._ownership == Town.borrow

    def is_own(self,) -> bool:
        return not self.is_borrow()

    def is_val(self, ) -> bool:
        return self._category == Tcat.val

    def is_fun(self, ) -> bool:
        return self._category == Tcat.fun

    def is_ref(self, ) -> bool:
        return self._category == Tcat.ref

    @property
    def tmod(self, ):
        return self._mod

    def is_lin(self, ) -> bool:
        return self.tmod == Tmod.lin

    def is_aff(self, ) -> bool:
        return self.tmod == Tmod.aff

    def is_un(self, ) -> bool:
        return self.tmod == Tmod.un

    @classmethod
    def is_subtype(cls, t1, t2):

        if isinstance(t1, str) or isinstance(t2, str):
            return t1 == t2

        assert isinstance(t1, Type)
        assert isinstance(t2, Type)

        if not Tmod.less_restrictive(t1.tmod, t2.tmod):
            return False

        elif t1._category != t2._category:
            return False

        elif t1.is_fun():
            self_ret_t, self_args_t = t1._type_args
            other_ret_t, other_args_t = t2._type_args

            if not cls.is_subtype(self_ret_t, other_ret_t):
                return False

            assert (len(self_args_t) == len(other_args_t))
            for s_arg_t, o_arg_t in zip(self_args_t, other_args_t):
                if not cls.is_subtype(o_arg_t, s_arg_t):
                    return False

            return True

        elif t1.is_ref():
            return cls.is_subtype(t1._type_args, t2._type_args) \
                   and cls.is_subtype(t2._type_args, t1._type_args)

        elif t1.is_val():
            return cls.is_subtype(t1._type_args, t2._type_args)


class FunType(Type):
    def __init__(self, mod: Tmod, retT: Type, argTs):
        super().__init__(category=Tcat.fun, mod=mod, args=(retT, argTs))

    @property
    def retT(self,) -> Type:
        return self._type_args[0]

    @property
    def argTs(self) -> Tuple[Type]:
        return self._type_args[1]


class ValType(Type):
    def __init__(self, mod: Tmod, tname):
        super().__init__(mod=mod, category=Tcat.val, args=tname)


class RefType(Type):
    def __init__(self, mod: Tmod, ref_type: Type):
        super().__init__(mod=mod, category=Tcat.ref, args=ref_type)

    def referenced_type(self,) -> Type:
        return self._type_args


def tparse(type_prog: Union[str, Tuple]) -> Union[Type, str]:
    """
    Given a program tree generated via the CFG defined in language spec, create the corresponding Type object
    """

    if isinstance(type_prog, str):
        return type_prog

    modstr, enumstr, args = type_prog
    mod, enum = Tmod[modstr], Tcat[enumstr]

    if enum == Tcat.fun:
        ret_tprog, arg_tprog_ls = args
        ret_t = tparse(ret_tprog)
        arg_t_ls = tuple(tparse(a) for a in arg_tprog_ls)

        return FunType(mod=mod, retT=ret_t, argTs=arg_t_ls)
    elif enum == Tcat.ref:
        return RefType(mod=mod, ref_type=tparse(args))
    elif enum == Tcat.val:
        return ValType(mod=mod, tname=tparse(args))
    else:
        raise RuntimeError(f"Unrecognized type code {enum}: Should be one of (ref, fun, val)")
