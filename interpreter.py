
class UnboundVariableAccessError(Exception):
    pass

class DeallocatedMemoryAccessError(Exception):
    pass


class BindingSet:
    """
    A class to hold all current bindings in the program (which are mostly
    just variable values)
    """

    def __init__(self,):
        # Binding dictionary maintains actual values. The allocated dictionary tracks whether a given
        # variable has been freed via a call to *free*
        self.binding_dict = {}
        self.type_dict = {}
        self.allocated_dict = {}

    def create_binding(self, varname: str, type: str, val):
        # TODO COMPILER This should be a compilation check, not in the interpreter itself.
        self.binding_exists_not_deallocated(varname)

        self.binding_dict[varname] = val
        self.allocated_dict[varname] = True
        return val


    def binding_exists_not_deallocated(self, varname: str):
        if varname in self.binding_dict and not self.allocated_dict[varname]:
            return DeallocatedMemoryAccessError
        if varname not in self.binding_dict:
            raise UnboundVariableAccessError()

    def set_binding(self, varname: str, val):

        # TODO COMPILER This should be a compilation check, not in the interpreter itself.
        self.binding_exists_not_deallocated(varname)

        self.binding_dict[varname] = val
        return val

    def get_val(self, varname: str):
        """If the token is a number, return it as-is. Else, it's a symbol so try to look in up in default bindings"""
        try:
            return int(varname)
        except ValueError:
            self.binding_exists_not_deallocated(varname)
            return self.binding_dict[varname]

    def free_binding(self, varname: str):
        """
        Free the variable (corresponding to the stack being de-allocated
        so that it can never be accessed again
        """
        self.binding_exists_not_deallocated(varname)

        self.allocated_dict[varname] = False
        return


def eval_with_bindings(code_tree, bindings: BindingSet):
    """
    Given a code tree, evaluate it! This code is not meant to check that the code is syntactically correct:
        that's the job of the parser. It assumes that the code it's been passed in is valid, and it just GOES

    :param code_tree:
    :param bindings:
    :return:
    """

    if not isinstance(code_tree, list):
        return bindings.get_val(code_tree)

    root_form = code_tree[0]
    if root_form == "define":
        "(define variable-name"
        assert len(code_tree) == 3
        BindingSet.create_binding()




