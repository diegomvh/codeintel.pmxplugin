#!/usr/bin/env python

from prymatex.gui.codeeditor import CodeEditor
from codeintel import addons

print("Registrando CodeIntel")
__prymatex__.registerComponent(addons.CodeIntelAddon, CodeEditor)