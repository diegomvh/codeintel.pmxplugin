#!/usr/bin/env python

import socket
try:
    import queue
except ImportError:
    import Queue as queue

from prymatex.core.settings import ConfigurableItem
from prymatex.qt import  QtCore
from prymatex.gui.codeeditor import CodeEditorAddon
from codeintel.base import (gotopython, autocomplete, delay_queue, guess_lang,
    cpln_fillup_chars, status_lock, addon_close, query_completions,
    thread_finalize, update_status, backtopython)
    
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
        self.setObjectName("CodeIntelAddon")

        self._rsock, self._wsock = socket.socketpair()
        self._queue = queue.Queue()
        self._notifier = QtCore.QSocketNotifier(self._rsock.fileno(),
                                                QtCore.QSocketNotifier.Read)
        self._notifier.activated.connect(self._handle_command)
        self._status = {}
        self.old_pos = None
        self.path = None
        self.lang = None
        self.modified = False
        self.cursor_position = None
        self._last_command = None
        
        # Connect
        self.editor.textChanged.connect(self.autocomplete)
        self.editor.aboutToClose.connect(self.on_editor_aboutToClose)
        self.application().aboutToQuit.connect(self.on_application_aboutToQuit)
        self.editor.cursorPositionChanged.connect(self.on_editor_cursorPositionChanged)
        self.editor.syntaxChanged.connect(self.on_editor_syntaxChanged)
        self.editor.filePathChanged.connect(self.on_editor_filePathChanged)
        
        self.editor.registerKeyPressHandler(QtCore.Qt.Key_Space, self.__run_autocomplete)
    
    # ---------------- Shortcuts
    def contributeToShortcuts(self):
        return [{
            "sequence": ("CodeIntel", "GoToPythonDefinition", "Meta+Alt+Ctrl+Up"),
            "activated": lambda : self.goToPythonDefinition()
        }, {
            "sequence": ("CodeIntel", "BackToPythonDefinition", "Meta+Alt+Ctrl+Left"),
            "activated": lambda : self.backToPythonDefinition()
        }]
    
    def goToPythonDefinition(self):
        if self.lang:
            self.content = self.editor.toPlainText()
            pos = self.editor.cursorPosition()

            gotopython(self, self.path, self.content, self.lang, pos)
        
    def backToPythonDefinition(self):
        backtopython(self)
    
    def __run_autocomplete(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            self.autocomplete()
        return False
    # ------------------ Signals
    def on_editor_modificationChanged(self, modified):
        self.modified = modified
        
    def on_editor_filePathChanged(self, path):
        self.path = path

    def on_editor_syntaxChanged(self):
        self.syntax_name = self.editor.syntax().name
        self.lang = guess_lang(self, self.path)
        if not self.lang or self.lang.lower() not in [ l.lower() for l in self.codeintel_live_enabled_languages ]:
            self.lang = None

    def on_application_aboutToQuit(self):
        thread_finalize()
    
    def on_editor_cursorPositionChanged(self):
        self.cursor_position = self.editor.cursorPosition()
        self.text_under_cursor = self.editor.textUnderCursor(direction = "left", search = True)
        self.rowcol = (self.editor.textCursor().blockNumber(), self.editor.textCursor().columnNumber())
        delay_queue(600)  # on movement, delay queue (to make movement responsive)

        if self.old_pos != self.rowcol:
            self.old_pos = self.rowcol
            update_status(self, self.rowcol[0])

    def on_editor_aboutToClose(self):
        addon_close(self)

    def autocomplete(self):
        # Ver si esta activo el autocompletado
        if not self.codeintel_live or not self.lang:
            return
        
        self.content = self.editor.toPlainText()
        pos = self.editor.cursorPosition()
        character = self.content[pos - 1] if pos > 1 else ""
        is_fill_char = (character and character in cpln_fillup_chars.get(self.lang, ''))
        
        if self._last_command == "commit_completion":
            forms = ('calltips',)
        else:
            forms = ('calltips', 'cplns')
        self._last_command = "autocomplete"
        autocomplete(self, 
            0 if is_fill_char else 200, 
            50 if is_fill_char else 600, 
            forms, is_fill_char, args=[self.path, pos, self.lang])

    # ------------------ Called by Python thread
    def run_command(self, command, *args, **kwargs):
        self._queue.put((command, args, kwargs))
        self._wsock.send(b'!')
    
    # ------------------ Commands happens in Qt's main thread
    def _handle_command(self):
        self._rsock.recv(1)
        command, args, kwargs = self._queue.get()
        method = getattr(self, command, None)
        if method is not None:
            method(*args, **kwargs)

    def auto_complete(self, disable_auto_insert = True, api_completions_only = True,
        next_completion_if_showing = False, auto_complete_commit_on_tab = True):
        completions = query_completions(self)
        if completions:
            self.editor.runCompleter(completions, callback = self.completer_callback)

    def set_status(self, lid, status):
        if lid in self._status:
            self._status[lid].setText(status)
        else:
            self._status[lid] = self.editor.showStatus(status)

    def erase_status(self, lid):
        self._status[lid].close()
        del self._status[lid]

    # ------------------ Completer callback
    def completer_callback(self, suggestion):
        self.editor.defaultCompletionCallback(suggestion)
        self._last_command = "commit_completion"
        
    # ------------------ Editor actions
    def settings(self):
        return {}

    def project_folders(self):
        project = self.editor.project()
        if project is not None:
            return [ project.path() ]
        return self.application().projectManager.knownProjects

    def is_scratch(self):
        return self.path is not None

    def is_dirty(self):
        return self.modified
