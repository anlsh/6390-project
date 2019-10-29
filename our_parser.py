##################################################################
# This section of code taken directly from Peter Norvig's lis.py #
# https://norvig.com/lispy.html                                  #
##################################################################


from typing import NewType


def parse(src_str: str):
    "Converts a scheme expression into a string"
    return read_from_tokens(tokenize(src_str))


def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace('(', ' ( ').replace(')', ' ) ').split()


def read_from_tokens(tokens: list):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop off ')'
        return tuple(L)
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def atom(token: str):
    "Numbers become numbers; every other token is a symbol."
    return str(token)
