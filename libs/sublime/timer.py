#!/usr/bin/env python

from prymatex.qt import QtCore

from prymatex.qt.helpers import qapplication
pmx = qapplication()

def set_timeout(callback, delay):
    QtCore.QTimer.singleShot(delay, callback)
