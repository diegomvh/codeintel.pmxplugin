#!/usr/bin/env python

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