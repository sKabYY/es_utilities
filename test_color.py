#!/usr/bin/env python


def colorrange(a, b):
    return map(
        lambda i: '\033[%dm' % i,
        range(a, b))


for color in colorrange(80, 100):
    print color + repr(color)
