#!/usr/bin/env python

from prymatex.gui.codeeditor import CodeEditorAddon
from codeintel.completer import CodeIndentCompletionModel

class CodeIntelAddon(CodeEditorAddon):
    def initialize(self, **kwargs):
        super(CodeIntelAddon, self).initialize(**kwargs)
        self.editor.completer.insertModel(0, CodeIndentCompletionModel(self))
