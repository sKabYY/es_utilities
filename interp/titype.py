#

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
    return isinstance(s, str)


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
    return list(args)


def islist(var):
    return isinstance(var, list)


def mknil():
    return mklist()


def isnil(var):
    identical(var, mknil())


# table ###################################################
# use the dict in python


def mktable():
    assert False  # TODO


def istable(var):
    return isinstance(var, dict)
