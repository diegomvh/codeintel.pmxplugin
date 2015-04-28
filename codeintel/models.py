#!/usr/bin/env python

from prymatex.qt import QtCore

from prymatex.gui.codeeditor.modes import CompletionBaseModel

class CodeIntelCompletionModel(CompletionBaseModel):
    def __init__(self, **kwargs):
        super(CodeIntelCompletionModel, self).__init__(**kwargs)
        self.suggestions = []
        self.flags = None

    def fill(self):
        self.suggestions, self.flags = self.parent().view.query_completions(
            self.completionPrefix(), 
            [1,2,3,4]
        )
        self.suggestionsReady.emit()

    def isReady(self):
        return bool(self.suggestions)
    
    def activatedCompletion(self, index):
        self.parent().complition.defaultCompletionCallback(
            self.suggestions[index.row()]
        )

    def highlightedCompletion(self, index):
        print("highlightedCompletion")
        
    def setCurrentRow(self, index, completion_count):
        return True
        
    def columnCount(self, parent=None):
        return 1

    def rowCount(self, parent=None):
        return len(self.suggestions)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if row < len(self.suggestions):
            return self.createIndex(row, column, parent)
        else:
            return QtCore.QModelIndex()

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        suggestion = self.suggestions[index.row()]
        if role == QtCore.Qt.DisplayRole:
            if 'display' in suggestion:
                return suggestion['display']
            elif 'title' in suggestion:
                return suggestion['title']
        elif role == QtCore.Qt.EditRole:
            if 'match' in suggestion:
                return suggestion['match']
            elif 'display' in suggestion:
                return suggestion['display']
            elif 'title' in suggestion:
                return suggestion['title']
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0 and 'image' in suggestion:
                return self.editor.resources().get_icon(suggestion['image'])
        elif role == QtCore.Qt.ToolTipRole:
            if 'tooltip' in suggestion:
                if 'tooltip_format' in suggestion:
                    print(suggestion["tooltip_format"])
                return suggestion['tooltip']
        elif role == QtCore.Qt.MatchRole:
            return suggestion['display']
