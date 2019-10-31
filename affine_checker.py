# We represent a context as a hash map...
from copy import deepcopy as copy
from language import *
from typing import Tuple


class TypeMismatchError(RuntimeError):
    pass


class VariableRedefinitionError(RuntimeError):
    pass


class UndeclaredVariableError(RuntimeError):
    pass


class LinAffineVariableReuseError(RuntimeError):
    pass


class Type:
    def __init__(self, mod, type_enum, type_args):
        self.mod = mod
        self.type_enum = type_enum
        self.type_args = type_args

        if self.mod not in type_mods:
            raise RuntimeError(f"Unrecognized type {self.mod}")
        elif self.type_enum not in type_enum:
            raise RuntimeError(f'Unrecognized type {self.type_enum}')

        # TODO Perform checking on type_args!

    def __eq__(self, other):
        return (self.mod == other.mod) and (self.type_enum == other.type_enum) and (self.type_args == other.type_args)


T_NIL = Type(mod_un, en_o, 'nil')
T_UNIT = Type(mod_un, en_o, 'unit')
T_BOOL = Type(mod_un, en_o, 'bool')
T_INT = Type(mod_un, en_o, 'int')


def parse_type(type_prog):
    mod, enum, args = type_prog
    if enum == en_fun:
        ret_type, arg_types = args
        parsed_arg_types = tuple(parse_type(a) for a in arg_types)
        return Type(mod, enum, (Type(*ret_type), parsed_arg_types))
    elif enum == en_ref:
        return Type(mod, enum, parse_type(args))
    elif enum == en_o:
        return Type(mod, enum, args)
    else:
        raise RuntimeError("Unrecognized type code!")

base_context = {
    "+": parse_type((mod_un, en_fun, ( (mod_un, en_o, 'int'),  ((mod_un, en_o, 'int'), (mod_un, en_o, 'int'))  )  )),
    "not": parse_type((mod_un, en_fun, ( (mod_un, en_o, 'bool'),  ((mod_un, en_o, 'bool'),) )))
}


def subtype(t1, t2):
    # TODO We should be able to use this to say that affine<T> is subtype of un<T>
    return t1 == t2


def type_check(context: dict, prog) -> Tuple[dict, Type]:

    """
    Given a context Gamma and program tree, type-check it (modifying gamma along the way)
    :param context:
    :param prog:
    :return:
    """
    context = copy(context)

    if not (isinstance(context, tuple)):

        try:
            int(prog)
            return context, T_INT
        except Exception:
            pass

        if prog in ['false', 'true']:
            return context, T_BOOL

        if prog in context:
            if context[prog] is None:
                raise LinAffineVariableReuseError(f'Duplicate use of {prog}')

            T = context.pop(prog)
            if T.mod == 'un':
                context[prog] = T
            else:
                context[prog] = None

            return context, T

    if len(prog) == 0:
        return context, T_NIL

    elif prog[0] == "defvar":
        _, vname, vtype, vdef = prog

        vtype = parse_type(vtype)
        context, deftype = type_check(context, vdef)

        if vname in context:
            raise VariableRedefinitionError

        if not subtype(vtype, deftype):
            raise TypeMismatchError
        else:
            # TODO Is setting the variable name to be a reference the correct thing to do?
            # TODO Moreover, should the reference be affine?
            context[vname] = Type(mod_aff, en_ref, vtype)
            return context, T_UNIT

    elif prog[0] == "defun":
        _, fname, ftmod, rT_spec, argspec = prog[:4]
        body = prog[4:]

        rettype = parse_type(rT_spec)

        empty_context = copy(base_context)
        argument_types = []
        for arg, argT in argspec:
            argT = parse_type(argT)
            empty_context[arg] = parse_type(argT)
            argument_types.append(argT)
            # TODO What to do with final context? I don't actually know if we need to do anything, as the "sequential
            # evaluation" case might take care of most of it if implemented as below.
        final_context, actually_returned_type = type_check(empty_context, body)
        argument_types = tuple(argument_types)

        # TODO This is one of the two places where an explicit check for affine and linear types has to go, I'm p sure
        # The other is in the sequential evaluation part. Both correspond to variables being descoped.

        if not (rettype == actually_returned_type):
            raise TypeMismatchError(f'{prog} returns the wrong type!')

        if fname in context:
            raise VariableRedefinitionError
        else:
            context[fname] = Type(ftmod, en_fun, (rettype, argument_types))
            return context, T_UNIT

    elif prog[0] == "ref":
        _, referenced_thing = prog
        context, thing_type = type_check(context, referenced_thing)
        # TODO What should references be? Affine? I think they can be unrestricted as long as they're immutable, and
        # we should only be able to call set on a mutable reference (pretty sure that will give us the behavior we want)
        return context, Type(mod_aff, en_ref, thing_type)

    elif prog[0] == "dref":
        _, thing = prog
        context, thing_type = type_check(context, thing)
        if thing_type.type_enum != en_ref:
            raise RuntimeError("Attempted to dereference something that's not a reference!")
        return context, thing_type.type_args

    elif prog[0] == "set":
        _, target_loc, new_def = prog
        # TODO The evaluation order is very important (might require deep consideration). Consider (set x (apply + x 1))
        context, target_loc_type = type_check(context, target_loc)
        context, def_type = type_check(context, new_def)
        if target_loc_type.type_enum != en_ref:
            raise RuntimeError("Attempting to set a non-reference!")
        elif not subtype(def_type, def_type.type_args):
            raise TypeMismatchError("Attempting to set to the wrong thing!")

        # TODO I'm not sure what to do here... It's getting a bit late :<
        # I think I need to manually add the statement that target_loc: def_type back in

        return context, T_UNIT

    elif prog[0] == "apply":
        _, fname = prog[:2]
        fargs = prog[2:]

        context, fsignature = type_check(context, fname)

        argument_types = []
        for arg in fargs:
            context, atype = type_check(context, arg)
            argument_types.append(atype)

        if len(argument_types) != len(fsignature.type_args[1]):
            raise RuntimeError("Didn't pass in right number of arguments!")
        for i in range(len(argument_types)):
            if not subtype(argument_types[i], fsignature.type_args[1][i]):
                raise TypeMismatchError(f'Argument {i} expected to be {fsignature.type_args[1][i]}, got {argument_types[i]}')

        return context, fsignature.type_args[0]

    else:
        ret_type = None
        for p in prog:
            context, ret_type = type_check(context, p)

        return context, ret_type
