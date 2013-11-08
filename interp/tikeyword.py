from simpletable import enum


#keywords
KW = enum(
    'define',
    'begin',
    'load',
    'if',
    'cond',
    'lambda',
    'quote',
    #'and',  TODO
    #'or',
    key_mapper=lambda s: s.upper())
