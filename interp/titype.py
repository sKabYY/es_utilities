#

import pprint

from simpletable import enum, SimpleTable
table = SimpleTable

TYPE = enum(
    # immutable types
    'VOID',
    'BOOLEAN',
    'NUMBER',
    'STRING',
    'COMPOUND',
    'PRIMITIVE',
    'SYMBOL',
    # mutable types
    'LIST',
    'TABLE',
    # mapper
    key_mapper=lambda s: s
)


def identical(a, b):
    return type(a) == type(b) and a == b


class TiType(table):
    def __init__(self, _type, **kwargs):
        self.update(kwargs)
        self.type = _type


def check_type(st, _type):
    return isinstance(st, TiType) and st.type == _type


# void ####################################################


def __global_void():
    pass


def mkvoid():
    r'A function that returns #<void>'
    return __global_void


def isvoid(var):
    return var == __global_void


# true ####################################################


def mktrue():
    return True


def idtrue(var):
    return identical(var, mktrue())


def mkfalse():
    return False


def idfalse(var):
    return identical(var, mkfalse())


def mkboolean(b):
    if b:
        return mktrue()
    else:
        return mkfalse()


def isboolean(var):
    return idtrue(var) or idfalse(var)


def isfalse(var):
    return idfalse(var)


def istrue(var):
    return not isfalse(var)


# number ##################################################


def mknumber(n):
    return n


def isinteger(n):
    return isinstance(n, int)


def isfloat(n):
    return isinstance(n, float)


def isnumber(n):
    return isinteger(n) or isfloat(n)


# string ##################################################


def mkstring(s):
    return s


def isstring(s):
    return type(s) == str


# symbol ##################################################


class Symbol(str):
    def __init__(self, s):
        super(Symbol, self).__init__(s)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return super(Symbol, self).__str__()

    def __eq__(self, v):
        if issymbol(v):
            symbol_tostring(self) == symbol_tostring(v)
        elif isstring(v):
            return symbol_tostring(self) == v
        else:
            return False


def mksymbol(s):
    return Symbol(s)


def issymbol(v):
    return type(v) == Symbol


def symbol_tostring(sym):
    return str(sym)


def symbol_eqs(a, b):
    if issymbol(a):
        a = symbol_tostring(a)
    if issymbol(b):
        b = symbol_tostring(b)
    return a == b


# procedure ###############################################

# struct of compound procedure:
#   table(
#     args: is a list of strings,
#     body: is a analyzed function,
#     env
#   )
def mkcompound(args, proc, env):
    return TiType(TYPE.COMPOUND,
                  args=args, body=proc, env=env)


def iscompound(var):
    return check_type(var, TYPE.COMPOUND)


# struct of primitive procedure:
#   table(
#     type: 'primitive'
#     name: a string
#     argc: a function that check the number of arguments
#     operation: a function with <argc> arguments
#   )
def mkprimitive(name, argc, operation):
    return TiType(TYPE.PRIMITIVE,
                  name=name, argc=argc, operation=operation)


def isprimitive(var):
    return check_type(var, TYPE.PRIMITIVE)


def isprocedure(var):
    return isprimitive(var) or iscompound(var)


# list ####################################################
# use the list in python


def mklist(*args):
    r'''(list a ...):
Make a list of <a>s.'''
    return list(args)


def islist(var):
    # Cannot use isinstance(var, list)!!
    return type(var) == list


def mknil():
    return mklist()


def list_tostring(var):
    return pprint.pformat(var)


def isnil(var):
    return identical(var, mknil())


def ispair(var):
    return islist(var) and list_length(var) != 0


def list_length(seq):
    return len(seq)


def list_append(a, b):
    res = mklist(*a)
    res.extend(b)
    return res


def list_cons(a, seq):
    res = mklist(*seq)
    res.insert(0, a)
    return res


def list_car(seq):
    return seq[0]


def list_cdr(seq):
    return seq[1:]


# table ###################################################
# use the dict in python


def mktable():
    assert False  # TODO


def istable(var):
    return isinstance(var, dict)  # TODO


def table_tostring(var):
    return pprint.pformat(var)
