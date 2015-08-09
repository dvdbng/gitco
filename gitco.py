#!/usr/bin/env python

from plumbum.cmd import git, highlight, ls
from color import get_color

import ansi

import curses
import os
import re
import sys

def git_status():
    return filter(None, (git["status", "--porcelain"])().split("\n"))

def git_diff(file):
    return (git["diff", "--color=always", "--", file])()

def cat_file(file):
    try:
        return (highlight['-O', 'ansi', file])()
    except:
        with open(file, 'r') as f:
            return f.read()

def list_dir(file):
    return ls['--color=always', '-lAhtr']()

MENU_PC = 0.4 # Percentage of screen that is menu (the rest is diff)

class MenuView(object):
    def __init__(self, mainwin, screenw, screenh):
        self.width = int(screenw*MENU_PC)
        self.left = 0
        self.top = 0
        self.height = screenh
        self.win = mainwin.subwin(self.height, self.width, self.top, self.left)
        self.selected_index = -1

    def set_options(self, options):
        self.options = options
        self._check_selected_index()
        self.redraw()

    def redraw(self):
        self.win.erase()

        for i, line in enumerate(self.options[:self.height]):
            attr = curses.A_STANDOUT if i == self.selected_index else 0
            self.win.addnstr(i, 0, line, self.width - 1, attr)

        self.win.vline(0, self.width-1, '|', self.height)
        self.win.refresh()

    def _check_selected_index(self):
        if self.selected_index < 0 and len(self.options):
            self.selected_index = 0
        elif self.selected_index >= len(self.options):
            self.selected_index = len(self.options) - 1

    def move(self, delta):
        self.selected_index += delta
        self._check_selected_index()
        self.redraw()

    def selected_file(self):
        if self.selected_index >= 0:
            return self.options[self.selected_index][3:]

    def selected_status(self):
        if self.selected_index >= 0:
            return self.options[self.selected_index][:2]

    def handle(self, key):
        if key == curses.KEY_DOWN:
            self.move(1)
        elif key == curses.KEY_UP:
            self.move(-1)
        else:
            return False
        return True

control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
control_char_re = re.compile('[%s]' % re.escape(control_chars))
def _repl_control_char(c):
    return repr(c.group())[1:-1]
def escape_non_printable(s):
    return control_char_re.sub('?', s)

class DiffView(object):
    def __init__(self, mainwin, screenw, screenh):
        self.width = int(screenw*(1-MENU_PC))
        self.left = int(screenw*MENU_PC)
        self.top = 0
        self.height = screenh
        self.win = mainwin.subwin(self.height, self.width, self.top, self.left)
        self.reset()
        self.proc = None

    def reset(self):
        self.line = 0

    def redraw(self):
        self.win.erase()
        for i, line in enumerate(self.lines[self.line:self.line + self.height]):
            self._draw_line(i, line)
        self.win.refresh()

    def _draw_line(self, i, line):
        try:
            self.win.move(i, 0)
        except:
            return
        col = 0
        for chunk in ansi.text_with_fg_bg_attr(line[:self.width]):
            if isinstance(chunk, tuple):
                fg, bg, attr = chunk
                self.win.attrset(curses.color_pair(get_color(fg, bg)) | attr)
            else:
                chunk = escape_non_printable(str(chunk))[:self.width-col-1]
                try:
                    self.win.addstr(chunk)
                except:
                    raise Exception('Addstring %s %s %s %s' % (repr(chunk), len(chunk), col, self.width))
                col += len(chunk)
                if col >= self.width:
                    return

    def set_text(self, text):
        self.reset()
        lines = text.split('\n')
        self.lines = lines
        self.redraw()

    def move(self, lines):
        self.line += lines
        if self.line < 0:
            self.line = 0
        elif self.line > len(self.lines) - self.height:
            self.line = len(self.lines) - self.height
        self.redraw()

    def handle(self, key):
        if key == ord('j'):
            self.move(1)
        elif key == ord('k'):
            self.move(-1)
        elif key == ord('g') or key == curses.KEY_HOME:
            self.move(-len(self.lines))
        elif key == ord('G') or key == curses.KEY_END:
            self.move(len(self.lines))
        elif key == ord('J') or key == curses.KEY_NPAGE:
            self.move(int(self.height*0.8))
        elif key == ord('K') or key == curses.KEY_PPAGE:
            self.move(-int(self.height*0.8))

def update(diff, menu):
    menu.set_options(git_status())
    file = menu.selected_file()
    status = menu.selected_status()
    if file:
        if status in ('??', 'A '):
            if os.path.isdir(file):
                text = list_dir(file)
            else:
                text = cat_file(file)
        else:
            text = git_diff(file)
    else:
        text = "No file selected"
    diff.set_text(text)

def handle(key, menu):
    file = menu.selected_file()
    if key == ord('a'):
        git['add', '--', file]()
    elif key == ord('c'):
        git["checkout", '--', file]()
    elif key == ord('r'):
        git["reset", 'HEAD', '--', file]()
    elif key == ord('q'):
        sys.exit(0)
    else:
        return False
    return True

@curses.wrapper
def main(win):
    curses.use_default_colors()
    win.refresh()

    h, w = win.getmaxyx()

    diff_view = DiffView(win, w, h)
    menu = MenuView(win, w, h)
    update(diff_view, menu)

    while 1:
        c = win.getch()
        if menu.handle(c) or handle(c, menu):
            update(diff_view, menu)
        else:
            diff_view.handle(c)

