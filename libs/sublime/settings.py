#!/usr/bin/env python

class Settings(object):
    def get(self, name):
        """get(name)    value    Returns the named setting.
        """
        pass
    def get(self, name, default):
        """get(self, name, default)    value    Returns the named setting, or default if it's not defined.
        """
        pass
    def set(self, name, value):
        """    None    Sets the named setting. Only primitive types, lists, and dictionaries are accepted.
        """
        pass
    def erase(name):
        """    None    Removes the named setting. Does not remove it from any parent Settings.
        """
        pass
    def has(self, name):
        """    bool    Returns true iff the named option exists in this set of Settings or one of its parents.
        """
        pass
    def add_on_change(self, key, on_change):
        """    None    Register a callback to be run whenever a setting in this object is changed.
        """
        pass
    def clear_on_change(self, key):
        """    None    Remove all callbacks registered with the given key.
        """
        pass