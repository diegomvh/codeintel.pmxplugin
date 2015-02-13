#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prymatex.gui.codeeditor import CodeEditor
from codeintel.addons import CodeIntelAddon
from sublime import setup_sublime_adapter

def registerPlugin(manager, descriptor):
    setup_sublime_adapter(manager, descriptor)
    manager.registerComponent(CodeIntelAddon, CodeEditor)
