#!/usr/bin/env python

import sys

from tilib import (
    InterpError, build_ast, eval_seq, setup_environment,
    isvoid, tostring,
    dofile
)


def driver_loop(global_env, get_prompt):
    while True:
        try:
            try:
                text = raw_input(get_prompt())
            except EOFError:
                break
            try:
                result = eval_seq(build_ast(text), global_env)
                if not isvoid(result):
                    print tostring(result)
            except InterpError as e:
                print >>sys.stderr, '[Error] %s' % str(e)
            except Exception as e:
                print >>sys.stderr, e
        except KeyboardInterrupt:
            print
    print '\nBye~'


if __name__ == '__main__':
    if len(sys.argv) == 1:
        driver_loop(setup_environment(), lambda: '> ')
    else:
        dofile(sys.argv[1], setup_environment())  # TODO
