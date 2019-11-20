import language as lang

import dsl_types as dslT
from typing import Tuple, Union
from copy import deepcopy

from env import TypeCheckEnv, deepcopy_env
import typecheck_errors as tc_err


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

        if env.contains_fun(prog):
            return env.get_fun_def(prog)

        # If the program isn't a boolean or integer, it must be a variable. Look it up in the current context
        # A variable's entry is set to None once a linear or affine judgement about it has been used. If we're
        # trying to use it again, then throw an error
        if env.get_bind_val(prog).is_borrow():
            raise tc_err.LinAffineVariableReuseError(f'{prog} attempts to use borrowed value')

        # If the judgement is unrestricted, then we can use it without any worry. If not, then we have to remove
        # the judgement from the context after using it.
        t = env.get_bind_val(prog)
        if not t.is_un():
            t.set_borrow()

        return t

    @classmethod
    def check_defvar(cls, env: TypeCheckEnv, name, declared_tprog, init_prog):

        signature_t = dslT.tparse(declared_tprog)
        valprog_t = cls.type_check(env, init_prog, being_bound=True)

        if not dslT.Type.is_subtype(valprog_t, signature_t):
            raise tc_err.TypeMismatchError(f'Binding {name} expects variable of type {signature_t} '
                                           f'but got {valprog_t}, which is not a subtype')
        else:
            if isinstance(signature_t, dslT.RefType):
                signature_t.borrow_parent = valprog_t.borrow_parent
                valprog_t.set_borrow()
            env.define_bind(name, signature_t)
            return lang.T_UNIT

    @classmethod
    def check_set(cls, env: TypeCheckEnv, name, new_def):

        signature_t = env.get_bind_val(name)
        valprog_t = cls.type_check(env, new_def, being_bound=True)

        if not dslT.Type.is_subtype(valprog_t, signature_t):
            raise tc_err.TypeMismatchError(f'Binding {name} expects variable of type {signature_t} '
                                           f'but got {valprog_t}, which is not a subtype')
        else:
            if isinstance(signature_t, dslT.RefType):
                signature_t.borrow_parent = valprog_t.borrow_parent
                valprog_t.set_borrow()

            if signature_t.is_borrow():
                env.get_bind_val(name).set_own()
            elif signature_t.is_own() and signature_t.is_lin():
                raise tc_err.TypeMismatchError("Trying to set variable which owns value (could leak memory this way)")
            return lang.T_UNIT

    @classmethod
    def check_defun(cls, env: TypeCheckEnv, fname, sig_ret_tprog, arg_spec_ls, *body):

        # Functions don't close over enclosing values, so declare.0 a new env that the body will be type-checking in
        new_env = TypeCheckEnv(defaults=env.functions)

        # To type-check the body, first assume that all arguments have the declared types...
        arg_t_ls = ()
        for arg_name, arg_tprog in arg_spec_ls:
            t = dslT.tparse(arg_tprog)

            # Need to manually set up dummy parents for all reference types...
            if isinstance(t, dslT.RefType):
                t.borrow_parent = t.referenced_type()
                t.borrow_parent.set_borrow()

            new_env.define_bind(arg_name, t)
            arg_t_ls += (new_env.get_bind_val(arg_name),)

        # And then check the body to see what is returned in the end. Set descope=True to make sure there aren't any
        # linear judgements unused
        actual_ret_t = cls.type_check(new_env, body, descope=True)

        # Make sure that the actual return value is a subtype of the signature return value
        sig_ret_t = dslT.tparse(sig_ret_tprog)
        if not dslT.Type.is_subtype(actual_ret_t, sig_ret_t):
            raise tc_err.TypeMismatchError(f'Function actually returns {actual_ret_t}, '
                                           f'which is not a subtype of declared return {sig_ret_t}')
        else:
            env.define_fun(fname, dslT.FunType(mod=lang.Tmod.un, retT=sig_ret_t, argTs=arg_t_ls))
            return lang.T_UNIT

    @classmethod
    def check_mkref(cls, env: TypeCheckEnv, var):
        ref_type = env.get_bind_val(var)
        if not ref_type.is_own():
            raise tc_err.BorrowedValueUseError(f"Attempted to make reference to {var}, which is currently borrowed")
        ref_type.set_borrow()
        return dslT.RefType(mod=lang.Tmod.un, ref_type=ref_type, borrow_parent=ref_type)

    @classmethod
    def check_deref(cls, env: TypeCheckEnv, refname):
        ref_type = env.get_bind_val(refname)
        assert isinstance(ref_type, dslT.RefType)
        if not ref_type.is_own():
            raise RuntimeError("Attempt to dereference borrowed reference!")
        ref_base_type = ref_type.referenced_type()
        if ref_base_type.is_un():
            ret_type = deepcopy(ref_base_type)
            ret_type.set_own_unconditional()
        else:
            raise tc_err.DerefNonCopyError()

        return ret_type

    @classmethod
    def check_setrefval(cls, env: TypeCheckEnv, ref_name, new_def):
        ref_type = env.get_bind_val(ref_name)
        if not isinstance(ref_type, dslT.RefType):
            raise RuntimeError("Attempted to use setrefval on a non-reference!")
        if not ref_type.is_own():
            raise RuntimeError("Attempting to set through a borrowed reference")
        if ref_type.referenced_type().is_lin():
            raise tc_err.UnusedLinVariableError("Attempt to set an owned linear variable through a reference")

        new_def_type = cls.type_check(env, new_def, being_bound=True)
        if not new_def_type.is_own():
            raise RuntimeError("The definition form evaluates to something borrowed!")
        elif not new_def_type.eq_ignore_oship(ref_type.referenced_type()):
            raise tc_err.TypeMismatchError(f"{ref_name} is reference to {ref_type.referenced_type()}, "
                                           f"but set was attempted with {new_def_type}")

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

            if isinstance(fsig_arg_t_ls[i], dslT.RefType):
                assert env.contains_bind(fargs[i])
                assert env.get_bind_val(fargs[i]).is_own()
                env.get_bind_val(fargs[i]).set_borrow()

            if not dslT.Type.is_subtype(actual_arg_t_ls[i], fsig_arg_t_ls[i]):
                raise tc_err.TypeMismatchError(f'Argument {i} expected to be {sigT}, got {actual_argT}')

        # Unborrow all the things passed in as arguments
        for i, bname in enumerate(fargs):
            if isinstance(fsig_arg_t_ls[i], dslT.RefType):
                env.get_bind_val(fargs[i]).set_own_unconditional()

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
            raise tc_err.TypeMismatchError("If statement conditional was not of type bool.")

        new_env_then = TypeCheckEnv(outer=deepcopy_env(env))
        new_env_else = TypeCheckEnv(outer=env)
        then_type = cls.type_check(new_env_then, then_body, descope=True)
        else_type = cls.type_check(new_env_else, else_body, descope=True)

        # TODO Confirm that this works
        if new_env_then.outer != env:
            raise tc_err.EnvironmentMismatchError("Branches of if statement produce different environments")

        if then_type != else_type:
            raise tc_err.TypeMismatchError("Then body type does not equal else body type.")

        return then_type

    @classmethod
    def check_while(cls, env: TypeCheckEnv, test, default, body):
        test_type = cls.type_check(env, test)
        if not dslT.Type.is_subtype(test_type, lang.T_LIN_BOOL):
            raise tc_err.TypeMismatchError("While statement conditional was not of type bool.")
        old_env = deepcopy_env(env)

        new_env_def = TypeCheckEnv(outer=deepcopy_env(env))
        new_env_bod = TypeCheckEnv(outer=env)
        def_type = cls.type_check(new_env_def, default, descope=True)
        bod_type = cls.type_check(new_env_bod, body, descope=True)

        if new_env_def.outer != old_env:
            raise tc_err.EnvironmentMismatchError("Default clause illegally modifies environment")
        elif new_env_bod.outer != old_env:
            raise tc_err.EnvironmentMismatchError("Body clause illegally modifies environment")

        if not def_type == bod_type:
            raise tc_err.TypeMismatchError("Default and Body clauses return values of different types")

        return def_type

    @classmethod
    def check_scope(cls, env: TypeCheckEnv, *body):
        new_frame = TypeCheckEnv(outer=env)
        return cls.type_check(new_frame, body, descope=True)

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
            "setrefval": cls.check_setrefval,
            "mkref": cls.check_mkref,
            "deref": cls.check_deref,
            "set": cls.check_set,
            "apply": cls.check_apply,
            "if": cls.check_if,
            "while": cls.check_while,
            "scope": cls.check_scope,
        }

        if not (isinstance(prog, tuple)):
            ret = cls.check_atomic(env, prog)
        elif len(prog) == 0:
            # The empty list is always interpreted as nil.
            ret = lang.T_NIL
        elif prog[0] in macro_tcheck_fns:
            ret = macro_tcheck_fns[prog[0]](env, *prog[1:])
        else:
            # We performed the check for zero-length above, so None will never actually be returned
            ret = cls.check_sequential(env, prog)

        if not being_bound:
            if ret.is_lin():
                raise tc_err.UnusedLinVariableError()
            # TODO It's not so great to hardcode this thing here, but maybe it's not too ugly?
            elif prog[0] == 'mkref':
                raise tc_err.ReferenceNoEffectError

        if descope:
            env.deallocate()

        return ret
