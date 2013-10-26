#!/usr/bin/env python

from terminal.titerminal import driver_loop
from interp.tilib import dostring
from interp.interp import Interpreter
from tieslib.tieslib import prompt, setup_ties_environment

driver_loop(lambda: '%s > ' % prompt(),
            Interpreter(dostring, setup_ties_environment))
