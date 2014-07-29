#!/usr/bin/env python

import socket
try:
    import queue
except ImportError:
    import Queue as queue

from prymatex.core.settings import ConfigurableItem
from prymatex.qt import  QtCore
from prymatex.gui.codeeditor import CodeEditorAddon
from codeintel.base import (delay_queue, guess_lang, cpln_fillup_chars, 
    autocomplete, set_status, status_lock, addon_close, query_completions,
    thread_finalize)
    
class CodeIntelAddon(CodeEditorAddon):
    # --------------- Default settings
    
    # Sets the mode in which CodeIntel runs:
    #    true - Enabled (the default).
    #    false - Disabled.
    codeintel = ConfigurableItem(default = True)
    
    # Disable Sublime Text autocomplete:
    sublime_auto_complete = ConfigurableItem(default = True)
    
    # Tooltips method: 
    #    "popup" - Uses Autocomplete popup for tooltips.
    #    "panel" - Uses the output panel for tooltips.
    #    "status" - Uses the status bar for tooltips (was the default).
    codeintel_tooltips = ConfigurableItem(default = "popup")
    
    # Insert functions snippets.
    codeintel_snippets = ConfigurableItem(default = True)
    
    # An array of language names which are enabled.
    codeintel_enabled_languages = ConfigurableItem(default = [
        "JavaScript", "Mason", "XBL", "XUL", "RHTML", "SCSS", "Python", "HTML",
        "Ruby", "Python3", "XML", "Sass", "XSLT", "Django", "HTML5", "Perl", "CSS",
        "Twig", "Less", "Smarty", "Node.js", "Tcl", "TemplateToolkit", "PHP"
    ])

    # Sets the mode in which SublimeCodeIntel's live autocomplete runs:
    #    true - Autocomplete popups as you type (the default).
    #    false - Autocomplete popups only when you request it.
    codeintel_live = ConfigurableItem(default = True)

    # An array of language names to enable.
    codeintel_live_enabled_languages = ConfigurableItem(default = [
        "JavaScript", "Mason", "XBL", "XUL", "RHTML", "SCSS", "Python", "HTML",
        "Ruby", "Python3", "XML", "Sass", "XSLT", "Django", "HTML5", "Perl", "CSS",
        "Twig", "Less", "Smarty", "Node.js", "Tcl", "TemplateToolkit", "PHP"
    ])

    # Maps syntax names to languages. This allows variations on a syntax
    # (for example "Python (Django)") to be used. The key is
    # the base filename of the .tmLanguage syntax files, and the value
    # is the syntax it maps to.
    codeintel_syntax_map = ConfigurableItem(default = {
        "Python Django": "Python"
    })
    
    # Define filters per language to exclude paths from scanning.
    # ex: "JavaScript":["/build/", "/min/"]
    codeintel_scan_exclude_dir = ConfigurableItem(default = {
        "JavaScript":["/build/", "/min/"]
    })

    # ----- Code Scanning: Controls how the Code Intelligence system scans your source code files.
    # Maximum directory depth:
    codeintel_max_recursive_dir_depth = ConfigurableItem(default = 10)

    # Include all files and directories from the project base directory:
    codeintel_scan_files_in_project = ConfigurableItem(default = True)

    # API Catalogs: SublimeCodeIntel uses API catalogs to provide autocomplete and calltips for 3rd-party libraies.
    # Add te libraries that you use in your code. Note: Adding all API catalogs for a particular language can lead to confusing results.
    
    #    Avaliable catalogs:
        # PyWin32 (Python3) (for Python3: Python Extensions for Windows)
        # PyWin32 (for Python: Python Extensions for Windows)
        # Rails (for Ruby: Rails version 1.1.6)
        # jQuery (for JavaScript: jQuery JavaScript library - version 1.9.1)
        # Prototype (for JavaScript: JavaScript framework for web development)
        # dojo (for JavaScript: Dojo Toolkit API - version 1.5.0)
        # Ext_30 (for JavaScript: Ext JavaScript framework - version 3.0)
        # HTML5 (for JavaScript: HTML5 (Canvas, Web Messaging, Microdata))
        # MochiKit (for JavaScript: A lightweight JavaScript library - v1.4.2)
        # Mozilla Toolkit (for JavaScript: Mozilla Toolkit API - version 1.8)
        # XBL (for JavaScript: XBL JavaScript support - version 1.0)
        # YUI (for JavaScript: Yahoo! User Interface Library - v2.8.1)
        # Drupal (for PHP: A full-featured PHP content management/discussion engine -- v5.1)
        # PECL (for PHP: A collection of PHP Extensions)
    codeintel_selected_catalogs = ConfigurableItem(default = [
        "PyWin32", "jQuery", "Rails"
    ])
    
    # Defines a configuration for each language.
    codeintel_config = ConfigurableItem(default = {
        "Python": {
            "env": {
                #"PATH": "/usr/local/bin:/usr/local/sbin:$PATH",
                #"PYTHONPATH": "/usr/local/lib/python2.7/site-packages:/usr/local/lib/python:$PYTHONPATH"
            }
        },
        "JavaScript": {
            "javascriptExtraPaths": [],
            "codeintel_scan_files_in_project": False,
            "codeintel_max_recursive_dir_depth": 2
        },
        "PHP": {
            "phpExtraPaths": [],
            "codeintel_scan_files_in_project": False,
            "codeintel_max_recursive_dir_depth": 5
        }
    })

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
        if not self.codeintel_live:
            return
        
        path = self.editor.filePath()
        lang = guess_lang(self, path)
        if not lang or lang.lower() not in [ l.lower() for l in self.codeintel_live_enabled_languages ]:
            return
            
        pos = self.editor.cursorPosition()
        character = self.editor.document().characterAt(pos - 1)
        is_fill_char = (character and character in cpln_fillup_chars.get(lang, ''))
        
        autocomplete(self, 
            0 if is_fill_char else 200, 
            50 if is_fill_char else 600, 
            ('calltips', 'cplns'), 
            is_fill_char, args=[path, pos, lang])
        
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
        addon_close(self)

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
        self.editor.runCompleter(completions,
            callback = self.completer_callback)

    # ------------------ Completer callback
    def completer_callback(self, suggestion):
        self.editor.defaultCompletionCallback(suggestion)
        print(suggestion)
        
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

    def text(self):
        return self.editor.textUnderCursor(direction = "left", search = True)
    
    def cursor_position(self):
        return self.editor.cursorPosition()

    def is_scratch(self):
        return self.editor.isScratch()

    def is_dirty(self):
        return self.editor.isDirty()

