#!/usr/bin/env python

cases = '''
(+ 1 2)
(* 2 3)
(* 2 (+ 3 4))
(* (+ 1 2) (+ 3 4))
(((lambda (x) (lambda (y) (* x y))) 2) 3)
((lambda (x) (* 2 x)) 3)
((lambda (y) (((lambda (y) (lambda (x) (* y 2))) 3) 0)) 4)
'''.strip().split('\n')

from tilib import build_ast, eval_seq, setup_environment

env = setup_environment()
for src in cases:
    print src,
    print '=',
    print eval_seq(build_ast(src), env)
