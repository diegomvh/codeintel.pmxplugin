#!/usr/bin/env python

from prymatex.gui.codeeditor import CodeEditorAddon
from codeintel.base import (guess_lang, cpln_fillup_chars, autocomplete)
from codeintel.completer import CodeIndentCompletionModel

class CodeIntelAddon(CodeEditorAddon):
    def initialize(self, **kwargs):
        super(CodeIntelAddon, self).initialize(**kwargs)
        self.editor.completer.registerModel(CodeIndentCompletionModel(self))
        self.editor.textChanged.connect(self.on_editor_textChanged)
        self.editor.selectionChanged.connect(self.on_editor_selectionChanged)
        self.editor.aboutToClose.connect(self.on_editor_aboutToClose)
        
    def on_editor_textChanged(self):
        # Ver si esta activo el autocompletado
        #if not self.editor.settings()[1].get('codeintel_live', True):
        #    return

        path = self.editor.filePath()
        lang = guess_lang(self.editor, path)
        print(lang)
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
        autocomplete(self.editor, 0 if is_fill_char else 200, 50 if is_fill_char else 600, forms, is_fill_char, args=[path, pos, lang])
        
    def on_editor_selectionChanged(self):
        print("selectionChanged")
    
    def on_editor_aboutToClose(self):
        print("aboutToClose")
