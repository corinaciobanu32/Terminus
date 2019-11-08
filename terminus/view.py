import sublime
import sublime_plugin

import re


def panel_window(view):
    for w in sublime.windows():
        for panel in w.panels():
            v = w.find_output_panel(panel.replace("output.", ""))
            if v and v.id() == view.id():
                return w
    return None


def panel_is_visible(view):
    window = panel_window(view)
    if not window:
        return False
    active_panel = window.active_panel()
    if not active_panel:
        return False
    active_view = window.find_output_panel(active_panel.replace("output.", ""))
    return active_view == view


def view_is_visible(view):
    window = view.window()
    if not window:
        return False
    group, _ = window.get_view_index(view)
    return window.active_view_in_group(group) == view


def view_size(view):
    pixel_width, pixel_height = view.viewport_extent()
    pixel_per_line = view.line_height()
    pixel_per_char = view.em_width()

    if pixel_per_line == 0 or pixel_per_char == 0:
        return (0, 0)

    nb_columns = int(pixel_width / pixel_per_char) - 3
    if nb_columns < 1:
        nb_columns = 1

    nb_rows = int(pixel_height / pixel_per_line)
    if nb_rows < 1:
        nb_rows = 1

    return (nb_rows, nb_columns)


class TerminusInsertCommand(sublime_plugin.TextCommand):

    def run(self, edit, point, character):
        self.view.insert(edit, point, character)


class TerminusTrimTrailingLinesCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view
        lastrow = view.rowcol(view.size())[0]
        if not self.is_empty(lastrow):
            view.insert(edit, view.size(), "\n")
            lastrow = lastrow + 1
        row = lastrow
        while row >= 1:
            if self.is_empty(row-1):
                R = view.line(view.text_point(row, 0))
                a = R.a
                b = R.b
                view.erase(edit, sublime.Region(a-1, b))
                row = row-1
            else:
                break

    def is_empty(self, row):
        view = self.view
        return re.match(r"^\s*$", view.substr(view.line(view.text_point(row, 0))))
