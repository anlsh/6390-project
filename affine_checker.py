import language as lang

import dsl_types as dslT
from typing import Tuple, Union

from env import TypeCheckEnv
from typecheck_errors import TypeMismatchError, LinAffineVariableReuseError, UnusedLinVariableError
from copy import deepcopy


def err_on_unused_lins(env: TypeCheckEnv):
    for name in env.get_toplevel_binds():
        if env.get_bind_val(name) is None:
            continue
        name_t = env.get_bind_val(name)
        if name_t.is_lin() and name_t.is_own():
            raise UnusedLinVariableError


class AffineTypeChecker:

    @classmethod
    def check_atomic(cls, env: TypeCheckEnv, prog: str) -> dslT.Type:
        # Try to interpret it as an integer or boolean first
        try:
            int(prog)
            return lang.T_INT
        except ValueError:
            if prog in lang.bool_map:
                return lang.T_BOOL

        # If the program isn't a boolean or integer, it must be a variable. Look it up in the current context
        # A variable's entry is set to None once a linear or affine judgement about it has been used. If we're
        # trying to use it again, then throw an error
        if env.get_bind_val(prog).is_borrow():
            raise LinAffineVariableReuseError(f'{prog} attempts to use borrowed value')

        # If the judgement is unrestricted, then we can use it without any worry. If not, then we have to remove
        # the judgement from the context after using it.
        # TODO This is where we'd implement checks for the "copy" trait.
        t = env.get_bind_val(prog)
        if not t.is_un():
            t.set_borrow()

        return t

    @classmethod
    def check_defvar(cls, env: TypeCheckEnv, name, declared_tprog, init_prog):

        signature_t = dslT.tparse(declared_tprog)
        initprogram_t = cls.type_check(env, init_prog, being_bound=True)

        if not dslT.Type.is_subtype(initprogram_t, signature_t):
            raise TypeMismatchError(f'Binding {name} expects variable of type {signature_t} '
                                    f'but got {initprogram_t}, which is not a subtype')
        else:
            env.define_bind(name, signature_t)
            return lang.T_UNIT

    @classmethod
    def check_defun(cls, env: TypeCheckEnv, fname, sig_ret_tprog, arg_spec_ls, *body):

        # Functions don't close over enclosing values, so declare a new env that the body will be type-checking in
        new_env = TypeCheckEnv()

        # To type-check the body, first assume that all arguments have the declared types...
        arg_t_ls = ()
        for arg_name, arg_tprog in arg_spec_ls:
            new_env.define_bind(arg_name, dslT.tparse(arg_tprog))
            arg_spec_ls += (new_env.get_bind_val(arg_name),)

        # And then check the body to see what is returned in the end. Set descope=True to make sure there aren't any
        # linear judgements used
        actual_ret_t = cls.type_check(new_env, body, descope=True)

        # Make sure that the actual return value is a subtype of the signature return value
        sig_ret_t = dslT.tparse(sig_ret_tprog)
        if not dslT.Type.is_subtype(actual_ret_t, sig_ret_t):
            raise TypeMismatchError(f'Function actually returns {actual_ret_t}, which is not a subtype of declared'
                                    f'return {sig_ret_t}')
        else:
            env.define_bind(fname,
                            dslT.FunType(mod=lang.Tmod.un, retT=sig_ret_t, argTs=arg_t_ls)
            )
            return lang.T_UNIT

    # TODO Implement the whole shebang on references... Seriously wtf are these things...

    @classmethod
    def check_ref(cls, env: TypeCheckEnv, referenced_thing):
        thing_type = cls.type_check(env, referenced_thing)
        return lang.Type(lang.Tmod.aff, lang.Tcat.ref, thing_type)

    @classmethod
    def check_dref(cls, env: TypeCheckEnv, thing):
        thing_type = cls.type_check(env, thing)
        if thing_type.type_enum != lang.Tcat.ref:
            raise RuntimeError("Attempted to dereference something that's not a reference!")
        return thing_type.__type_args

    @classmethod
    def check_set(cls, env: TypeCheckEnv, target_loc, new_def):
        place_sig_t = env.get_bind_val(target_loc)
        setform_t = cls.type_check(env, new_def, being_bound=True)

        if not dslT.Type.is_subtype(setform_t, place_sig_t):
            raise TypeMismatchError(f"{target_loc} expects type {place_sig_t}, but got {setform_t}")
        else:
            return lang.T_UNIT

    @classmethod
    def check_apply(cls, env: TypeCheckEnv, fname, *fargs):
        ftype = cls.type_check(env, fname)
        assert isinstance(ftype, dslT.FunType)
        fsig_arg_t_ls = ftype.argTs

        actual_arg_t_ls = ()
        for arg_name in fargs:
            actual_arg_t_ls += (cls.type_check(env, arg_name, being_bound=True),)

        if len(actual_arg_t_ls) != len(fsig_arg_t_ls):
            raise RuntimeError("Didn't pass in right number of arguments!")

        for i, (actual_argT, sigT) in enumerate(zip(actual_arg_t_ls, ftype.argTs)):
            if not dslT.Type.is_subtype(actual_arg_t_ls[i], fsig_arg_t_ls[i]):
                raise TypeMismatchError(f'Argument {i} expected to be {sigT}, got {actual_argT}')

        return ftype.retT

    @classmethod
    def check_sequential(cls, env: TypeCheckEnv, prog_ls):
        ret_type = None
        for p in prog_ls:
            ret_type = cls.type_check(env, p)

        return ret_type

    @classmethod
    def check_if(cls, env: TypeCheckEnv, test, then_body, else_body):
        test_type = cls.type_check(env, test)
        if not dslT.Type.is_subtype(test_type, lang.T_LIN_BOOL):
            raise TypeMismatchError("If test was not of type bool.")
        new_env_then = TypeCheckEnv(outer=deepcopy(env))
        new_env_else = TypeCheckEnv(outer=env)
        # TODO Confirm that this works
        if not new_env_then.outer == env:
            raise TypeMismatchError("Env copy is wack.")
        then_type = cls.type_check(new_env_then, then_body, descope=True)
        else_type = cls.type_check(new_env_else, else_body, descope=True)
        if not then_type == else_type:
            raise TypeMismatchError("Then body type does not equal else body type.")

        return then_type

    @classmethod
    def type_check(cls, env: TypeCheckEnv, prog: Union[Tuple, str],
                   descope: bool = False, being_bound: bool = False) -> dslT.Type:
        """
        Given a context Gamma and program tree, type-check it (modifying gamma along the way)
        :param being_bound: Don't allow orphaning of linear types, essentially
        :param descope:
        :param env:
        :param prog:
        :return:
        """
        #################################################################################
        # If the program isn't a tree, then it should be an integer, string, or boolean #
        #################################################################################
        macro_tcheck_fns = {
            "defvar": cls.check_defvar,
            "defun": cls.check_defun,
            "ref": cls.check_ref,
            "dref": cls.check_dref,
            "set": cls.check_set,
            "apply": cls.check_apply,
            "if": cls.check_if
        }

        if not (isinstance(prog, tuple)):
            ret = cls.check_atomic(env, prog)
        elif len(prog) == 0:
            # The empty list is always interpreted as nil.
            ret = lang.T_NIL
        elif prog[0] in lang.MACRO_NAMES:
            ret = macro_tcheck_fns[prog[0]](env, *prog[1:])
        else:
            # We performed the check for zero-length above, so None will never actually be returned
            ret = cls.check_sequential(env, prog)

        if descope:
            err_on_unused_lins(env)
        if (not being_bound) and (ret.is_lin()):
            raise UnusedLinVariableError()

        return ret
