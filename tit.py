#!/usr/bin/env python

from terminal.titerminal import driver_loop
from interp.tilib import dostring
from interp.interp import Interpreter
from tieslib.tieslib import prompt, setup_ties_environment


def setup_tit_environment():
    global_env = setup_ties_environment()
    import sys
    if len(sys.argv) > 1:
        from interp.tilib import dofile
        fns = sys.argv[1:]
        for fn in fns:
            dofile(fn, global_env)
    return global_env

driver_loop(lambda: '%s > ' % prompt(),
            Interpreter(dostring, setup_tit_environment))
