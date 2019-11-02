import language as lang
from typing import Tuple, Union

from env import Env


class TypeMismatchError(RuntimeError):
    pass


class VariableRedefinitionError(RuntimeError):
    pass


class UndeclaredVariableError(RuntimeError):
    pass


class LinAffineVariableReuseError(RuntimeError):
    pass


class AffineTypeChecker:

    @classmethod


def subtype(t1, t2):
    # TODO We should be able to use this to say that affine<T> is subtype of un<T>
    return t1 == t2


def type_check(env: Env, prog: Union[Tuple, str]) -> lang.Type:
    """
    Given a context Gamma and program tree, type-check it (modifying gamma along the way)
    :param env:
    :param prog:
    :return:
    """
    #################################################################################
    # If the program isn't a tree, then it should be an integer, string, or boolean #
    #################################################################################

    if not (isinstance(env, tuple)):

        # Check if we can interpret the program as an integer...
        try:
            int(prog)
            return lang.T_INT
        except ValueError:
            pass

        # Or if we can interpret it as a boolean
        if prog in ['false', 'true']:
            return lang.T_BOOL

        # If the program isn't a boolean or integer, it must be a variable. Look it up in the current context
        if not env.contains_bind(prog):
            raise UndeclaredVariableError()
        else:

            # A variable's entry is set to None once a linear or affine judgement about it has been used. If we're
            # trying to use it again, then throw an error
            if env.get_bind_val(prog) is None:
                raise LinAffineVariableReuseError(f'Duplicate use of {prog}')

            # If the judgement is unrestricted, then we can use it without any worry. If not, then we have to remove
            # the judgement from the context after using it.
            t = env.get_bind_val(prog)
            if t.mod != lang.T_mod.un:
                env.set_bind_val(prog, None)

            return t

    elif len(prog) == 0:
        # The empty list is always interpreted as nil.
        return lang.T_NIL

    elif prog[0] == "defvar":
        _, name, declared_tprog, init_prog = prog

        declared_tprog = lang.tparse(declared_tprog)
        init_t = type_check(env, init_prog)

        if not subtype(init_t, declared_tprog):
            raise TypeMismatchError
        else:
            # TODO Is setting the variable name to be a reference the correct thing to do? Also, should it be affine?
            env.define_bind(name, lang.Type(lang.T_mod.aff, lang.T_cat.val, declared_tprog))
            return lang.T_UNIT

    elif prog[0] == "defun":
        _, fname, f_tmod, ret_tprog, arg_spec_ls = prog[:4]
        body = prog[4:]

        ret_t = lang.tparse(ret_tprog)

        new_env = Env()
        actual_arg_t_ls = ()
        for arg_name, arg_tprog in arg_spec_ls:
            new_env.define_bind(arg_name, lang.tparse(arg_tprog))
            arg_spec_ls += (new_env.get_bind_val(arg_name),)
        actual_ret_t = type_check(new_env, body)

        # TODO This is one of the two places where an explicit check for affine and linear types has to go, I'm p sure
        # The other is in the sequential evaluation part. Both correspond to variables being descoped.

        if not subtype(actual_ret_t, ret_t):
            raise TypeMismatchError(f'{prog} returns the wrong type!')

        if env.contains_bind(fname):
            raise VariableRedefinitionError
        else:
            env.define_bind(fname, lang.Type(f_tmod, lang.T_cat.fun, (ret_t, actual_arg_t_ls)))
            return lang.T_UNIT

    elif prog[0] == "ref":
        _, referenced_thing = prog
        thing_type = type_check(env, referenced_thing)
        # TODO What should references be? Affine? I think they can be unrestricted as long as they're immutable, and
        # we should only be able to call set on a mutable reference (pretty sure that will give us the behavior we want)
        return lang.Type(lang.T_mod.aff, lang.T_cat.ref, thing_type)

    elif prog[0] == "dref":
        _, thing = prog
        thing_type = type_check(env, thing)
        if thing_type.type_enum != lang.T_cat.ref:
            raise RuntimeError("Attempted to dereference something that's not a reference!")
        return thing_type.type_args

    elif prog[0] == "set":
        # TODO Should we check that only mutable references are ever set?
        _, target_loc, new_def = prog
        # TODO The evaluation order is very important (might require deep consideration). Consider (set x (apply + x 1))
        if not env.contains_bind(target_loc):
            raise UndeclaredVariableError
        # TODO Should this check even be here! I mean, maybe?
        elif env.get_bind_val(target_loc) is None:
            raise VariableRedefinitionError
        target_loc_t = env.get_bind_val(target_loc)
        setform_t = type_check(env, new_def)
        if target_loc_t.type_enum != lang.T_cat.ref:
            raise RuntimeError("Attempting to set a non-reference!")
        elif not subtype(setform_t, target_loc_t.type_args):
            raise TypeMismatchError("Attempting to set to the wrong thing!")
        else:
            # TODO I'm not sure what to do here... It's getting a bit late :<
            # I think I need to manually add the statement that target_loc: def_type back in
            return target_loc_t

    elif prog[0] == "apply":
        _, fname = prog[:2]
        fargs = prog[2:]

        ftype = type_check(env, fname)
        fsig_ret_t, fsig_arg_t_ls = ftype.type_args[1]

        actual_arg_t_ls = ()
        for arg_name in fargs:
            actual_arg_t_ls += (type_check(env, arg_name),)

        if len(actual_arg_t_ls) != len(fsig_arg_t_ls):
            raise RuntimeError("Didn't pass in right number of arguments!")
        for i in range(len(actual_arg_t_ls)):
            if not subtype(actual_arg_t_ls[i], fsig_arg_t_ls[i]):
                raise TypeMismatchError(
                    f'Argument {i} expected to be {ftype.type_args[1][i]}, got {actual_arg_t_ls[i]}')

        return fsig_ret_t

    else:
        # We performed the check for zero-length above, so None will never actually be returned
        ret_type = None
        for p in prog:
            ret_type = type_check(env, p)

        return ret_type
