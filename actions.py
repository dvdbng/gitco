import curses
import os
import shlex
from plumbum.cmd import git, highlight, ls
from plumbum import local, FG

def edit(file):
    editor = 'vim'
    for var in 'GITCO_EDITOR', 'VISUAL', 'EDITOR':
        if var in os.environ:
            editor = os.environ[var]
            break
    args = shlex.split(editor)
    args.append(file)
    with suspend_curses():
        local[args[0]](*args[1:])

def cat_file(file):
    try:
        return (highlight['-O', 'ansi', file])()
    except:
        with open(file, 'r') as f:
            return f.read()

def list_dir(file):
    return ls['--color=always', '-lAhtr']()

class suspend_curses():
    """Context Manager to temporarily leave curses mode"""
    def __enter__(self):
        curses.endwin()

    def __exit__(self, exc_type, exc_val, tb):
        curses.doupdate()

def open_shell_with(contents):
    with suspend_curses():
        local['env']['PREFILL_PROMPT=%s' % contents, 'fish'] & FG

