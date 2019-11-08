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


class Toship(Enum):
    own = 'own'
    borrow = 'borrow'


class Tcat(Enum):
    val = 'val'
    fun = 'fun'
    ref = 'ref'


class Type:
    def __init__(self, *,
                 category, mod, args):
        self.__mod = mod
        self.__type_args = args
        self.__category = category

    def __eq__(self, other):
        assert isinstance(other, Type)
        return (self.__mod == other.__mod) and (self.__category == other.__category) \
               and (self.__type_args == other.__type_args)

    def is_val(self, ) -> bool:
        return self.__category == Tcat.val

    def is_fun(self, ) -> bool:
        return self.__category == Tcat.fun

    def is_ref(self, ) -> bool:
        return self.__category == Tcat.ref

    @property
    def tmod(self, ):
        return self.__mod

    def is_lin(self, ) -> bool:
        return self.tmod == Tmod.lin

    def is_aff(self, ) -> bool:
        return self.tmod == Tmod.aff

    def is_un(self, ) -> bool:
        return self.tmod == Tmod.un

    @classmethod
    def is_subtype(cls, t1, t2):

        if isinstance(t1, str) or isinstance(t2, str):
            if t1 != t2:
                return False

        assert isinstance(t1, Type)
        assert isinstance(t2, Type)

        if not Tmod.less_restrictive(t1.tmod, t2.tmod):
            return False

        elif t1.__category != t2.__category:
            return False

        elif t1.is_fun():
            self_ret_t, self_args_t = t1.__type_args
            other_ret_t, other_args_t = t2.__type_args

            if not cls.is_subtype(self_ret_t, other_ret_t):
                return False

            assert (len(self_args_t) == len(other_args_t))
            for s_arg_t, o_arg_t in zip(self_args_t, other_args_t):
                if not cls.is_subtype(o_arg_t, s_arg_t):
                    return False

            return True

        elif t1.is_ref():
            return cls.is_subtype(t1.__type_args, t2.__type_args) \
                   and cls.is_subtype(t2.__type_args, t1.__type_args)

        elif t1.is_val():
            return cls.is_subtype(t1.__type_args, t2.__type_args)


class FunType(Type):
    def __init__(self, *args, mod, retT, argTs):
        super().__init__(*args,
                         category=Tcat.fun, mod=mod,
                         args=(retT, argT_tuple))

    @property
    def retT(self,) -> Type:
        return self.__type_args[0]

    @property
    def argTs(self) -> Tuple[Type]:
        return self.__type_args[1]


class ValType(Type):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, category=Tcat.val, **kwargs)


class RefType(Type):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, category=Tcat.ref, **kwargs)


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

        return FunType(mod=mod, args=(ret_t, arg_t_ls))

    elif (enum == Tcat.ref) or (enum == Tcat.val):
        return RefType(mod=mod, args=tparse(args))
    else:
        raise RuntimeError(f"Unrecognized type code {enum}: Should be one of (ref, fun, val)")
