##

from table import table
from scanner import Token
from scanner import LPAREN, RPAREN, VARIABLE, NUMBER


#keywords
KW = table([
    'define',
    'if',
    'cond',
    'lambda',
    'and',
    'or',
], lambda s: s.upper())


class InterpError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


def check_error(b, msg=None):
    if not b:
        raise InterpError(msg)


def raise_error(msg):
    raise InterpError(msg)


class Env(object):
    def __init__(self, enclosing_env=None):
        self.current_env = {}
        self.enclosing_env = enclosing_env

    def put(self, symbol, value):
        self.current_env[symbol] = value

    def lookup(self, symbol):
        cur = self
        while cur is not None:
            try:
                return cur.current_env[symbol]
            except KeyError:
                cur = cur.enclosing_env
        raise_error('Unbound symbol: "%s"' % symbol)

    def extend(self, symbols, values):
        check_error(len(symbols) == len(values))
        n = len(symbols)
        new_env = Env(self)
        for i in xrange(n):
            new_env.put(symbols[i], values[i])
        return new_env


def is_token_type(exp, _type):
    return isinstance(exp, Token) and exp.type == _type


def is_token_value(exp, value):
    return isinstance(exp, Token) and exp.value == value


def is_tagged_list(exp, tag):
    return isinstance(exp, list) and is_token_value(exp[0], tag)


class Void(object):
    def __repr__(self):
        return str(self)

    def __str__(self):
        return '#void'


def void():
    return Void()


def isvoid(v):
    return isinstance(v, Void)


def nil():
    return []


def isnil(l):
    return isinstance(l, list) and len(l) == 0


def true():
    return True


def false():
    return False


def istrue(b):
    return b == true()


def isfalse(b):
    return not istrue(b)


# struct of procedure:
#   table(
#     type: 'procedure'
#     args: is a list of strings,
#     body: is a list of tokens,
#     env
#   )
def make_procedure(arguments, body, env):
    check_error(isinstance(arguments, list))
    check_error(
        reduce(
            lambda x, y: x and y,
            map(is_variable, arguments)))
    args = map(lambda t: t.value, arguments)
    return table({
        'type': 'procedure',
        'args': args,
        'body': body,
        'env': env,
    })


def is_table_type(t, _type):
    return isinstance(t, table) and t.type == _type


# struct of primitive procedure:
#   table(
#     type: 'primitive'
#     argc: number, < 0 means any
#     operation: a function with <argc> arguments
#   )
def isprimitive(p):
    return is_table_type(p, 'primitive')


def iscompound(p):
    return is_table_type(p, 'procedure')


def isprocedure(p):
    return isprimitive(p) or iscompound(p)


def is_self_evaluating(exp):
    return is_token_type(exp, NUMBER)


def is_variable(exp):
    return is_token_type(exp, VARIABLE)


def is_definition(exp):
    return is_tagged_list(exp, KW.DEFINE)


# Two types of define:
#   1, (define a 1.0) or (define f (lambda (x) x))
#   2, (define (f x) x)
def eval_define(exp, env):
    check_error(len(exp) == 3)
    if type(exp[1]) == list:
        subexp = exp[1]
        check_error(subexp[0].type == VARIABLE)
        arguments = subexp[1:]
        v = make_procedure(arguments, exp[2], env)
        env.put(subexp[0].value, v)
    else:
        check_error(exp[1].type == VARIABLE)
        v = _eval(exp[2], env)
        env.put(exp[1].value, v)
    return void()


def is_if(exp):
    return is_tagged_list(exp, KW.IF)


def eval_if(exp, env):
    check_error(len(exp) == 4)
    condition = _eval(exp[1], env)
    if istrue(condition):
        return _eval(exp[2], env)
    else:
        return _eval(exp[3], env)


def is_cond(exp):
    return is_tagged_list(exp, KW.COND)


def eval_cond(exp, env):
    check_error(False)  # TODO


def is_lambda(exp):
    return is_tagged_list(exp, KW.LAMBDA)


def eval_lambda(exp, env):
    check_error(len(exp) == 3)
    return make_procedure(exp[1], exp[2], env)


def is_application(exp):
    return isinstance(exp, list)


def eval_application(exp, env):
    proc = _eval(exp[0], env)
    check_error(
        isprocedure(proc),
        'Not a procedure: %s' % proc
    )
    args = map(lambda a: _eval(a, env), exp[1:])
    return _apply(proc, args)


def apply_primitive(proc, args):
    check_error(proc.argc < 0 or proc.argc == len(args))
    return apply(proc.operation, args)


def apply_compound(proc, args):
    ext_env = proc.env.extend(
        proc.args,
        args)
    return _eval(proc.body, ext_env)


def build_ast(text):
    from scanner import scanner
    tokens = scanner(text)
    num_tokens = len(tokens)
    tree = []

    def parse_start(start):
        node = []
        i = start
        while i < num_tokens:
            t = tokens[i]
            if t.type == LPAREN:
                child, i = parse_start(i + 1)
                node.append(child)
            elif t.type == RPAREN:
                return node, i + 1
            else:
                node.append(t)
                i += 1
        return node, num_tokens

    tree, end = parse_start(0)
    assert end == num_tokens
    return tree


def eval_seq(exps, env):
    res = void()
    for exp in exps:
        res = _eval(exp, env)
    return res


def _eval(exp, env):
    if is_self_evaluating(exp):
        return exp.value
    elif is_variable(exp):
        return env.lookup(exp.value)
    elif is_definition(exp):
        return eval_define(exp, env)
    elif is_if(exp):
        return eval_if(exp, env)
    elif is_cond(exp):
        return eval_cond(exp, env)
    elif is_lambda(exp):
        return eval_lambda(exp, env)
    elif is_application(exp):
        return eval_application(exp, env)
    else:
        raise_error('unknown exp type -- EVAL: %s' % exp)


def _apply(proc, args):
    if isprimitive(proc):
        return apply_primitive(proc, args)
    elif iscompound(proc):
        return apply_compound(proc, args)
    else:
        check_error(False)


def primitive_procedures():

    def number_add(*ns):
        return sum(ns)

    def number_minus(*ns):
        if len(ns) == 1:
            return -ns[0]
        else:
            return ns[0] - sum(ns[1:])

    def number_product(*ns):
        return reduce(lambda x, y: x * y, ns)

    def number_remainder(a, b):
        return a % b

    def equal(a, b):
        return a == b

    def lt(a, b):
        return a < b

    def le(a, b):
        return a <= b

    def gt(a, b):
        return a > b

    def ge(a, b):
        return a >= b

    PM = [
        ('+', number_add, -1),
        ('-', number_minus, -1),
        ('*', number_product, -1),
        ('%', number_remainder, 2),
        ('=', equal, 2),
        ('<', lt, 2),
        ('<=', le, 2),
        ('>', gt, 2),
        ('>=', ge, 2),
    ]

    def make_primitive(operation, argc):
        return table({
            'type': 'primitive',
            'argc': argc,
            'operation': operation,
        })

    res = []
    for symbol, operation, argc in PM:
        proc = make_primitive(operation, argc)
        res.append((symbol, proc))
    return res


def setup_environment():
    global_env = Env()
    for symbol, value in primitive_procedures():
        global_env.put(symbol, value)
    return global_env
