#!/usr/bin/env python

import sys
import readline

from tilib import (
    InterpError, setup_environment,
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


def driver_loop(newenv, get_prompt):
    readline.parse_and_bind('tab: complete')
    interpreter = Interpreter(dostring, newenv)
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
            except InterpError as e:
                print >>sys.stderr, '[Error] %s' % str(e)
            except Exception as e:
                import traceback
                traceback.print_exc(None, sys.stderr)
        except KeyboardInterrupt:
            print
    print '\nBye~'


if __name__ == '__main__':
    if len(sys.argv) == 1:
        driver_loop(setup_environment, lambda: '> ')
    else:
        dofile(sys.argv[1], setup_environment())  # TODO
