#!/usr/bin/env python

import sys

from tieslib.tieslib import (
    prompt, setup_ties_environment
)
from interp.interp import newenv_with_preload, driver_loop


def input_prompt():
    return '%s\n> ' % prompt()

### Load and save history file ############################
import os
import readline
histfile = os.path.join(os.path.expanduser('~'), '.ties_history')
try:
    readline.read_history_file(histfile)
except IOError:
    pass
import atexit


def write_history():
    try:
        readline.write_history_file(histfile)
    except IOError:
        pass

atexit.register(write_history)
###########################################################

newenv = newenv_with_preload(setup_ties_environment, sys.argv[1:])
print 'TiES Interpreter Version 0.0'
print 'Copyleft (c) balabala'
print
driver_loop(newenv, input_prompt)
