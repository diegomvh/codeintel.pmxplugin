#!/usr/bin/env python
# Sublime qt abstraction layer
from prymatex.qt import QtCore

from prymatex.qt.helpers import qapplication

from .edit import Edit
from .region import Region
from .selection import Selection
from .settings import Settings
from .view import View
from .window import Window

pmx = qapplication()
DESCRIPTOR = None

def setup(manager, descriptor):
    global DESCRIPTOR
    DESCRIPTOR = descriptor

def load_settings(base_name):
    global DESCRIPTOR
    print(base_name, DESCRIPTOR, DESCRIPTOR.path)
    return Settings()

def active_window():
    return Window(pmx.currentWindow())

def set_timeout(callback, delay):
    QtCore.QTimer.singleShot(delay, callback)
