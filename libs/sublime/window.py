#!/usr/bin/env python

class Window(object):
    def __init__(self, window):
        self._window = window
        
    def id(self):
        """ return int    Returns a number that uniquely identifies this window.
        """
        return id(self._window)

    def new_file(self):
        """ return View    Creates a new file. The returned view will be empty, and its is_loaded method will return True.
        """
        pass
    def open_file(self, file_name, flags=None):
        """ return View    Opens the named file, and returns the corresponding view. If the file is already opened, it will be brought to the front. Note that as file loading is asynchronous, operations on the returned view won't be possible until its is_loading() method returns False.
        The optional flags parameter is a bitwise combination of:
        sublime.ENCODED_POSITION. Indicates the file_name should be searched for a :row or :row:col suffix
        sublime.TRANSIENT. Open the file as a preview only: it won't have a tab assigned it until modified
        """
        pass
    def find_open_file(self, file_name):
        """ return View    Finds the named file in the list of open files, and returns the corresponding View, or None if no such file is open.
        """
        pass
    def active_view(self):
        """ return View    Returns the currently edited view.
        """
        pass
    def active_view_in_group(self, group):
        """ return View    Returns the currently edited view in the given group.
        """
        pass
    def views(self):
        """ return [View]    Returns all open views in the window.
        """
        pass
    def views_in_group(self, group):
        """ return [View]    Returns all open views in the given group.
        """
        pass
    def num_groups(self):
        """ return int    Returns the number of view groups in the window.
        """
        pass
    def active_group(self):
        """ return int    Returns the index of the currently selected group.
        """
        pass
    def focus_group(self, group):
        """ return None    Makes the given group active.
        """
        pass
    def focus_view(self, view):
        """ return None    Switches to the given view.
        """
        pass
    def get_view_index(self, view):
        """ return (group, index)    Returns the group, and index within the group of the view. Returns -1 if not found.
        """
        pass
    def set_view_index(self, view, group, index):
        """ return None    Moves the view to the given group and index.
        """
        pass
    def folders(self):
        """ return [String]    Returns a list of the currently open folders.
        """
        pass
    def project_file_name(self):
        """ return String    Returns name of the currently opened project file, if any.
        """
        pass
    def project_data(self):
        """ return Dictionary    Returns the project data associated with the current window. The data is in the same format as the contents of a .sublime-project file.
        """
        pass
    def set_project_data(self, data):
        """ return None    Updates the project data associated with the current window. If the window is associated with a .sublime-project file, the project file will be updated on disk, otherwise the window will store the data internally.
        """
        pass
    def run_command(self, string, args=None):
        """ return None    Runs the named Command with the (optional) given arguments. Window.run_command is able to run both any sort of command, dispatching the command via input focus.
        """
        pass
    def show_quick_panel(self, items, on_done, flags=None, selected_index=None, on_highlighted=None):
        """ return None    Shows a quick panel, to select an item in a list. on_done will be called once, with the index of the selected item. If the quick panel was cancelled, on_done will be called with an argument of -1.
        Items may be an array of strings, or an array of string arrays. In the latter case, each entry in the quick panel will show multiple rows.
        Flags currently only has one option, sublime.MONOSPACE_FONT
        on_highlighted, if given, will be called every time the highlighted item in the quick panel is changed.
        """
        pass
    def show_input_panel(self, caption, initial_text, on_done, on_change, on_cancel):
        """ return View    Shows the input panel, to collect a line of input from the user. on_done and on_change, if not None, should both be functions that expect a single string argument. on_cancel should be a function that expects no arguments. The view used for the input widget is returned.
        """
        pass
    def create_output_panel(self, name):
        """ return View    Returns the view associated with the named output panel, created it if required. The output panel can be shown by running the show_panel window command, with the panel argument set to the name with an "output." prefix.
        """
        pass
    def lookup_symbol_in_index(self, symbol):
        """ return [Location]    Returns all locations where the symbol is defined across files in the current project.
        """
        pass
    def lookup_symbol_in_open_files(self, symbol):
        """ return [Location]    Returns all locations where the symbol is defined across open files.
        """
        pass