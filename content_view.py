# -*- coding: utf-8 -*-
import ansi
import curses
import re
from color import get_color
from view import View
from ansi import escape_non_printable

def log(*args):
    with open('./logg', 'a') as f:
        for s in args:
            f.write("%s\n" % s)


class ContentView(View):
    def __init__(self, win):
        self.win = win
        self.reset()

    def reset(self):
        self.line = 0

    def paint(self):
        for i, line in enumerate(self.lines[self.line:self.line + self.height]):
            self._draw_line(i, line)

    def _draw_line(self, i, line):
        try:
            self.win.move(i, 0)
        except:
            return
        for chunk in ansi.text_with_fg_bg_attr(ansi.char_slice(line, 0, self.width)):
            if isinstance(chunk, tuple):
                fg, bg, attr = chunk
                self.win.attrset(get_color(fg, bg) | attr)
            else:
                if isinstance(chunk, unicode):
                    chunk = chunk.encode('utf-8')
                chunk = escape_non_printable(chunk)
                try:
                    self.win.addstr(chunk)
                except:
                    self.win.insstr(chunk)

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
        if key in (ord('j'), curses.KEY_DOWN):
            self.move(1)
        elif key in (ord('k'), curses.KEY_UP):
            self.move(-1)
        elif key == ord('g') or key == curses.KEY_HOME:
            self.move(-len(self.lines))
        elif key == ord('G') or key == curses.KEY_END:
            self.move(len(self.lines))
        elif key == ord('J') or key == curses.KEY_NPAGE:
            self.move(int(self.height*0.8))
        elif key == ord('K') or key == curses.KEY_PPAGE:
            self.move(-int(self.height*0.8))
        else:
            return False
        return True
