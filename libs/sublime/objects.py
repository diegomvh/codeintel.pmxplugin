#!/usr/bin/env python

# Sublime qt object emulator
# https://www.sublimetext.com/docs/3/api_reference.html

class Region(object):
    def __init__(self, a, b, xpos=-1):
        super(Region, self).__init__()
        self.a = a if a <= b else b
        self.b = b if b >= a else a
        self.xpos = xpos

    def begin(self):
        "int Returns the minimum of a and b."
        return self.a

    def end(self):
        "int Returns the maximum of a and b."
        return self.a

    def size(self):
        "int Returns the number of characters spanned by the region. Always >= 0."
        return abs(self.a - self.b)

    def empty(self):
        "bool Returns true iff begin() == end()."
        return self.a == self.b

    def cover(self, region):
        "Region	Returns a Region spanning both this and the given regions."
        return self.a

    def intersection(self, region):
        "Region	Returns the set intersection of the two regions."
        return self.a

    def intersects(self, region):
        "bool Returns True iff this == region or both include one or more positions in common."
        return self.a

    def contains(self, region_or_point):
        "bool Returns True iff the given region is a subset."
        "Returns True iff begin() <= point <= end()."
        return self.a

class Selection(object):
    def __init__(self):
        super(Selection, self).__init__()
        self.regions = []

    def clear(self):
        "None	Removes all regions."
        pass

    def add(self, region):
        "None	Adds the given region. It will be merged with any intersecting regions already contained within the set."
        pass

    def add_all(self, region_set):
        "None	Adds all regions in the given set."
        pass

    def subtract(self, region):
        "None	Subtracts the region from all regions in the set."
        pass

    def contains(self, region):
        "bool	Returns true iff the given region is a subset."
        pass

class Settings(object):
    def __init__(self):
        super(Settings, self).__init__()

    def get(self, name, default=None):
        return default

    def set(self, name, value):
        pass

    def erase(self, name):
        pass

    def has(self, name):
        pass

    def add_on_change(self, key, on_change):
        pass

    def clear_on_change(self, key):
        pass

class View(object):
    def __init__(self, editor):
        super(View, self).__init__()
        self._editor = editor
        self._listeners = []

    def add_event_listener(self, listener):
        self._listeners.append(listener)
        self._editor.activated.connect(
            lambda view=self: listener.on_activated(view)
        )
        self._editor.deactivated.connect(lambda view=self: listener.on_deactivated(view))
        self._editor.aboutToSave.connect(lambda view=self: listener.on_pre_save(view))
        self._editor.saved.connect(lambda view=self: listener.on_post_save(view))
        self._editor.closed.connect(lambda view=self: listener.on_close(view))
        self._editor.textChanged.connect(lambda view=self: listener.on_modified(view))
        self._editor.selectionChanged.connect(lambda view=self: listener.on_selection_modified(view))
        
    def sel(self):
        return Selection()

    def run_command(self, *args, **kwargs):
        print(args, kwargs)

    def settings(self):
        return {}

    def is_scratch(self):
        return self._editor.filePath() is not None

    def is_dirty(self):
        return self._editor.isModified()
