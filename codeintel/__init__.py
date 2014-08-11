#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prymatex.gui.codeeditor import CodeEditor
from codeintel.addons import CodeIntelAddon, CodeIntelKeyHelper

def registerPlugin(manager, descriptor):
    manager.registerComponent(CodeIntelAddon, CodeEditor)
    manager.registerComponent(CodeIntelKeyHelper, CodeEditor)
