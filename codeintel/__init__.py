#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prymatex.gui.codeeditor import CodeEditor
from codeintel.addons import CodeIntelAddon
from sublime import setup as setup_sublime

def registerPlugin(manager, descriptor):
    setup_sublime(manager, descriptor)
    manager.registerComponent(CodeIntelAddon, CodeEditor)
