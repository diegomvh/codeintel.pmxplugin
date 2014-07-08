#!/usr/bin/env python

import os
import sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

libs_path = os.path.join(__path__, 'libs')
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

arch_path = os.path.join(__path__, 'arch')
if arch_path not in sys.path:
    sys.path.insert(0, arch_path)

prymatex_path = os.path.abspath(os.path.join(__path__, '../../prymatex'))
if prymatex_path not in sys.path:
    sys.path.insert(0, prymatex_path)
    # Install 
    from prymatex import resources
    resources.installCustomFromThemeMethod()

from codeintel.base import autocomplete

from prymatex.qt.helpers import qapplication
from prymatex.widgets.texteditor import TextEditWidget

class Editor(TextEditWidget):
    def __init__(self, *largs, **kwargs):
        super(Editor, self).__init__(*largs, **kwargs)
        self.path = None
        self.lang = "Python"
        
    def isScratch(self):
        return True
    
    def isDirty(self):
        return False

    def settings(self):
        return {}
    
    def runCompleter(self, suggestions, already_typed=None, callback = None, 
        case_insensitive=True, disable_auto_insert = True, api_completions_only = True,
        next_completion_if_showing = False, auto_complete_commit_on_tab = True):
        print(suggestions)
    
    def keyPressEvent(self, event):
        super(Editor, self).keyPressEvent(event)
        autocomplete(editor, 0, 0, ('calltips', 'cplns'), True, args=[self.path, 
            self.cursorPosition(), self.lang])
        
text = """"""
if __name__ == '__main__':
    app = qapplication()
    editor = Editor()
    editor.setPlainText(text)
    editor.show()
    def exit():
        app.exit()
    app.lastWindowClosed.connect(exit)
    sys.exit(app.exec_())

