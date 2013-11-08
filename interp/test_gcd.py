#!/usr/bin/env python

from tilib import setup_environment, dostring


text = '''
(define (gcd a b)
  (if (= a 0)
      b
      (gcd (% b a) a)))
(gcd 144 12144)
'''

env = setup_environment()
output = dostring(text, env)
print output
