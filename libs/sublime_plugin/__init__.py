#!/usr/bin/env python

# Sublime Plugins abstraction layer
    
class EventListener(object):
    def on_activated(self, view):
        pass

    def on_deactivated(self, view):
        pass

    def on_pre_save(self, view):
        pass

    def on_post_save(self, view):
        pass
        
    def on_close(self, view):
        pass

    def on_modified(self, view):
        pass

    def on_selection_modified(self, view):
        pass

    def on_query_completions(self, view, prefix, locations):
        pass
    
class ApplicationCommand(object):
    def run(self, *args, **kwargs):
        """None Called when the command is run.
        """
        pass
    
    def is_enabled(self, *args, **kwargs):
        """bool Returns true if the command is able to be run at this time. The default implementation simply always returns True.
        """
        pass
        
    def is_visible(self, *args, **kwargs):
        """bool Returns true if the command should be shown in the menu at this time. The default implementation always returns True.
        """
        pass

    def is_checked(self, *args, **kwargs):
        """bool Returns true if a checkbox should be shown next to the menu item. The .sublime-menu file must have the checkbox attribute set to true for this to be used.
        """
        pass
    
    def description(self, *args, **kwargs):
        """String Returns a description of the command with the given arguments. Used in the menu, if no caption is provided. Return None to get the default description.
        """
        pass

class WindowCommand(object):
    def run(self, *args, **kwargs):
        """None Called when the command is run.
        """
        pass
    
    def is_enabled(self, *args, **kwargs):
        """bool Returns true if the command is able to be run at this time. The default implementation simply always returns True.
        """
        pass
        
    def is_visible(self, *args, **kwargs):
        """bool Returns true if the command should be shown in the menu at this time. The default implementation always returns True.
        """
        pass

    def description(self, *args, **kwargs):
        """String Returns a description of the command with the given arguments. Used in the menu, if no caption is provided. Return None to get the default description.
        """
        pass

class TextCommand(object):
    def run(self, edit, *args, **kwargs):
        """None Called when the command is run.
        """
        pass
    
    def is_enabled(self, *args, **kwargs):
        """bool Returns true if the command is able to be run at this time. The default implementation simply always returns True.
        """
        pass
        
    def is_visible(self, *args, **kwargs):
        """bool Returns true if the command should be shown in the menu at this time. The default implementation always returns True.
        """
        pass

    def description(self, *args, **kwargs):
        """String Returns a description of the command with the given arguments. Used in the menu, if no caption is provided. Return None to get the default description.
        """
        pass
        
