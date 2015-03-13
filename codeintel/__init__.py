#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prymatex.gui.codeeditor import CodeEditor
from codeintel.addons import CodeIntelAddon
from sublime import setup_sublime_adapter

setup_sublime_adapter(manager, descriptor)
__plugin__.registerComponent(CodeIntelAddon, CodeEditor)
