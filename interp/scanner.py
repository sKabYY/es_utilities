# lex #####################################################

# ignore spaces and comma
t_ignore = ', \t\r'

LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
NUMBER = 'NUMBER'
VARIABLE = 'VARIABLE'

tokens = (
    LPAREN,
    RPAREN,
    NUMBER,
    VARIABLE,
)
t_LPAREN = r'\('
t_RPAREN = r'\)'


def t_NUMBER(t):
    r'[\+\-]?\d+\.?\d*'
    try:
        t.value = int(t.value)
    except ValueError:
        t.value = float(t.value)
    return t


def symbol_chars(ext):
    return r'[%sa-zA-Z=<>\*\+\-/%%]' % ext
t_VARIABLE = '%s%s*' % (symbol_chars(''), symbol_chars('0-9'))


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print 'Illegal character "%s"' % t.value[0]
    t.lexer.skip(1)


import ply.lex as lex
__lexer = lex.lex()


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


def scanner(text):
    __lexer.input(text)
    buf = []
    while True:
        tok = __lexer.token()
        if not tok:
            break
        buf.append(tok)
    return map(lex_to_tokens, buf)
###########################################################
