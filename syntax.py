from syntax_errors import *


def check_id_spec(name: str):
    allowed_special_chars = ["-", "_"]
    for c in allowed_special_chars:
        name = name.replace(c, "")
    if not name.isalnum():
        raise ValueError(f"{name} is not a valid identifier (must be alphanumeric with no spaces)")


def check_valid_typemod(mod: str):
    if not (mod in ['lin', 'un', 'aff']):
        raise ValueError(f'Invalid type modifier: {mod}')


def check_name_exists(name: str, curr_vars: set):
    check_id_spec(name)
    if name not in curr_vars:
        raise VariableUndefinedError()


def check_name_nexists(name: str, curr_vars: set):
    check_id_spec(name)
    if name in curr_vars:
        raise BindingRedefinitionError()


def check_type_exists(name: str, curr_types: set):
    check_id_spec(name)
    if name not in curr_types:
        raise TypeUndefinedError()


def check_type_nexists(name: str, curr_types: set):
    check_id_spec(name)
    if name in curr_types:
        raise RedefiningTypeError()


def check_syntax_with_env(code_tree, curr_vars: set, curr_types: set):

    if isinstance(code_tree, str):
        check_name_exists(code_tree, curr_vars)
        return curr_vars, curr_types
    else:
        if len(code_tree) == 0:
            return curr_vars, curr_types

        root_node = code_tree[0]
        root_args = code_tree[1:]

        if root_node == "defvar":
            # (defvar var-name type-modifier base-type)
            assert len(root_args) == 3
            _, var_name, type_modifier, var_type = code_tree
            check_name_nexists(var_name, curr_vars)
            check_valid_typemod(type_modifier)
            check_type_exists(var_type, curr_types)

            return curr_vars.union([var_name]), curr_types

        elif root_node == "deftype":
            # (deftype foo-type)
            assert len(root_args) == 1
            type_name = root_args[0]
            check_name_nexists(type_name, curr_types)

            return curr_vars, curr_types.union([type_name])

        elif root_node == "defun":
            # (defun fun-name (ret-mod ret-type) [(arg1 tmod1 t1) ... (argn tmodn tn)] code)
            assert len(root_args) == 4
            fun_name, ret_tspec, arg_bindings, body = root_args[0], root_args[1], root_args[2], root_args[3]
            check_name_nexists(fun_name, curr_vars)
            assert isinstance(ret_tspec, tuple)
            check_valid_typemod(ret_tspec[0])
            check_type_exists(ret_tspec[1], curr_types)

            assert isinstance(arg_bindings, tuple)

            fvars = set()
            for binding in arg_bindings:
                assert isinstance(binding, tuple)
                assert len(binding) == 3
                vname, tmod, t = binding
                check_id_spec(vname)
                check_valid_typemod(tmod)
                check_type_exists(t, curr_types)

                fvars.add(vname)

            check_syntax_with_env(body, fvars, curr_types)

            return curr_vars.union([fun_name]), curr_types

        elif root_node == "apply":
            # TODO Don't allow calling with an incorrect number of arguments
            # (call fun-name code1 ... coden)
            assert len(root_args) >= 1
            fname, fargs = root_args[0], root_args[1:]
            check_name_exists(fname, curr_vars)
            for arg in fargs:
                check_syntax_with_env(arg, curr_vars, curr_types)

            return curr_vars, curr_types

        elif root_node == "set":
            # (set var-name code)
            assert len(root_args) == 2
            var_name, eval_form = root_args
            check_name_exists(var_name, curr_vars)
            check_syntax_with_env(eval_form, curr_vars, curr_types)
            return curr_vars, curr_types

        elif root_node == "free":
            assert len(root_args) == 1
            check_syntax_with_env(root_args, curr_vars, curr_types)
            return curr_vars, curr_types

        elif root_node == "mut-ref":
            assert len(root_args) == 1
            var_name = root_args[0]
            check_name_exists(var_name, curr_vars)
            return curr_vars, curr_types

        elif root_node == "ref":
            assert len(root_args) == 1
            var_name = root_args[0]
            check_name_exists(var_name, curr_vars)
            return curr_vars, curr_types

        elif root_node == "if":
            assert len(root_args) == 3
            [check_syntax_with_env(b, curr_vars, curr_types) for b in root_args]
            return curr_vars, curr_types

        elif root_node == "while":
            assert len(root_args) == 2
            test, body = root_args[0], root_args[1]
            check_syntax_with_env(test, curr_vars, curr_types)
            check_syntax_with_env(body, curr_vars, curr_types)
            return curr_vars, curr_types

        else:
            # TODO This isn't right... It will leak abstractions from (what should be) inner scopes
            # Actually, the implementation seems surprisingly resilient after running a few tests.
            # I'm sure bugs are lurking underneath the surface, but hopefully it's fine for now.
            for statement in code_tree:
                curr_vars, curr_types = check_syntax_with_env(statement, curr_vars, curr_types)

            return curr_vars, curr_vars


def check_syntax(code_tree):
    return check_syntax_with_env(code_tree, set(), set())