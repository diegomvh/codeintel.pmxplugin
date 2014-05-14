#!/usr/bin/env python
from __future__ import print_function

import time
import logging
from cStringIO import StringIO

from prymatex.qt import QtCore

from prymatex.gui.codeeditor import CompletionBaseModel

from codeintel2.common import (CodeIntelError, EvalTimeout, LogEvalController,
    TRG_FORM_DEFN, TRG_FORM_CPLN, TRG_FORM_CALLTIP)

from codeintel.base import codeintel_scan, condeintel_log_file
from codeintel.utils import pos2bytes

class CodeIndentCompletionModel(CompletionBaseModel):
    def __init__(self, addon):
        super(CodeIndentCompletionModel, self).__init__(parent = addon)
        self.logger = addon.application.getLogger("codeintel")
    
    def fillModel(self, callback):
        print("arrancamos")

    def isReady(self):
        return False

    def allowOneSuggestion(self, isPrefix):
        return False
        
    def columnCount(self, parent = None):
        return 1
    
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        suggestion = self.suggestions[index.row()]
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            #Es un bundle item
            if index.column() == 0:
                return suggestion.tabTrigger
            elif index.column() == 1:
                return suggestion.name
        elif role == QtCore.Qt.DecorationRole and index.column() == 0:
            return suggestion.icon()
        elif role == QtCore.Qt.ToolTipRole:
            return suggestion.name

    def insertCompletion(self, index):
        suggestion = self.suggestions[index.row()]
        currentWord, start, end = self.editor.currentWord()
        cursor = self.editor.newCursorAtPosition(start, end)
        cursor.removeSelectedText()
        self.editor.insertBundleItem(suggestion)
