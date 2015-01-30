#!/usr/bin/env python

# Sublime qt abstraction layer

from prymatex.qt.helpers import qapplication

from .objects import *
from .timer import *

pmx = qapplication()

def load_settings(base_name):
    return Settings()

def active_window():
    return pmx.currentWindow()
