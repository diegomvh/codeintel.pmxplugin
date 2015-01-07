#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prymatex.gui.codeeditor import CodeEditor
from codeintel.base import thread_finalize
from codeintel.addons import CodeIntelAddon

def on_application_aboutToQuit():
    thread_finalize()
    
def registerPlugin(manager, descriptor):
    manager.application().aboutToQuit.connect(on_application_aboutToQuit)
    manager.registerComponent(CodeIntelAddon, CodeEditor)
