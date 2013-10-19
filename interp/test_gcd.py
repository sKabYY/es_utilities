#!/usr/bin/env python

from tilib import build_ast, setup_environment, eval_seq


text = '''
(define (gcd a b)
  (if (= a 0)
      b
      (gcd (% b a) a)))
(gcd 144 12144)
'''

env = setup_environment()
output = eval_seq(build_ast(text), env)
print output
