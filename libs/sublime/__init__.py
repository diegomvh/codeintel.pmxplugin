#!/usr/bin/env python
# Sublime qt abstraction layer
from prymatex.qt import QtCore

from prymatex.qt.helpers import qapplication

from .window import Window
from .settings import Settings

pmx = qapplication()

def load_settings(base_name):
    return Settings()

def active_window():
    return Window(pmx.currentWindow())

def set_timeout(callback, delay):
    QtCore.QTimer.singleShot(delay, callback)