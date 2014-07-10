#!/usr/bin/env python

import socket
try:
    import queue
except ImportError:
    import Queue as queue

from prymatex.qt import  QtCore
from prymatex.gui.codeeditor import CodeEditorAddon
from codeintel.base import (delay_queue, guess_lang, cpln_fillup_chars, 
    autocomplete, set_status, status_lock, editor_close, query_completions,
    thread_finalize)
    
class CodeIntelAddon(CodeEditorAddon):
    def initialize(self, **kwargs):
        super(CodeIntelAddon, self).initialize(**kwargs)
        
        self._rsock, self._wsock = socket.socketpair()
        self._queue = queue.Queue()
        self._notifier = QtCore.QSocketNotifier(self._rsock.fileno(),
                                                QtCore.QSocketNotifier.Read)
        self._notifier.activated.connect(self._handle_command)
        
        self.editor.textChanged.connect(self.on_editor_textChanged)
        self.editor.aboutToClose.connect(self.on_editor_aboutToClose)
        self.application.aboutToQuit.connect(self.on_application_aboutToQuit)
        #self.editor.selectionChanged.connect(self.on_editor_selectionChanged)
        
        self.old_pos = None

    def on_application_aboutToQuit(self):
        thread_finalize()

    def on_editor_textChanged(self):
        # Ver si esta activo el autocompletado
        #if not self.editor.settings()[1].get('codeintel_live', True):
        #    return

        path = self.editor.filePath()
        lang = guess_lang(self, path)
        #if not lang or lang.lower() not in [l.lower() for l in self.editor.settings()[1].get('codeintel_live_enabled_languages', [])]:
        #    return

        text, start, end = self.editor.currentWord()
        if not text:
            return
        pos = self.editor.cursorPosition()

        is_fill_char = (text and text[-1] in cpln_fillup_chars.get(lang, ''))

        # Ahora tengo que ver si no se esta mostrando el completer
        # print('on_modified', self.editor.command_history(1), self.editor.command_history(0), self.editor.command_history(-1))
        #if (not hasattr(self.editor, 'command_history') or self.editor.command_history(1)[1] is None and (
        #        self.editor.command_history(0)[0] == 'insert' and (
        #            self.editor.command_history(0)[1]['characters'][-1] != '\n'
        #        ) or
        #        self.editor.command_history(-1)[0] in ('insert', 'paste') and (
        #            self.editor.command_history(0)[0] == 'commit_completion' or
        #            self.editor.command_history(0)[0] == 'insert_snippet' and self.editor.command_history(0)[1]['contents'] == '($0)'
        #        )
        #)):
        #    if self.editor.command_history(0)[0] == 'commit_completion':
        #        forms = ('calltips',)
        #    else:
        #        forms = ('calltips', 'cplns')
        #    autocomplete(self.editor, 0 if is_fill_char else 200, 50 if is_fill_char else 600, forms, is_fill_char, args=[path, pos, lang])
        #else:
        #    self.editor.run_command('hide_auto_complete')
        forms = ('calltips', 'cplns')
        autocomplete(self, 0 if is_fill_char else 200, 50 if is_fill_char else 600, forms, is_fill_char, args=[path, pos, lang])
        
    def on_editor_selectionChanged(self):
        print("selectionChanged")
        global despair, despaired, old_pos
        delay_queue(600)  # on movement, delay queue (to make movement responsive)
        text, start, end = self.editor.currentWord()
        if not text:
            return

        rowcol = self.editor.cursorPosition()
        if self.old_pos != rowcol:
            vid = id(self.editor)
            self.old_pos = rowcol
            despair = 1000
            despaired = True
            status_lock.acquire()
            try:
                slns = [sid for sid, sln in status_lineno.items() if sln != rowcol[0]]
            finally:
                status_lock.release()
            for vid in slns:
                set_status(self, "", lid=vid)
    
    def on_editor_aboutToClose(self):
        editor_close(self)

    # ------------------ Called by Python thread
    def run_command(self, command, arguments):
        self._queue.put((command, arguments))
        self._wsock.send(b'!')
        
    def set_status(self, lid, status):
        print(lid, status)

    # ------------------ Commands happens in Qt's main thread
    def _handle_command(self):
        self._rsock.recv(1)
        command, arguments = self._queue.get()
        print(command, arguments)
        method = getattr(self, command, None)
        if method is not None:
            method(arguments)

    def auto_complete(self, disable_auto_insert = True, api_completions_only = True,
        next_completion_if_showing = False, auto_complete_commit_on_tab = True):
        completions = query_completions(self)
        self.editor.runCompleter(completions)

    # ------------------ Editor actions
    def settings(self):
        return {}

    def window(self):
        return self.editor.mainWindow()
    
    def syntax_name(self):
        return self.editor.syntax().name

    def file_name(self):
        return self.editor.filePath()

    def content(self):
        return self.editor.toPlainText()

    def current_word(self):
        return self.editor.currentWord()
    
    def cursor_position(self):
        return self.editor.cursorPosition()

    def is_scratch(self):
        return self.editor.isScratch()

    def is_dirty(self):
        return self.editor.isDirty()

