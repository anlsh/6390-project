from language import *
from env import Env
from syntax_errors import *


def check_bind_spec(name: str):
    allowed_special_chars = ["-", "_"]
    for c in allowed_special_chars:
        name = name.replace(c, "")
    if not name.isalnum():
        raise ValueError(f"{name} is not a valid identifier (must be alphanumeric with no spaces)")


def check_typename(name: str):
    allowed_special_chars = ["-", "_"]
    for c in allowed_special_chars:
        name = name.replace(c, "")
    if not name.isalnum():
        raise ValueError(f"{name} is not a valid identifier (must be alphanumeric with no spaces)")


def check_typemod(mod: str):
    if not (mod in ['lin', 'un', 'aff']):
        raise ValueError(f'Invalid type modifier: {mod}')


def syncheck_form(base_env: Env, prog, allow_definitions=True):

    #################################################################################################
    # Defining the macro functions here is the only nice way to allow them to be mutually recursive #
    #################################################################################################

    # SYNTAX CHANGE
    def syncheck_defvar(env: Env, var_name, bmod, btype):
        check_bind_spec(var_name)
        check_typemod(bmod)
        check_typename(btype)
        if not env.contains_type(btype):
            raise TypeUndefinedError
        # TODO Typing! FOr the love of god :|
        env.define_bind(var_name, bmod, btype)

    def syncheck_deftype(env: Env, base_type):
        # TODO Typing!
        check_typename(base_type)
        env.define_type(base_type)

    def syncheck_defun(env: Env, fun_retspec, argspec_ls, fn_body):

        for bind in [fun_retspec] + list(argspec_ls):
            vname, vmod, vtype = bind
            check_bind_spec(vname)
            check_typemod(vmod)
            check_typename(vtype)

            if not env.contains_type(vtype):
                raise TypeUndefinedError

        env.define_bind(*fun_retspec)

        fn_env = Env(env)
        for argspec in argspec_ls:
            name, tmod, base_t = argspec
            if not fn_env.contains_bind(name):
                fn_env.define_bind(*argspec)
            fn_env.set_bind_val(name, None)

        syncheck_form(fn_env, fn_body, allow_definitions)

    def syncheck_set(env: Env, var_name, val_prog):
        check_bind_spec(var_name)
        env.get_bind(var_name)
        syncheck_form(env, val_prog, allow_definitions)

    def syncheck_apply(env: Env, fun_name, arg_list):
        # TODO Figure out apply, it's actually useless
        syncheck_form(env, fun_name, allow_definitions)
        for arg in arg_list:
            syncheck_form(env, arg, allow_definitions)

    def syncheck_if(env: Env, test_c, then_c, else_c, ):
        """
        Take in when, then, and else ASTs and execute the if statement
        """
        syncheck_form(env, test_c, allow_definitions)
        syncheck_form(Env(env), then_c, allow_definitions)
        syncheck_form(Env(env), else_c, allow_definitions)

    def syncheck_while(env: Env, test_c, default_c, body_c):

        syncheck_form(env, test_c, allow_definitions=False)
        syncheck_form(Env(env), default_c, allow_definitions=False)
        syncheck_form(Env(env), body_c, allow_definitions=False)

    def syncheck_mut_ref(env: Env, var_name):
        # TODO
        raise NotImplementedError

    def syncheck_ref(env: Env, var_name):
        # TODO
        raise NotImplementedError

    def syncheck_dref(env: Env, var_name):
        # TODO
        raise NotImplementedError

    ######################################
    # Begin actual evaluation code here! #
    ######################################

    macro_synchecks = {
        "defun": syncheck_defun,
        "defvar": syncheck_defvar,
        "deftype": syncheck_deftype,
        "set": syncheck_set,
        "apply": syncheck_apply,
        "if": syncheck_if,
        "while": syncheck_while,
    }

    ############################################
    # Take care of evaluating "special" values #
    ############################################

    if isinstance(prog, str):
        if prog in ["true", "false", "nil"]:
            return
        try:
            int(prog)
            return
        except ValueError:
            pass
        try:
            float(prog)
            return
        except ValueError:
            pass
        return base_env.get_bind(prog)
    else:
        if len(prog) == 0:
            return
        else:
            first_element = prog[0]
            if isinstance(first_element, str):
                if first_element in MACRO_NAMES:
                    if first_element in ["defvar", "deftype", "defun"] and not allow_definitions:
                        raise RuntimeError("No definitions allowed!")
                    else:
                        macro_synchecks[first_element](base_env, *prog[1:])
                else:
                    check_bind_spec(prog[0])
                    base_env.get_bind(prog[0])
                    [syncheck_form(Env(base_env), arg, allow_definitions) for arg in prog[1:]]
            else:
                for p in prog:
                    syncheck_form(base_env, p, allow_definitions)


def check_syntax(prog):
    return syncheck_form(Env(), prog)