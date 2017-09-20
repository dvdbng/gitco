import curses
import locale

from content_view import ContentView
from menu_view import MenuView

def log(*args):
    with open('./logg', 'a') as f:
        for s in args:
            f.write("%s\n" % s)

class App:
    def __init__(self, win, handle, update):
        App.app = self
        self.win = win

        self.menu = MenuView(win.subwin(0,0))
        self.content = ContentView(win.subwin(0, 0))
        self.update_fn = update
        self.handle_fn = handle
        self.menu_percent = 0.4 # Percentage of screen covered by menu
        self.size = 0, 0, self.menu_percent
        self.resize()

    def update(self):
        self.update_fn(self.content, self.menu)

    def resize(self):
        h, w = self.win.getmaxyx()
        if (h, w, self.menu_percent) == self.size:
            return
        self.size = h, w, self.menu_percent
        self.win.clear()
        curses.resizeterm(h, w)
        self.win.refresh()

        menu_width = int(self.menu_percent * w)

        self.menu.resize(0, 0, h, menu_width)
        self.content.resize(0, menu_width, h, w - menu_width)
        self.update()

    def set_status(self, status, attr=None):
        h, w = self.win.getmaxyx()
        self.win.addnstr(h - 1, 0, status, w - 1)

    def handle(self, c):
        if c == curses.KEY_RESIZE:
            self.resize()
        elif c == -1:
            self.update()
        elif c == curses.KEY_LEFT and self.menu_percent > .0:
            self.menu_percent = max(.0, self.menu_percent - 0.2)
            self.resize()
        elif c == curses.KEY_RIGHT and self.menu_percent < 1:
            self.menu_percent = min(1.0, self.menu_percent + 0.2)
            self.resize()
        elif self.menu_percent > 0 and self.menu.handle(c) or self.handle_fn(c, self.menu, self.win):
            self.update()
        elif self.menu_percent < 1 and self.content.handle(c):
            pass
        else:
            self.set_status("No binding %s" % curses.keyname(c))

    def loop(self):
        while 1:
            self.handle(self.win.getch())


def main(handle, update):
    locale.setlocale(locale.LC_ALL, '')
    @curses.wrapper
    def main_inner(win):
        curses.curs_set(False)
        curses.use_default_colors()
        win.refresh()
        win.timeout(200)
        App(win, handle, update).loop()
