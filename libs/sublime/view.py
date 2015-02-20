#!/usr/bin/env python

import difflib

from prymatex.utils import text as textutils

from .selection import Selection
from .settings import Settings
from .region import Region

class View(object):
    def __init__(self, editor):
        super(View, self).__init__()
        self._editor = editor
        self._command_history = []
        self._command_index = len(self._command_history) - 1
        self._editor.document().contentsChange.connect(self.on_document_contentsChange)
        self._event_listeners = []
        self._commands = {}
        self._content = ""

    def add_event_listener(self, listener):
        self._event_listeners.append(listener)
        self._editor.activated.connect(
            lambda view=self: listener.on_activated(view)
        )
        self._editor.deactivated.connect(lambda view=self: listener.on_deactivated(view))
        self._editor.aboutToSave.connect(lambda view=self: listener.on_pre_save(view))
        self._editor.saved.connect(lambda view=self: listener.on_post_save(view))
        self._editor.closed.connect(lambda view=self: listener.on_close(view))
        self._editor.textChanged.connect(lambda view=self: listener.on_modified(view))
        self._editor.selectionChanged.connect(lambda view=self: listener.on_selection_modified(view))

    def query_completions(self, prefix, locations):
        completions = []
        for listener in self._event_listeners:
            completions.extend(listener.on_query_completions(self, prefix, locations))
        return completions

    def extract_completions(self, prefix, location):
        return []

    def add_command(self, command):
        names = textutils.camelcase_to_text(command.__class__.__name__).split()
        name = "_".join(names[:-1])
        self._commands[name] = command

    def on_document_contentsChange(self, position, charsRemoved, charsAdded):
        text = self._editor.toPlainText()
        if charsRemoved:
            self._command_history.append(
                ('delete', { 'characters': self._content[position:position + charsRemoved] }, 0)
            )
        if text and charsAdded:
            self._command_history.append(
                ('insert', { 'characters': text[position:position + charsAdded] }, 0)
            )
        self._content = text
        self._command_index = len(self._command_history) - 1

    def id(self):
        """id() int Returns a number that uniquely identifies this view."""
        return id(self._editor)

    def buffer_id(self):
        """buffer_id() int Returns a number that uniquely identifies the buffer underlying this view."""
        pass
    def file_name(self):
        """file_name() String The full name file the file associated with the buffer, or None if it doesn't exist on disk."""
        return self._editor.filePath()
    def name(self):
        """name()	String	The name assigned to the buffer, if any"""
        pass
    def set_name(self, name):
        """set_name(name)	None	Assigns a name to the buffer"""
        pass
    def is_loading(self):
        """is_loading()	bool	Returns true if the buffer is still loading from disk, and not ready for use."""
        pass
    def is_dirty(self):
        """is_dirty()	bool	Returns true if there are any unsaved modifications to the buffer."""
        pass    
    def is_read_only(self):
        """is_read_only()	bool	Returns true if the buffer may not be modified."""
        pass
    def set_read_only(self, value):
        """return None	Sets the read only property on the buffer."""
        pass
    def is_scratch(self):
        """return bool	Returns true if the buffer is a scratch buffer. Scratch buffers never report as being dirty."""
        pass
    def set_scratch(self, value):
        """return None	Sets the scratch property on the buffer."""
        pass
    def settings(self):
        """return Settings	Returns a reference to the views settings object. Any changes to this settings object will be private to this view."""
        return Settings(self._editor.settings(), self._editor)

    def window(self):
        """return Window	Returns a reference to the window containing the view."""
        pass
    def run_command(self, string, args=None):
        """return None	Runs the named TextCommand with the (optional) given arguments."""
        self._editor.runCommand(string, args)

    def size(self):
        """return int	Returns the number of character in the file."""
        pass
        
    def substr(self, region):
        """return String Returns the contents of the region as a string.
        return String Returns the character to the right of the point.
        """
        if isinstance(region, Region):
            return self._editor.toPlainTextWithEol()[region[0]:region[1]]
        return self._editor.document().characterAt(point)

    def insert(self, edit, point, string):
        """return int	Inserts the given string in the buffer at the specified point. Returns the number of characters inserted: this may be different if tabs are being translated into spaces in the current buffer."""
        pass
    def erase(self, edit, region):
        """return None	Erases the contents of the region from the buffer."""
        pass
    def replace(self, edit, region, string):
        """return None	Replaces the contents of the region with the given string."""
        pass

    def sel(self):
        """return Selection	Returns a reference to the selection."""
        sel = Selection()
        for cursor in self._editor.textCursors():
            sel.add(Region(cursor.position(), cursor.anchor()))    
        return sel

    def line(self, point_region):
        """return Region	Returns the line that contains the point.
        return Region	Returns a modified copy of region such that it starts at the beginning of a line, and ends at the end of a line. Note that it may span several lines.
        """
        if isinstance(point_region, Region):
            cursor = self._editor.newCursorAtPosition(point_region[0], point_region[1])
            block_start, block_end = self._editor.selectionBlockStartEnd(cursor)
            return Region(block_start.position(), block_end.position() + block_end.length())
        block = self._editor.document().findBlock(point_region)
        return Region(block.position(), block.position() + block.length())

    def full_line(self, point_region):
        """return Region	As line(), but the region includes the trailing newline character, if any.
        return Region	As line(), but the region includes the trailing newline character, if any.
        """
        pass
    
    def lines(self, region):
        """return [Region]	Returns a list of lines (in sorted order) intersecting the region."""
        pass
    def split_by_newlines(self, region):
        """return [Region]	Splits the region up such that each region returned exists on exactly one line."""
        pass
    def word(self, point):
        """return Region	Returns the word that contains the point."""
        pass
    def word(self, region):
        """return Region	Returns a modified copy of region such that it starts at the beginning of a word, and ends at the end of a word. Note that it may span several words."""
        pass
    def classify(self, point):
        """return int Classifies pt, returning a bitwise OR of zero or more of these flags:
        CLASS_WORD_START
        CLASS_WORD_END
        CLASS_PUNCTUATION_START
        CLASS_PUNCTUATION_END
        CLASS_SUB_WORD_START
        CLASS_SUB_WORD_END
        CLASS_LINE_START
        CLASS_LINE_END
        CLASS_EMPTY_LINE"""
        pass
    def find_by_class(self, point, forward, classes, separators=None):
        """find_by_class(point, forward, classes, <separators>) Region	Finds the next location after point that matches the given classes. If forward is False, searches backwards instead of forwards. classes is a bitwise OR of the sublime.CLASS_XXX flags. separators may be passed in, to define what characters should be considered to separate words."""
        pass
    def expand_by_class(self, point, classes, separators=None):
        "expand_by_class(point, classes, <separators>) Region	Expands point to the left and right, until each side lands on a location that matches classes. classes is a bitwise OR of the sublime.CLASS_XXX flags. separators may be passed in, to define what characters should be considered to separate words."
        pass
    def expand_by_class(self, region, classes, separators=None):
        """return Region	Expands region to the left and right, until each side lands on a location that matches classes. classes is a bitwise OR of the sublime.CLASS_XXX flags. separators may be passed in, to define what characters should be considered to separate words."""
        pass
    def find(self, pattern, fromPosition, flags=None):
        """return Region	Returns the first Region matching the regex pattern, starting from the given point, or None if it can't be found. The optional flags parameter may be sublime.LITERAL, sublime.IGNORECASE, or the two ORed together."""
        pass
    def find_all(self, pattern, flags=None, format=None, extractions=None):
        """return [Region]	Returns all (non-overlapping) regions matching the regex pattern. The optional flags parameter may be sublime.LITERAL, sublime.IGNORECASE, or the two ORed together. If a format string is given, then all matches will be formatted with the formatted string and placed into the extractions list."""
        pass

    def rowcol(self, point):
        """return (int, int)	Calculates the 0 based line and column numbers of the point."""
        cursor = self._editor.newCursorAtPosition(point)
        return cursor.blockNumber(), cursor.positionInBlock()
        
    def text_point(self, row, col):
        """return int	Calculates the character offset of the given, 0 based, row and column. Note that 'col' is interpreted as the number of characters to advance past the beginning of the row."""
        pass
    def set_syntax_file(self, syntax_file):
        """return None	Changes the syntax used by the view. syntax_file should be a name along the lines of Packages/Python/Python.tmLanguage. To retrieve the current syntax, use view.settings().get('syntax')."""
        pass
    def extract_scope(self, point):
        """return Region	Returns the extent of the syntax name assigned to the character at the given point."""
        pass

    def scope_name(self, point):
        """return String Returns the syntax name assigned to the character at the given point."""
        return str(self._editor.scope(self._editor.newCursorAtPosition(point))[1])
        
    def score_selector(self, point, selector):
        """return Int Matches the selector against the scope at the given location, returning a score. A score of 0 means no match, above 0 means a match. Different selectors may be compared against the same scope: a higher score means the selector is a better match for the scope."""
        pass
    def find_by_selector(self, selector):
        """return [Regions]	Finds all regions in the file matching the given selector, returning them as a list."""
        pass
    def show(self, point, show_surrounds):
        """return None	Scroll the view to show the given point."""
        pass
    def show(self, region, show_surrounds):
        """return None	Scroll the view to show the given region."""
        pass
    def show(self, region_set, show_surrounds):
        """return None	Scroll the view to show the given region set."""
        pass
    def show_at_center(self, point):
        """return None	Scroll the view to center on the point."""
        pass
    def show_at_center(self, region):
        """return None	Scroll the view to center on the region."""
        pass
    def visible_region(self):
        """return Region	Returns the currently visible area of the view."""
        pass
    def viewport_position(self):
        """return Vector	Returns the offset of the viewport in layout coordinates."""
        pass
    def set_viewport_position(self, vector, animate=None):
        """return None	Scrolls the viewport to the given layout position."""
        pass
    def viewport_extent(self):
        """return vector	Returns the width and height of the viewport."""
        pass
    def layout_extent(self):
        """return vector	Returns the width and height of the layout."""
        pass
    def text_to_layout(self, point):
        """return vector	Converts a text position to a layout position"""
        pass
    def layout_to_text(self, vector):
        """return point	Converts a layout position to a text position"""
        pass
    def line_height(self):
        """return real	Returns the light height used in the layout"""
        pass
    def em_width(self):
        """return real	Returns the typical character width used in the layout"""
        pass
    def add_regions(self, key, regions, scope=None, icon=None, flags=None):
        """return None	Add a set of regions to the view. If a set of regions already exists with the given key, they will be overwritten. The scope is used to source a color to draw the regions in, it should be the name of a scope, such as "comment" or "string". If the scope is empty, the regions won't be drawn.

The optional icon name, if given, will draw the named icons in the gutter next to each region. The icon will be tinted using the color associated with the scope. Valid icon names are dot, circle, bookmark and cross. The icon name may also be a full package relative path, such as Packages/Theme - Default/dot.png.

The optional flags parameter is a bitwise combination of:

    sublime.DRAW_EMPTY. Draw empty regions with a vertical bar. By default, they aren't drawn at all.
    sublime.HIDE_ON_MINIMAP. Don't show the regions on the minimap.
    sublime.DRAW_EMPTY_AS_OVERWRITE. Draw empty regions with a horizontal bar instead of a vertical one.
    sublime.DRAW_NO_FILL. Disable filling the regions, leaving only the outline.
    sublime.DRAW_NO_OUTLINE. Disable drawing the outline of the regions.
    sublime.DRAW_SOLID_UNDERLINE. Draw a solid underline below the regions.
    sublime.DRAW_STIPPLED_UNDERLINE. Draw a stippled underline below the regions.
    sublime.DRAW_SQUIGGLY_UNDERLINE. Draw a squiggly underline below the regions.
    sublime.PERSISTENT. Save the regions in the session.
    sublime.HIDDEN. Don't draw the regions. 

The underline styles are exclusive, either zero or one of them should be given. If using an underline, DRAW_NO_FILL and DRAW_NO_OUTLINE should generally be passed in."""
        pass
    def get_regions(self, key):
        """return [regions]	Return the regions associated with the given key, if any"""
        pass
    def erase_regions(self, key):
        """return None	Removed the named regions"""
        pass
    def set_status(self, key, value):
        """return None	Adds the status key to the view. The value will be displayed in the status bar, in a comma separated list of all status values, ordered by key. Setting the value to the empty string will clear the status."""
        pass
    def get_status(self, key):
        """return String	Returns the previously assigned value associated with the key, if any."""
        pass
    def erase_status(self, key):
        """return None	Clears the named status."""
        pass
    def command_history(self, index, modifying_only=None):
        """return (String,Dict,int)	Returns the command name, command arguments, and repeat count for the given history entry, as stored in the undo / redo stack.
Index 0 corresponds to the most recent command, -1 the command before that, and so on. Positive values for index indicate to look in the redo stack for commands. If the undo / redo history doesn't extend far enough, then (None, None, 0) will be returned.

Setting modifying_only to True (the default is False) will only return entries that modified the buffer."""
        index = self._command_index + index
        if 0 <= index < len(self._command_history):
            return self._command_history[index]
        return (None, None, 0)

    def change_count(self):
        """return int	Returns the current change count. Each time the buffer is modified, the change count is incremented. The change count can be used to determine if the buffer has changed since the last it was inspected."""
        pass
    def fold(self, regions):
        """return bool	Folds the given regions, returning False if they were already folded"""
        pass
    def fold(self, region):
        """return bool	Folds the given region, returning False if it was already folded"""
        pass
    def unfold(self, region):
        """return [regions]	Unfolds all text in the region, returning the unfolded regions"""
        pass
    def unfold(self, regions):
        """return [regions]	Unfolds all text in the regions, returning the unfolded regions"""
        pass
    def encoding(self):
        """return String	Returns the encoding currently associated with the file"""
        pass
    def set_encoding(self, encoding):
        """return None	Applies a new encoding to the file. This encoding will be used the next time the file is saved."""
        pass
    def line_endings(self):
        """return String	Returns the line endings used by the current file."""
        pass
    def set_line_endings(self, line_endings):
        """return None	Sets the line endings that will be applied when next saving."""
        pass
    def overwrite_status(self):
        """return Bool	Returns the overwrite status, which the user normally toggles via the insert key."""
        pass
    def set_overwrite_status(self, enabled):
        """return None	Sets the overwrite status."""
        pass
    def symbols(self, line_endings):
        """return [(Region, String)]	Extract all the symbols defined in the buffer."""
        pass
    def show_popup_menu(self, items, on_done, flags=None):
        """return None	Shows a pop up menu at the caret, to select an item in a list. on_done will be called once, with the index of the selected item. If the pop up menu was cancelled, on_done will be called with an argument of -1.
        Items is an array of strings.
        Flags currently only has no option."""
        pass
