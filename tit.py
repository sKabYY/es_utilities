#!/usr/bin/env python

import sys

from terminal.titerminal import driver_loop
from interp.tilib import dostring
from interp.interp import Interpreter, newenv_with_preload
from tieslib.tieslib import prompt, setup_ties_environment

setup_tit_environment = newenv_with_preload(
    setup_ties_environment, sys.argv[1:])
driver_loop(lambda: '%s\n> ' % prompt(),
            Interpreter(dostring, setup_tit_environment))
