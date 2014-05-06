#!/usr/bin/env python

import sublime
import sublime_plugin


class TooltipOutputCommand(sublime_plugin.TextCommand):
    def run(self, edit, output='', clear=True):
        if clear:
            region = sublime.Region(0, self.view.size())
            self.view.erase(edit, region)
        self.view.insert(edit, 0, output)

class PythonCodeIntel(sublime_plugin.EventListener):
    def on_close(self, view):
        vid = view.id()
        if vid in completions:
            del completions[vid]
        if vid in languages:
            del languages[vid]
        codeintel_cleanup(view.file_name())

    def on_modified(self, view):
        if not view.settings().get('codeintel_live', True):
            return

        path = view.file_name()
        lang = guess_lang(view, path)
        if not lang or lang.lower() not in [l.lower() for l in view.settings().get('codeintel_live_enabled_languages', [])]:
            return

        view_sel = view.sel()
        if not view_sel:
            return

        sel = view_sel[0]
        pos = sel.end()
        text = view.substr(sublime.Region(pos - 1, pos))
        is_fill_char = (text and text[-1] in cpln_fillup_chars.get(lang, ''))

        # print('on_modified', view.command_history(1), view.command_history(0), view.command_history(-1))
        if (not hasattr(view, 'command_history') or view.command_history(1)[1] is None and (
                view.command_history(0)[0] == 'insert' and (
                    view.command_history(0)[1]['characters'][-1] != '\n'
                ) or
                view.command_history(-1)[0] in ('insert', 'paste') and (
                    view.command_history(0)[0] == 'commit_completion' or
                    view.command_history(0)[0] == 'insert_snippet' and view.command_history(0)[1]['contents'] == '($0)'
                )
        )):
            if view.command_history(0)[0] == 'commit_completion':
                forms = ('calltips',)
            else:
                forms = ('calltips', 'cplns')
            autocomplete(view, 0 if is_fill_char else 200, 50 if is_fill_char else 600, forms, is_fill_char, args=[path, pos, lang])
        else:
            view.run_command('hide_auto_complete')

    def on_selection_modified(self, view):
        global despair, despaired, old_pos
        delay_queue(600)  # on movement, delay queue (to make movement responsive)
        view_sel = view.sel()
        if not view_sel:
            return
        rowcol = view.rowcol(view_sel[0].end())
        if old_pos != rowcol:
            vid = view.id()
            old_pos = rowcol
            despair = 1000
            despaired = True
            status_lock.acquire()
            try:
                slns = [sid for sid, sln in status_lineno.items() if sln != rowcol[0]]
            finally:
                status_lock.release()
            for vid in slns:
                set_status(view, "", lid=vid)

    def on_query_completions(self, view, prefix, locations):
        vid = view.id()
        if vid in completions:
            _completions = completions[vid]
            del completions[vid]
            return _completions
        return []


class CodeIntelAutoComplete(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        view = self.view
        view_sel = view.sel()
        if not view_sel:
            return
        sel = view_sel[0]
        pos = sel.end()
        path = view.file_name()
        lang = guess_lang(view, path)
        if lang:
            autocomplete(view, 0, 0, ('calltips', 'cplns'), True, args=[path, pos, lang])


class GotoPythonDefinition(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        view = self.view
        path = view.file_name()
        lang = guess_lang(view, path)
        if lang:
            view_sel = view.sel()
            if not view_sel:
                return
            sel = view_sel[0]
            pos = sel.end()
            content = view.substr(sublime.Region(0, view.size()))
            file_name = view.file_name()

            def _trigger(defns):
                if defns is not None:
                    defn = defns[0]
                    if defn.name and defn.doc:
                        msg = "%s: %s" % (defn.name, defn.doc)
                        logger(view, 'info', msg, timeout=3000)

                    if defn.path and defn.line:
                        if defn.line != 1 or defn.path != file_name:
                            path = defn.path + ':' + str(defn.line)
                            msg = 'Jumping to: %s' % path
                            log.debug(msg)
                            codeintel_log.debug(msg)

                            window = sublime.active_window()
                            if window.id() not in jump_history_by_window:
                                jump_history_by_window[window.id()] = collections.deque([], HISTORY_SIZE)
                            jump_history = jump_history_by_window[window.id()]

                            # Save current position so we can return to it
                            row, col = view.rowcol(view_sel[0].begin())
                            current_location = "%s:%d" % (file_name, row + 1)
                            jump_history.append(current_location)

                            window.open_file(path, sublime.ENCODED_POSITION)
                            window.open_file(path, sublime.ENCODED_POSITION)
                    elif defn.name:
                        msg = 'Cannot find jumping point to: %s' % defn.name
                        log.debug(msg)
                        codeintel_log.debug(msg)

            codeintel(view, path, content, lang, pos, ('defns',), _trigger)


class BackToPythonDefinition(sublime_plugin.TextCommand):
    def run(self, edit, block=False):

        window = sublime.active_window()
        if window.id() in jump_history_by_window:
            jump_history = jump_history_by_window[window.id()]

            if len(jump_history) > 0:
                previous_location = jump_history.pop()
                window = sublime.active_window()
                window.open_file(previous_location, sublime.ENCODED_POSITION)


class CodeintelCommand(sublime_plugin.TextCommand):
    """command to interact with codeintel"""

    def __init__(self, view):
        self.view = view
        self.help_called = False

    def run_(self, action):
        """method called by default via view.run_command;
           used to dispatch to appropriate method"""
        if not action:
            return

        try:
            lc_action = action.lower()
        except AttributeError:
            return
        if lc_action == 'reset':
            self.reset()
        elif lc_action == 'enable':
            self.enable(True)
        elif lc_action == 'disable':
            self.enable(False)
        elif lc_action == 'on':
            self.on_off(True)
        elif lc_action == 'off':
            self.on_off(False)
        elif lc_action == 'lang-on':
            self.on_off(True, guess_lang(self.view, self.view.file_name()))
        elif lc_action == 'lang-off':
            self.on_off(False, guess_lang(self.view, self.view.file_name()))

    def reset(self):
        """Restores user settings."""
        reload_settings(self.view)
        logger(self.view, 'info', "SublimeCodeIntel Reseted!")

    def enable(self, enable):
        self.view.settings().set('codeintel', enable)
        logger(self.view, 'info', "SublimeCodeIntel %s" % ("Enabled!" if enable else "Disabled",))

    def on_off(self, enable, lang=None):
        """Turns live autocomplete on or off."""
        if lang:
            _codeintel_live_enabled_languages = self.view.settings().get('codeintel_live_enabled_languages', [])
            if lang.lower() in [l.lower() for l in _codeintel_live_enabled_languages]:
                if not enable:
                    _codeintel_live_enabled_languages = [l for l in _codeintel_live_enabled_languages if l.lower() != lang.lower()]
                    self.view.settings().set('codeintel_live_enabled_languages', _codeintel_live_enabled_languages)
                    logger(self.view, 'info', "SublimeCodeIntel Live Autocompletion for %s %s" % (lang, "Enabled!" if enable else "Disabled"))
            else:
                if enable:
                    _codeintel_live_enabled_languages.append(lang)
                    self.view.settings().set('codeintel_live_enabled_languages', _codeintel_live_enabled_languages)
                    logger(self.view, 'info', "SublimeCodeIntel Live Autocompletion for %s %s" % (lang, "Enabled!" if enable else "Disabled"))
        else:
            self.view.settings().set('codeintel_live', enable)
            logger(self.view, 'info', "SublimeCodeIntel Live Autocompletion %s" % ("Enabled!" if enable else "Disabled",))
            # logger(view, 'info', "skip `%s': disabled language" % lang)


class SublimecodeintelWindowCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        view = self.window.active_view()
        return bool(view)

    def run_(self, args):
        pass


class SublimecodeintelCommand(SublimecodeintelWindowCommand):
    def is_enabled(self, active=None):
        enabled = super(SublimecodeintelCommand, self).is_enabled()

        if active is not None:
            view = self.window.active_view()
            enabled = enabled and codeintel_enabled(view, True) == active

        return bool(enabled)

    def run_(self, args={}):
        view = self.window.active_view()
        action = args.get('action', '')

        if view and action:
            view.run_command('codeintel', action)


class SublimecodeintelEnableCommand(SublimecodeintelCommand):
    def is_enabled(self):
        return super(SublimecodeintelEnableCommand, self).is_enabled(False)


class SublimecodeintelDisableCommand(SublimecodeintelCommand):
    def is_enabled(self):
        return super(SublimecodeintelDisableCommand, self).is_enabled(True)


class SublimecodeintelResetCommand(SublimecodeintelCommand):
    def is_enabled(self):
        return super(SublimecodeintelResetCommand, self).is_enabled()


class SublimecodeintelLiveCommand(SublimecodeintelCommand):
    def is_enabled(self, active=True, onlylang=False):
        enabled = super(SublimecodeintelLiveCommand, self).is_enabled(True)

        if active is not None:
            view = self.window.active_view()

            if onlylang:
                enabled = enabled and view.settings().get('codeintel_live', True) is True
                lang = guess_lang(view)
                enabled = enabled and lang and (lang.lower() in [l.lower() for l in view.settings().get('codeintel_live_enabled_languages', [])]) == active
            else:
                enabled = enabled and view.settings().get('codeintel_live', True) == active

        return bool(enabled)


class SublimecodeintelEnableLiveCommand(SublimecodeintelLiveCommand):
    def is_enabled(self):
        return super(SublimecodeintelEnableLiveCommand, self).is_enabled(False, False)


class SublimecodeintelDisableLiveCommand(SublimecodeintelLiveCommand):
    def is_enabled(self):
        return super(SublimecodeintelDisableLiveCommand, self).is_enabled(True, False)


class SublimecodeintelEnableLiveLangCommand(SublimecodeintelLiveCommand):
    def is_enabled(self):
        return super(SublimecodeintelEnableLiveLangCommand, self).is_enabled(False, True)


class SublimecodeintelDisableLiveLangCommand(SublimecodeintelLiveCommand):
    def is_enabled(self):
        return super(SublimecodeintelDisableLiveLangCommand, self).is_enabled(True, True)
