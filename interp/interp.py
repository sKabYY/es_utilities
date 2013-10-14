#!/usr/bin/env python

from lslib import InterpError, isvoid, build_ast, eval_seq, setup_environment


def driver_loop():
    global_env = setup_environment()
    while True:
        try:
            try:
                text = raw_input('> ')
            except EOFError:
                break
            try:
                result = eval_seq(build_ast(text), global_env)
                if not isvoid(result):
                    print result
            except InterpError as e:
                print '[Error] %s' % str(e)
        except KeyboardInterrupt:
            print
    print '\nBye~'


if __name__ == '__main__':
    driver_loop()
