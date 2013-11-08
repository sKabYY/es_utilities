#!/usr/bin/env python

text = '''
(define (gcd a b)
  (if (= a 0)
      b
      (gcd (remainder b a) a)))
(display "hehe")
(display (gcd 144 12144))
(display 'x)
'x
''x
'('x)
'''

import tiparser
tree = tiparser.parse(text)

from pprint import pprint
pprint(tree)
