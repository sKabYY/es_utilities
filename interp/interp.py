#!/usr/bin/env python

import sys
import readline

from tierror import TiError

from tilib import (
    keywords,
    setup_environment,
    isvoid, tostring, dostring,
    dofile
)


class Interpreter(object):
    def __init__(self, _eval, newenv):
        '''
        <newenv> is a function which takes no arguments and
        returns an environment. The environment returned
        by <newenv> will be used as the global environment.
        Q: Why this class needs a function instead of
           an Env instance?
        A: The global environment may be changed and
           in some cases, the interpreter may need to reset the environment.
           So, function <newenv> can be used to get a new global environment.
        '''
        self.__eval = _eval
        self.__newenv = newenv
        self.reset()

    def get_env(self):
        try:
            return self.__global_env
        except AttributeError:
            return None

    def reset(self):
        self.__global_env = self.__newenv()

    def eval(self, code):
        return self.__eval(code, self.__global_env)


def newenv_with_preload(newenv, fns):
    '''
    Return a function which will returns initialized environment
    '''
    def __new_newenv():
        '''
        This function uses <newenv> to get a new environment and then
        loads files for each whose filename is in <fns>.
        '''
        env = newenv()
        for fn in fns:
            dofile(fn, env)
        return env
    return __new_newenv


def rlcompleter(get_env):
    '''
    TODO: Rewrite!
    '''

    def complete(text, state):
        env_symbol_set = get_env().symbols()
        all_symbols = list(keywords() | env_symbol_set)
        env_symbols = list(env_symbol_set)
        seps = text.rsplit('(', 1)
        if len(seps) == 1:
            last_expr = seps[0]
            prefix = ''
        elif len(seps) == 2:
            prefix, last_expr = seps
            prefix += '('
        else:
            return
        tokens = last_expr.split()
        if len(tokens) == 0:
            text = ''
        elif len(tokens) > 2:
            return
        else:
            if tokens[0] == 'help':  # help function
                prefix += 'help '
                all_symbols = env_symbols  # Do not search keywords.
                if len(tokens) == 1:
                    text = ''
                else:  # len(tokens) == 2
                    text = tokens[1]
            elif len(tokens) == 1:
                text = tokens[0]
            else:
                return
        for symbol in all_symbols:
            if symbol.startswith(text):
                if state == 0:
                    return '%s%s' % (prefix, symbol)
                else:
                    state -= 1

    return complete


def driver_loop(newenv, get_prompt):
    readline.parse_and_bind('tab: complete')
    readline.set_completer_delims('')
    interpreter = Interpreter(dostring, newenv)
    readline.set_completer(rlcompleter(interpreter.get_env))
    while True:
        try:
            try:
                text = raw_input(get_prompt())
            except EOFError:
                break
            try:
                output = interpreter.eval(text)
                if not isvoid(output):
                    print tostring(output)
            except TiError as e:
                print >>sys.stderr, '[Error] %s' % str(e)
            except Exception as e:
                import traceback
                traceback.print_exc(None, sys.stderr)
        except KeyboardInterrupt:
            print
    print '\nBye~'


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Ti Interpreter Version 0.0'
        print 'Copyleft (c) balabala'
        print
        driver_loop(setup_environment, lambda: '> ')
    else:
        dofile(sys.argv[1], setup_environment())  # TODO
