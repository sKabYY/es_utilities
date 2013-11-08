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

from tilib import dostring, setup_environment

env = setup_environment()
for src in cases:
    print src,
    print '=',
    print dostring(src, env)
