#!/usr/bin/env python

class View(object):
    def id(self):
        "id() int Returns a number that uniquely identifies this view."
        pass
    def buffer_id(self):
        "buffer_id() int Returns a number that uniquely identifies the buffer underlying this view."
        pass
    def file_name(self):
        "file_name() String The full name file the file associated with the buffer, or None if it doesn't exist on disk."
        pass
    def name(self):
        "name()	String	The name assigned to the buffer, if any"
        pass
    def set_name(self, name):
        "set_name(name)	None	Assigns a name to the buffer"
        pass
    def is_loading(self):
        "is_loading()	bool	Returns true if the buffer is still loading from disk, and not ready for use."
        pass
    def is_dirty(self):
        "is_dirty()	bool	Returns true if there are any unsaved modifications to the buffer."
        pass
    def is_read_only(self):
        "is_read_only()	bool	Returns true if the buffer may not be modified."
        pass
"set_read_only(value)	None	Sets the read only property on the buffer.	def "
"is_scratch()	bool	Returns true if the buffer is a scratch buffer. Scratch buffers never report as being dirty.
"set_scratch(value)	None	Sets the scratch property on the buffer.
"settings()	Settings	Returns a reference to the views settings object. Any changes to this settings object will be private to this view.
"window()	Window	Returns a reference to the window containing the view.
"run_command(string, <args>)	None	Runs the named TextCommand with the (optional) given arguments.
"size()	int	Returns the number of character in the file.
"substr(region)	String	Returns the contents of the region as a string.
"substr(point)	String	Returns the character to the right of the point.
"insert(edit, point, string)	int	Inserts the given string in the buffer at the specified point. Returns the number of characters inserted: this may be different if tabs are being translated into spaces in the current buffer.
"erase(edit, region)	None	Erases the contents of the region from the buffer.
"replace(edit, region, string)	None	Replaces the contents of the region with the given string.
"sel()	Selection	Returns a reference to the selection.
"line(point)	Region	Returns the line that contains the point.
"line(region)	Region	Returns a modified copy of region such that it starts at the beginning of a line, and ends at the end of a line. Note that it may span several lines.
"full_line(point)	Region	As line(), but the region includes the trailing newline character, if any.
"full_line(region)	Region	As line(), but the region includes the trailing newline character, if any.
"lines(region)	[Region]	Returns a list of lines (in sorted order) intersecting the region.
"split_by_newlines(region)	[Region]	Splits the region up such that each region returned exists on exactly one line.
"word(point)	Region	Returns the word that contains the point.
"word(region)	Region	Returns a modified copy of region such that it starts at the beginning of a word, and ends at the end of a word. Note that it may span several words.
"classify(point)	int	Classifies pt, returning a bitwise OR of zero or more of these flags:

    CLASS_WORD_START
    CLASS_WORD_END
    CLASS_PUNCTUATION_START
    CLASS_PUNCTUATION_END
    CLASS_SUB_WORD_START
    CLASS_SUB_WORD_END
    CLASS_LINE_START
    CLASS_LINE_END
    CLASS_EMPTY_LINE 

    def find_by_class(self, point, forward, classes, <separators>):
        "find_by_class(point, forward, classes, <separators>) Region	Finds the next location after point that matches the given classes. If forward is False, searches backwards instead of forwards. classes is a bitwise OR of the sublime.CLASS_XXX flags. separators may be passed in, to define what characters should be considered to separate words."
        pass
    def expand_by_class(self, point, classes, <separators>):
        "expand_by_class(point, classes, <separators>) Region	Expands point to the left and right, until each side lands on a location that matches classes. classes is a bitwise OR of the sublime.CLASS_XXX flags. separators may be passed in, to define what characters should be considered to separate words."
        pass
    def expand_by_class(region, classes, <separators>)	Region	Expands region to the left and right, until each side lands on a location that matches classes. classes is a bitwise OR of the sublime.CLASS_XXX flags. separators may be passed in, to define what characters should be considered to separate words.
    def find(pattern, fromPosition, <flags>)	Region	Returns the first Region matching the regex pattern, starting from the given point, or None if it can't be found. The optional flags parameter may be sublime.LITERAL, sublime.IGNORECASE, or the two ORed together.
    def find_all(pattern, <flags>, <format>, <extractions>)	[Region]	Returns all (non-overlapping) regions matching the regex pattern. The optional flags parameter may be sublime.LITERAL, sublime.IGNORECASE, or the two ORed together. If a format string is given, then all matches will be formatted with the formatted string and placed into the extractions list.
    def rowcol(point)	(int, int)	Calculates the 0 based line and column numbers of the point.
    def text_point(row, col)	int	Calculates the character offset of the given, 0 based, row and column. Note that 'col' is interpreted as the number of characters to advance past the beginning of the row.
    def set_syntax_file(syntax_file)	None	Changes the syntax used by the view. syntax_file should be a name along the lines of Packages/Python/Python.tmLanguage. To retrieve the current syntax, use view.settings().get('syntax').
    def extract_scope(point)	Region	Returns the extent of the syntax name assigned to the character at the given point.
    def scope_name(point)	String	Returns the syntax name assigned to the character at the given point.
    def score_selector(point, selector)	Int	Matches the selector against the scope at the given location, returning a score. A score of 0 means no match, above 0 means a match. Different selectors may be compared against the same scope: a higher score means the selector is a better match for the scope.
    def find_by_selector(selector)	[Regions]	Finds all regions in the file matching the given selector, returning them as a list.
    def show(point, <show_surrounds>)	None	Scroll the view to show the given point.
    def show(region, <show_surrounds>)	None	Scroll the view to show the given region.
    def show(region_set, <show_surrounds>)	None	Scroll the view to show the given region set.
    def show_at_center(point)	None	Scroll the view to center on the point.
    def show_at_center(region)	None	Scroll the view to center on the region.
    def visible_region()	Region	Returns the currently visible area of the view.
    def viewport_position()	Vector	Returns the offset of the viewport in layout coordinates.
    def set_viewport_position(vector, <animate<)	None	Scrolls the viewport to the given layout position.
    def viewport_extent()	vector	Returns the width and height of the viewport.
    def layout_extent()	vector	Returns the width and height of the layout.
    def text_to_layout(point)	vector	Converts a text position to a layout position
    def layout_to_text(vector)	point	Converts a layout position to a text position
    def line_height()	real	Returns the light height used in the layout
    def em_width()	real	Returns the typical character width used in the layout
    def add_regions(key, [regions], <scope>, <icon>, <flags>)	None	Add a set of regions to the view. If a set of regions already exists with the given key, they will be overwritten. The scope is used to source a color to draw the regions in, it should be the name of a scope, such as "comment" or "string". If the scope is empty, the regions won't be drawn.

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

The underline styles are exclusive, either zero or one of them should be given. If using an underline, DRAW_NO_FILL and DRAW_NO_OUTLINE should generally be passed in.
get_regions(key)	[regions]	Return the regions associated with the given key, if any
erase_regions(key)	None	Removed the named regions
set_status(key, value)	None	Adds the status key to the view. The value will be displayed in the status bar, in a comma separated list of all status values, ordered by key. Setting the value to the empty string will clear the status.
get_status(key)	String	Returns the previously assigned value associated with the key, if any.
erase_status(key)	None	Clears the named status.
command_history(index, <modifying_only>)	(String,Dict,int)	Returns the command name, command arguments, and repeat count for the given history entry, as stored in the undo / redo stack.

Index 0 corresponds to the most recent command, -1 the command before that, and so on. Positive values for index indicate to look in the redo stack for commands. If the undo / redo history doesn't extend far enough, then (None, None, 0) will be returned.

Setting modifying_only to True (the default is False) will only return entries that modified the buffer.
change_count()	int	Returns the current change count. Each time the buffer is modified, the change count is incremented. The change count can be used to determine if the buffer has changed since the last it was inspected.
fold([regions])	bool	Folds the given regions, returning False if they were already folded
fold(region)	bool	Folds the given region, returning False if it was already folded
unfold(region)	[regions]	Unfolds all text in the region, returning the unfolded regions
unfold([regions])	[regions]	Unfolds all text in the regions, returning the unfolded regions
encoding()	String	Returns the encoding currently associated with the file
set_encoding(encoding)	None	Applies a new encoding to the file. This encoding will be used the next time the file is saved.
line_endings()	String	Returns the line endings used by the current file.
set_line_endings(line_endings)	None	Sets the line endings that will be applied when next saving.
overwrite_status()	Bool	Returns the overwrite status, which the user normally toggles via the insert key.
set_overwrite_status(enabled)	None	Sets the overwrite status.
symbols(line_endings)	[(Region, String)]	Extract all the symbols defined in the buffer.
show_popup_menu(items, on_done, <flags>)	None	Shows a pop up menu at the caret, to select an item in a list. on_done will be called once, with the index of the selected item. If the pop up menu was cancelled, on_done will be called with an argument of -1.

Items is an array of strings.

Flags currently only has no option.
