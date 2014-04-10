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
        self.start = time.time()
        self.timeout = 7000
        forms = ('defns', 'cplns', 'calltips')
        path = self.editor.filePath
        content = self.editor.toPlainText()
        pos = self.editor.cursorPosition()
        lang = self.editor.syntax().name
        def _codeintel(buf, msgs):
            cplns = None
            calltips = None
            defns = None
            
            if not buf:
                return [None] * len(forms)

            try:
                trg = getattr(buf, 'preceding_trg_from_pos', lambda p: None)(pos2bytes(content, pos), pos2bytes(content, pos))
                defn_trg = getattr(buf, 'defn_trg_from_pos', lambda p: None)(pos2bytes(content, pos))
            except (CodeIntelError):
                self.logger.exception("Exception! %s:%s (%s)" % (path or '<Unsaved>', pos, lang))
                trg = None
                defn_trg = None
            except:
                self.logger.exception("Exception! %s:%s (%s)" % (path or '<Unsaved>', pos, lang))
                raise
            else:
                eval_log_stream = StringIO()
                _hdlrs = self.logger.handlers
                hdlr = logging.StreamHandler(eval_log_stream)
                hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
                self.logger.handlers = list(_hdlrs) + [hdlr]
                ctlr = LogEvalController(self.logger)
                try:
                    if 'cplns' in forms and trg and trg.form == TRG_FORM_CPLN:
                        cplns = buf.cplns_from_trg(trg, ctlr=ctlr, timeout=20)
                    if 'calltips' in forms and trg and trg.form == TRG_FORM_CALLTIP:
                        calltips = buf.calltips_from_trg(trg, ctlr=ctlr, timeout=20)
                    if 'defns' in forms and defn_trg and defn_trg.form == TRG_FORM_DEFN:
                        defns = buf.defns_from_trg(defn_trg, ctlr=ctlr, timeout=20)
                except EvalTimeout:
                    pass
                finally:
                    self.logger.handlers = _hdlrs
                result = False
                merge = ''
                for msg in reversed(eval_log_stream.getvalue().strip().split('\n')):
                    msg = msg.strip()
                    if msg:
                        try:
                            name, levelname, msg = msg.split(':', 2)
                            name = name.strip()
                            levelname = levelname.strip().lower()
                            msg = msg.strip()
                        except:
                            merge = (msg + ' ' + merge) if merge else msg
                            continue
                        merge = ''
                        if not result and msg.startswith('evaluating '):
                            result = True
            ret = []
            for f in forms:
                if f == 'cplns':
                    ret.append(cplns)
                elif f == 'calltips':
                    ret.append(calltips)
                elif f == 'defns':
                    ret.append(defns)

            total = (time.time() - self.start) * 1000
            if total > 1000:
                timestr = "~%ss" % int(round(total / 1000))
            else:
                timestr = "%sms" % int(round(total))
            if total < self.timeout:
                msg = "Done '%s' CodeIntel! Full CodeIntel took %s" % (lang, timestr)
                #print(msg, file=condeintel_log_file)
                #print(ret)
                callback(self)
            else:
                msg = "Just finished indexing '%s'! Please try again. Full CodeIntel took %s" % (lang, timestr)
                #print(msg, file=condeintel_log_file)

        codeintel_scan(self.editor, path, content, lang,
            callback=_codeintel, pos=pos, forms=forms)

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
