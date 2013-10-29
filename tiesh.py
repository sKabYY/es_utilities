#!/usr/bin/env python

from tieslib.tieslib import (
    prompt, setup_ties_environment
)
from interp.interp import driver_loop


def input_prompt():
    return '%s > ' % prompt()


def newenv():
    global_env = setup_ties_environment()
    import sys
    if len(sys.argv) > 1:
        from interp.tilib import dofile
        fns = sys.argv[1:]
        for fn in fns:
            dofile(fn, global_env)
    return global_env

driver_loop(newenv, input_prompt)
