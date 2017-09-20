import curses
from view import View

class MenuView(View):
    def __init__(self, win):
        self.win = win
        self.selected_index = -1

    def set_options(self, options):
        self.options = options
        self._check_selected_index()
        self.redraw()

    def paint(self):
        for i, line in enumerate(self.options[:self.height]):
            attr = curses.A_STANDOUT if i == self.selected_index else 0
            chars_used = 0
            self.win.move(i, 0)
            for chunk, chunkattrs in line:
                if type(chunk) is unicode:
                    chunk = chunk.encode('utf-8')
                self.win.addstr(chunk[:self.width - chars_used - 1], attr | chunkattrs)
                chars_used += len(chunk)
        self.win.vline(0, self.width-1, '|', self.height)

    def _check_selected_index(self):
        if self.selected_index < 0 and len(self.options):
            self.selected_index = 0
        elif self.selected_index >= len(self.options):
            self.selected_index = len(self.options) - 1

    def move(self, delta):
        self.selected_index += delta
        self._check_selected_index()
        self.redraw()

    def selected_line(self):
        if self.selected_index >= 0:
            return ''.join([x for x, _ in self.options[self.selected_index]])

    def handle(self, key):
        if key == curses.KEY_DOWN:
            self.move(1)
        elif key == curses.KEY_UP:
            self.move(-1)
        else:
            return False
        return True

