#!/usr/bin/env python

from tieslib.tieslib import prompt, setup_ties_environment
from interp.interp import driver_loop


def input_prompt():
    return '%s > ' % prompt()

driver_loop(setup_ties_environment(), input_prompt)
