#!/usr/bin/env python

from prymatex.gui.codeeditor import CodeEditor
from codeintel import addons

__prymatex__.registerComponent(addons.CodeIntelAddon, CodeEditor)
