from tierror import TiError


class ParseError(TiError):
    pass


def raise_parse_error(msg):
    raise ParseError(msg)

# lex #####################################################

# ignore spaces and comma
t_ignore = ' \t\r'

LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
NUMBER = 'NUMBER'
STRING = 'STRING'
QUOTE = 'QUOTE'
SYMBOL = 'SYMBOL'

tokens = (
    LPAREN,
    RPAREN,
    NUMBER,
    STRING,
    QUOTE,
    SYMBOL,
)


t_LPAREN = r'\('
t_RPAREN = r'\)'


def t_comment(t):
    r';.*'
    t.lexer.lineno += 1


def t_NUMBER(t):
    r'[\+\-]?\d+\.?\d*'
    try:
        t.value = int(t.value)
    except ValueError:
        t.value = float(t.value)
    return t


def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t


t_QUOTE = '\''


def symbol_chars(ext):
    return r'[%sa-zA-Z=<>\*\+\-/%%]' % ext

t_SYMBOL = '%s%s*' % (symbol_chars(''), symbol_chars(r'0-9!\?'))


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    raise_parse_error('Illegal character "%s"' % t.value[0])


import ply.lex as lex
__global_lexer = lex.lex()


def new_lexer():
    return __global_lexer.clone()


class Token(object):
    def __init__(self, t, v, lineno):
        self.type = t
        self.value = v
        self.lineno = lineno

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s, "%s", %s>' % (self.type, self.value, self.lineno)


def lex_to_tokens(t):
    return Token(t.type, t.value, t.lineno)


def scanne(text):
    lexer = new_lexer()
    lexer.input(text)
    buf = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        buf.append(tok)
    return map(lex_to_tokens, buf)
###########################################################


# parse ###################################################
from tikeyword import KW


def parse(text):
    tokens = scanne(text)
    token_tree = build_tree(tokens)
    translated_tree = translate_quote(token_tree)
    return parse_tree(translated_tree)


def mk_symbol_token(s, lineno):
    return Token(SYMBOL, s, lineno)


def build_tree(tokens):
    num_tokens = len(tokens)
    token_tree = []

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

    def is_all_rparen(start, end):
        r'''
        Returns whether all the tokens have type RPAREN in tokens[start:end]
        '''
        return all(map(
            lambda i: tokens[i].type == RPAREN,
            xrange(start, end)))

    token_tree, end = parse_start(0)

    if not (end == num_tokens or is_all_rparen(end, num_tokens)):
        raise_parse_error("Syntax error: check the parentheses")

    return token_tree


def translate_quote(lst):
    n = len(lst)

    def __iter(start):
        if start < n:
            node = lst[start]
            rest = __iter(start + 1)
            if isinstance(node, list):
                rest.insert(0, translate_quote(node))
            elif node.type == QUOTE:
                if start + 1 >= n:
                    raise_parse_error("Syntaxe error: nothing follows quote")
                quote_node = mk_symbol_token(KW.QUOTE, node.lineno)
                rest[0] = [quote_node, rest[0]]
            else:
                rest.insert(0, node)
            return rest
        else:
            return []

    return __iter(0)


from titype import (
    mknumber, mkstring, mksymbol, mklist
)


def parse_tree(node):

    def parse_token(token):
        if token.type == NUMBER:
            return mknumber(token.value)
        elif token.type == STRING:
            return mkstring(token.value)
        elif token.type == SYMBOL:
            return mksymbol(token.value)
        else:
            raise_parse_error('Unknown token type: %s' % token.type)

    if isinstance(node, list):
        buf = mklist()
        for n in node:
            buf.append(parse_tree(n))
        return buf
    else:
        return parse_token(node)
