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
        self.__eval = _eval
        self.__newenv = newenv
        self.reset()

    def reset(self):
        self.__global_env = self.__newenv()

    def eval(self, code):
        return self.__eval(code, self.__global_env)


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
