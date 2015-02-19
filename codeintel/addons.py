#!/usr/bin/env python

import socket
try:
    import queue
except ImportError:
    import Queue as queue

from prymatex.core.settings import ConfigurableItem
from prymatex.qt import  QtCore
from prymatex.gui.codeeditor import CodeEditorAddon
from prymatex.gui.codeeditor.modes import CodeEditorComplitionMode

from sublime import View
from sublime_plugin import InsertSnippetCommand

from codeintel.models import CodeIntelCompletionModel
from codeintel.SublimeCodeIntel import PythonCodeIntel, queue_finalize

class CodeIntelAddon(CodeEditorAddon):

    def initialize(self, **kwargs):
        super(CodeIntelAddon, self).initialize(**kwargs)
        self.setObjectName("CodeIntelAddon")
        
        # Build Sublime abstraction
        self.view = View(self.editor)
        self.view.add_event_listener(PythonCodeIntel())
        self.view.add_command(InsertSnippetCommand())
        self.application().aboutToQuit.connect(self.finalize)
        
        self.complition_model = CodeIntelCompletionModel(parent=self)
        complition = self.editor.findAddon(CodeEditorComplitionMode)
        complition.registerModel(self.complition_model)

    def finalize(self):
        import threading
        print(threading.current_thread().name)
        for thread in threading.enumerate():
            print(thread.name)
            
    # ---------------- Shortcuts
    def contributeToShortcuts(self):
        return [{
            "sequence": ("CodeIntel", "GoToPythonDefinition", "Meta+Alt+Ctrl+Up"),
            "activated": lambda : self.goToPythonDefinition()
        }, {
            "sequence": ("CodeIntel", "BackToPythonDefinition", "Meta+Alt+Ctrl+Left"),
            "activated": lambda : self.backToPythonDefinition()
        }]
