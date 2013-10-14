#

from simpletable import enum, SimpleTable
table = SimpleTable

TYPE = enum(
    # base types
    'VOID',
    'NIL',
    'INTEGER',
    'FLOAT',
    'STRING',
    'PROCEDURE',
    # query types
    # TODO
    # mapper
    key_mapper=lambda s: s
)


class SemanticType(table):
    def __init__(self, _type):
        self.type = _type


def check_type(value, _type):
    return isinstance(value, table) and value.type == _type


# VOID and NIL
#  struct: {
#    type;
#  }

__global_void = SemanticType(TYPE.VOID)
__global_nil = SemanticType(TYPE.NIL)


def void():
    return __global_void


def isvoid(var):
    return check_type(var, TYPE.VOID)


def nil():
    return __global_nil


def isnil(var):
    return check_type(var, TYPE.NIL)

###

# INTEGER, FLOAT and STRING
#  struct: {
#    type;
#    value;
#  }


def fill_type_value(t, v):
    st = SemanticType(t)
    st.value = v
    return st


def mkinteger(i):
    return fill_type_value(TYPE.INTEGER, int(i))


def isinteger(var):
    return check_type(var, TYPE.INTEGER)


def mkfloat(f):
    return fill_type_value(TYPE.FLOAT, float(f))


def isfloat(var):
    return check_type(var, TYPE.FLOAT)


def mkstring(s):
    return fill_type_value(TYPE.STRING, str(s))


def isstring(var):
    return check_type(var, TYPE.STRING)

###

# PROCEDURE
#  struct: {
#    type;
#    args: a list of strings
#    body: a python function
#    env;
#  }


def mkprocedure():
    pass  # TODO
