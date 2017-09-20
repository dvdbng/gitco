#!/usr/bin/python
import curses
import os
import sys
import time

import start_app
from actions import edit, suspend_curses, list_dir, cat_file

while not os.path.exists('.git'):
    os.chdir('..')

from plumbum.cmd import git, hub
from plumbum import local, FG

treeish = None if len(sys.argv) == 1 else sys.argv[1]

def git_status():
    if treeish:
        lines = git['diff-tree', '--no-commit-id', '--name-status', '-r', treeish]().split('\n')
        lines = ['   ' + line[2:] for line in lines]
    else:
        lines = (git["status", "--porcelain"])().split("\n")
    return [[(line, 0)] for line in lines if line]


def git_diff(file):
    if treeish:
        return git["show", "--color=always", treeish, '--', file]()
    else:
        return (git["diff", "--color=always", "--", file]() or
                git["diff", "--color=always", 'HEAD', "--", file]())


def update(diff, menu):
    menu.set_options(git_status())
    line = menu.selected_line()
    if line:
        file, status = line[3:], line[:2]
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


def handle(key, menu, win):
    global treeish
    file = (menu.selected_line() or '')[3:] or None
    if key == ord('a'):
        git['add', '--', file]()
    elif key == ord('A'):
        with suspend_curses():
            git['add', '-p', '--', file] & FG
    elif key == ord('c'):
        c = win.getch()
        backup_dir = os.path.expanduser('~/lost/git-checkout/%s' % os.path.basename(os.getcwd()))
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        with open(os.path.join(backup_dir, '%s-%s.diff' % (time.strftime('%Y-%m-%d_%H-%M-%S'), os.path.basename(file))), 'w') as f:
            f.write(git_diff(file))
        git["checkout", '--', file]()
    elif key == ord('r'):
        git["reset", 'HEAD', '--', file]()
    elif key == curses.KEY_F5:
        pass  # Handling the key will cause the data to update
    elif key in (curses.KEY_ENTER, ord('\n')):
        with suspend_curses():
            git['commit'] & FG
    elif key == ord('m'):
        with suspend_curses():
            git['commit', '--amend'] & FG
    elif key == ord('d'):
        with suspend_curses():
            git['diff', '--', file] & FG
    elif key in (ord('e'), ord('E')):
        edit(file)
    elif key == ord('p') or key == ord('P'):
        with suspend_curses():
            git['push']
    elif key == ord('R'):
        with suspend_curses():
            hub['pr']
    elif key == ord('^'):
        treeish = "%s^" % treeish if treeish else 'HEAD'
    elif key == ord('H'):
        treeish = 'HEAD'
    elif key == ord('w'):
        treeish = None
    elif key == ord('q'):
        sys.exit(0)
    else:
        return False
    return True


start_app.main(handle, update)
