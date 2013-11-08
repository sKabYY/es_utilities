#!/usr/bin/env python

tests = '''
(define a 123.3)
(dfe (welj) s12)
'''.strip().split('\n')

from tiparser import scanne
for data in tests:
    print scanne(data)
