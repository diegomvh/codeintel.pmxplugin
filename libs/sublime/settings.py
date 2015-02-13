#!/usr/bin/env python

# Sublime custom names
SUBLIME_MAPPING = {
    'syntax': lambda settings, editor: editor and editor.syntax().currentSourcePath()
}

class Settings(object):
    def __init__(self, settings, editor=None):
        self._settings = settings
        self._editor = editor
        
    def get(self, name, default=None):
        """return value Returns the named setting.
        return value Returns the named setting, or default if it's not defined.
        """
        global SUBLIME_MAPPING
        if name in SUBLIME_MAPPING:
            return SUBLIME_MAPPING[name](self._settings, self._editor) or default
        return self._settings.get(name, default)

    def set(self, name, value):
        """return None Sets the named setting. Only primitive types, lists, and dictionaries are accepted.
        """
        self._settings.set(name, value)

    def erase(self, name):
        """return None Removes the named setting. Does not remove it from any parent Settings.
        """
        self._settings.rease(name)

    def has(self, name):
        """return bool Returns true iff the named option exists in this set of Settings or one of its parents.
        """
        self._settings.has(name)

    def add_on_change(self, key, on_change):
        """return None Register a callback to be run whenever a setting in this object is changed.
        """
        self._settings.add_callback(key, on_change)

    def clear_on_change(self, key):
        """return None Remove all callbacks registered with the given key.
        """
        self._settings.remove_callback(key)
