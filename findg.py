#!/usr/bin/python
import curses
import os
import re
import shlex
import sys
import thread

import start_app
from actions import edit, suspend_curses, list_dir, cat_file, open_shell_with
from color import get_color

#while not os.path.exists('.git'):
#    os.chdir('..')

from plumbum.cmd import rm
from plumbum import local, FG

def get_ignored_dirs():
    ignored = []
    for line in local['ack-grep']['--dump']().split('\n'):
        for delim in '--ignore-directory=is:', '--ignore-dir=':
            if delim in line:
                ignored.append(line.split(delim, 1)[1])
    return set(ignored)


def highlight(line, regexp):
    color = get_color(curses.COLOR_RED, -1) | curses.A_BOLD
    match = regexp.search(line)
    if match:
        return [(line[:match.start(0)], 0), (match.group(0), color), (line[match.end(0):], 0)]
    else:
        return [(line, 0)]



class Findg():
    def __init__(self):
        self.results = None
        self.loading = True
        self.currently_scanning = '.'
        thread.start_new_thread(self.load_results, ())

    def get_results(self):
        regexp = re.compile(sys.argv[1])
        results = []
        ignored_dirs = get_ignored_dirs()
        dir_filter = lambda dir: dir not in ignored_dirs
        for dirname, subdirs, file_list in os.walk('.', topdown=True):
            subdirs[:] = filter(dir_filter, subdirs)
            self.currently_scanning = dirname
            for file in file_list:
                if regexp.search(os.path.join(dirname, file)):
                    yield highlight(os.path.join(dirname, file), regexp)

    def load_results(self):
        if self.results is None:
            self.results = []
            for result in self.get_results():
                self.results.append(result)
                if len(self.results) > 150:
                    break
            self.loading = False

    def update(self, diff, menu):
        loading = [[('Finding... (Currently scanning %s)' % self.currently_scanning, get_color(curses.COLOR_BLUE, -1))]] if self.loading else []
        menu.set_options(self.results + loading)
        file = menu.selected_line()
        if file:
            if os.path.isdir(file):
                text = list_dir(file)
            elif os.path.exists(file):
                text = cat_file(file)
            else:
                text = "File doesn't exist %s" % file
        else:
            text = "No file selected"
        diff.set_text(text)


    def handle(self, key, menu, win):
        file = menu.selected_line()
        if key == ord('r'):
            c = win.getch()
            if c == ord('y'):
                rm[file]()
        elif key == curses.KEY_F5:
            pass  # Handling the key will cause the data to update
        elif key in (ord('e'), ord('E')):
            edit(file)
            if key == ord('e'):
                sys.exit(0)
        elif key == ord('!'):
            open_shell_with(' %s ; and exit' % file)
        elif key == ord('q'):
            sys.exit(0)
        else:
            return False
        return True


findg = Findg()
start_app.main(findg.handle, findg.update)
