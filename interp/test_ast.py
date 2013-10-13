#!/usr/bin/env python

text = '''
(define (gcd a b)
  (if (= a 0)
      b
      (gcd (remainder b a) a)))
(display (gcd 144 12144))
'''

import lslib
tree = lslib.build_ast(text)

from pprint import pprint
pprint(tree)
