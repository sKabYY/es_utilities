#!/usr/bin/env python

import sys

from tieslib.tieslib import (
    prompt, setup_ties_environment
)
from interp.interp import newenv_with_preload, driver_loop


def green(s):
    GREEN = '\001\033[92m\002'
    ENDC = '\001\033[0m\002'
    return '%s%s%s' % (GREEN, s, ENDC)


def input_prompt():
    return green('%s\n> ' % prompt())

newenv = newenv_with_preload(setup_ties_environment, sys.argv[1:])
driver_loop(newenv, input_prompt)
