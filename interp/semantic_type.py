#

from simpletable import enum, SimpleTable
table = SimpleTable

TYPE = enum(
    # base types
    'VOID',
    'NIL',
    'BOOLEAN',
    'INTEGER',
    'FLOAT',
    'STRING',
    'PROCEDURE',
    'PRIMITIVE',
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

# BOOLEAN, INTEGER, FLOAT and STRING
#  struct: {
#    type;
#    value;
#  }


def fill_type_value(t, v):
    st = SemanticType(t)
    st.value = v
    return st


def __do_mkboolean(b):
    return fill_type_value(TYPE.BOOLEAN, b)


__global_true = __do_mkboolean(True)
__global_false = __do_mkboolean(False)


def true():
    return __global_true


def false():
    return __global_false


def mkboolean(b):
    if bool(b):
        return true()
    else:
        return false()


def isboolean(var):
    return check_type(var, TYPE.BOOLEAN)


def isfalse(var):
    return var == false()


def istrue(var):
    return not isfalse(var)


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


def mkprocedure(args, body, env):
    st = SemanticType(TYPE.PROCEDURE)
    st.args = args
    st.body = body
    st.env = env
    return st


def iscompound(var):
    return check_type(var, TYPE.PROCEDURE)


# PRIMITIVE PROCEDURE
#  struct: {
#    type;
#    argc: number of arguments, a negative number means any
#    body: a python function
#  }


def mkprimitive(argc, body):
    st = SemanticType(TYPE.PRIMITIVE)
    st.argc = argc
    st.body = body


def isprimitive(var):
    return check_type(var, TYPE.PRIMITIVE)


def isprocedure(var):
    return isprimitive(var) or iscompound(var)
