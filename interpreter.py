from env import Env
from language import *
from type_checker import *


class Procedure:
    def __init__(self, fn_type, argspec_ls, fn_body):

        # TODO How to handle recursive procedures?

        self.argspec_ls = argspec_ls
        self.fn_body = fn_body
        # TODO Have to figure out how to actually use the function type...
        self.type = fn_type

    def __call__(self, *argvals):
        if len(argvals) != len(self.argspec_ls):
            raise RuntimeError("Mismatch between number of arguments required and number of arguments given")
        env = Env()
        for argspec, val in zip(self.argspec_ls, argvals):
            name, tmod, base_t = argspec
            # TODO TYPING Have to create this as a function type!
            if not base_t == check_type_of_evaluated(env, val):
                raise FunctionArgumentTypeError(
                    f"{argspec[0]}: Expected {base_t}, Received: {check_type_of_evaluated(env, val)}")
            env.define_bind(name, tmod, base_t)
            env.set_bind_val(name, val)

        return eval_form(env, self.fn_body)


def eval_form(base_env: Env, prog):

    #################################################################################################
    # Defining the macro functions here is the only nice way to allow them to be mutually recursive #
    #################################################################################################

    def eval_defvar(env: Env, var_name, bmod, btype):
        env.define_bind(var_name, bmod, btype)
        return UNIT

    def eval_deftype(env: Env, base_type):
        env.define_type(base_type)
        return base_type

    def eval_defun(env: Env, fun_spec, argspec_list, fn_body):
        # TODO Have to figure out how to represent/check function types
        function_type = (fun_spec[2])
        env.define_bind(*fun_spec)
        env.set_bind_val(fun_spec[0], Procedure(function_type, argspec_list, fn_body))

    def eval_set(env: Env, var_name, val_prog):
        final = eval_form(env, val_prog)
        env.set_bind_val(var_name, final)
        return final

    def eval_apply(env: Env, fun_name, arg_list):
        # TODO Figure out apply, it's actually useless
        return env.get_bind_val(fun_name,)(*arg_list)

    def eval_if(env: Env, when_c, then_c, else_c, ):
        """
        Take in when, then, and else ASTs and execute the if statement
        """
        when_result = eval_form(env, when_c)
        inner_env = Env(env)

        if when_result:
            ret = eval_form(inner_env, then_c)
        else:
            ret = eval_form(inner_env, else_c)
        inner_env.deallocate()

        return ret

    def eval_while(env: Env, test_c, default_c, body_c):

        inner_env = Env(env)
        return_default = True
        ret = None

        while True:
            test_result = eval_form(env, test_c)
            if test_result:
                return_default = False
                ret = eval_form(inner_env, body_c)
            else:
                break

        if not return_default:
            return ret
        else:
            return eval_form(inner_env, default_c)

    def eval_mut_ref(env: Env, var_name):
        # TODO
        raise NotImplementedError

    def eval_ref(env: Env, var_name):
        # TODO
        raise NotImplementedError

    ######################################
    # Begin actual evaluation code here! #
    ######################################

    macro_evaluators = {
        "defun": eval_defun,
        "defvar": eval_defvar,
        "deftype": eval_deftype,
        "set": eval_set,
        "apply": eval_apply,
        "if": eval_if,
        "while": eval_while,
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
            return NIL
        else:
            first_element = prog[0]
            if isinstance(first_element, str):
                if first_element in MACRO_NAMES:
                    return macro_evaluators[first_element](base_env, *prog[1:])
                else:
                    evaluated_args = [eval_form(base_env, arg) for arg in prog[1:]]
                    return_value = base_env.get_bind_val(first_element)(*evaluated_args)
                    if not check_type_of_evaluated(base_env, return_value) in base_env.get_bind_type(first_element):
                        raise FunctionReturnTypeError(f"{first_element} does not return value of type "
                                                      f"{base_env.get_bind_type(first_element)}")
                    return base_env.get_bind_val(first_element)(*evaluated_args)
            else:
                ret = None
                for prog in prog:
                    ret = eval_form(base_env, prog)

                return ret


def evaluate(prog):
    return eval_form(Env(), prog)

