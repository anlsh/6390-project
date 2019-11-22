from env import Env
from language import *


class Procedure:
    def __init__(self, defaults, argspec_ls, fn_body):
        self.argspec_ls = argspec_ls
        self.fn_body = fn_body
        self.defaults = defaults

    def __call__(self, *argvals):
        if len(argvals) != len(self.argspec_ls):
            raise RuntimeError("Mismatch between number of arguments required and number of arguments given")
        # TODO How to have an env that captures previously defined functions but not variables?
        env = Env(defaults=self.defaults)
        for argspec, val in zip(self.argspec_ls, argvals):
            name, arg_type = argspec
            env.define_bind(name, arg_type)
            env.set_bind_val(name, val)
        return eval_form(env, self.fn_body)


def eval_form(base_env: Env, prog):

    #################################################################################################
    # Defining the macro functions here is the only nice way to allow them to be mutually recursive #
    #################################################################################################

    def eval_defvar(env: Env, name, declared_tprog, init_prog):
        final = eval_form(env, init_prog)
        env.define_bind(name, final)
        return None

    def eval_defun(env: Env, fname, fun_ret_t, argspec_list, *fn_body):
        env.define_fun(fname, Procedure(base_env.functions, argspec_list, fn_body))
        return None

    def eval_set(env: Env, var_name, val_prog):
        final = eval_form(env, val_prog)
        env.set_bind_val(var_name, final)
        return None

    def eval_apply(env: Env, fun_name, *arg_list):
        eval_args = [eval_form(env, arg) for arg in arg_list]
        return env.get_fun_def(fun_name)(*eval_args)

    def eval_scope(env: Env, *prog):
        return evaluate(Env(outer=env), prog)

    def eval_if(env: Env, test, then_c, else_c, ):
        """
        Take in when, then, and else ASTs and execute the if statement
        """
        test_result = eval_form(env, test)
        inner_env = Env(outer=env)

        if test_result:
            ret = eval_form(inner_env, then_c)
        else:
            ret = eval_form(inner_env, else_c)
        inner_env.deallocate()

        return ret

    def eval_while(env: Env, test_c, default_c, body_c):

        inner_env = Env(outer=env)
        return_default = True
        ret = None

        while True:
            test_result = eval_form(inner_env, test_c)
            if test_result:
                return_default = False
                ret = eval_form(inner_env, body_c)
            else:
                break

        inner_env.deallocate()
        if not return_default:
            return ret
        else:
            return eval_form(inner_env, default_c)

    def eval_mkref(env: Env, var):
        return (var, env.get_bind(var))

    def eval_setref(env: Env, ref_name, new_def):
        eval_new_def = eval_form(env, new_def)
        env.set_bind_val(ref_name, eval_new_def)

    def eval_deref(env: Env, ref):
        var, referenced_binding = env.get_bind_val(ref)
        val, defining_env = referenced_binding
        return val

    def eval_setrefval(env: Env, ref, new_val):
        eval_new_val = eval_form(env, new_val)
        var, referenced_binding = env.get_bind_val(ref)
        val, defining_env = referenced_binding
        defining_env.set_bind_val(var, eval_new_val)

    ######################################
    # Begin actual evaluation code here! #
    ######################################

    macro_evaluators = {
        "defun": eval_defun,
        "defvar": eval_defvar,
        "scope": eval_scope,
        "set": eval_set,
        "apply": eval_apply,
        "if": eval_if,
        "while": eval_while,
        "mkref": eval_mkref,
        "setref": eval_setref,
        "deref": eval_deref,
        "setrefval": eval_setrefval
    }

    ############################################
    # Take care of evaluating "special" values #
    ############################################

    if isinstance(prog, str):
        if prog == "true":
            return True
        elif prog == "false":
            return False
        elif prog == "nil":
            return None
        try:
            return int(prog)
        except ValueError:
            pass
        try:
            return float(prog)
        except ValueError:
            pass

        return base_env.get_bind_val(prog)
    else:
        if len(prog) == 0:
            return T_NIL
        else:
            first_element = prog[0]

            if first_element in macro_evaluators:
                return macro_evaluators[first_element](base_env, *prog[1:])
            else:
                ret = None
                for subprog in prog:
                    ret = eval_form(base_env, subprog)
                return ret


def evaluate(env, prog):
    return eval_form(env, prog)