#!/usr/bin/env python

# Sublime object emulator

class Region(object):
    def __init__(self, a, b, xpos=-1):
        super(Region, self).__init__()
        self.a = a
        self.b = b
        self.xpos = xpos

class Selection(object):
    def __init__(self):
        super(Selection, self).__init__()

class View(object):
    def __init__(self, editor):
        super(View, self).__init__()
        self.editor = editor

    def settings(self):
        return {}

    def project_folders(self):
        project = self.editor.project()
        if project is not None:
            return [ project.path() ]
        return self.editor.application().projectManager.knownProjects

    def is_scratch(self):
        return self.editor.filePath() is not None

    def is_dirty(self):
        return self.editor.isModified()