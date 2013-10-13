#!/usr/bin/env python

tests = '''
(define a 123.3)
(dfe (welj) s12)
'''.strip().split('\n')

from scanner import scanner
for data in tests:
    print scanner(data)
