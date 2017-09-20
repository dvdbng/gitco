#!/usr/bin/python
import curses
import os
import re
import pexpect
import sys
import textwrap
import pickle
from threading import Thread

import start_app
from actions import edit, suspend_curses, list_dir, cat_file, open_shell_with
from color import get_color, get_rgb
from ansi import ansi_to_attr_list

ORIG_CWD = os.getcwd()
TMP_FILE = '/tmp/gitco-gh-issues'
os.chdir('/home/david/dev/inboundsms')

from plumbum.cmd import hub, highlight, firefox, git
from plumbum import local, FG
from contextlib import contextmanager

@contextmanager
def in_orig_dir():
    os.chdir(ORIG_CWD)
    yield
    os.chdir('/home/david/dev/inboundsms')

def checkout_branch_starting_with(prefix):
    with in_orig_dir():
        branch = git('branch', '--list', '%s*' % prefix).split('\n')[0][2:].strip()
        if branch:
            git('checkout', branch)


def run_in_tty(cmd, *args):
    child = pexpect.spawn(cmd, list(args))
    try:
        child.expect(None)
    except pexpect.exceptions.EOF:
        return child.before.decode('utf-8')


class Issues():
    def __init__(self):
        self.issues = []
        self.load_issues_cache()
        t = Thread(target=self.load_issues)
        t.start()

    def load_issues_cache(self):
        if os.path.exists(TMP_FILE):
            with open(TMP_FILE, 'r') as f:
                self.issues = pickle.load(f)


    def load_issues(self):
        fields = {
            'number': 'i',
            'id': 'I',
            'url': 'U',
            'title': 't',
            'body': 'b',
            'labels': 'l',
            'author': 'au',
            'assignes': 'as',
            'milestone': 'Mt',
            'comment_count': 'NC',
            'created_at': 'ct',
            'updated_at': 'ut',
        }


        field_pairs = fields.items()
        field_separator = '---djoji2e101u182sd----'
        issue_separator = '---1oij231j231kasds----'
        format = field_separator.join('%' + pair[1] for pair in field_pairs) + issue_separator

        resp = (run_in_tty('hub', 'issue', '-a', 'none', '-a', 'none', '-f', format) +
                run_in_tty('hub', 'issue', '-a', 'dvdbng', '-f', format))

        if issue_separator not in resp:
            print(resp)
            sys.exit(1)

        res = [
            dict(zip((pair[0] for pair in field_pairs), issue_raw.split(field_separator)))
            for issue_raw in resp.split(issue_separator)
            if field_separator in issue_raw
        ]
        res.sort(key=lambda i: (len(i.get('milestone', '')), i.get('milestone')))
        res.reverse()
        self.issues = res
        with open(TMP_FILE, 'w') as f:
            f.write(pickle.dumps(res))

    def find_by_id(self, id):
        for issue in self.issues:
            if issue['id'] == id:
                return issue

    def issue_title(self, issue):
        status = re.search(' ([0-5]) -', issue['labels'])
        status = status.group(1) if status else ' '
        status_color = get_color(curses.COLOR_WHITE, get_rgb(0, 0, 255)) if status != ' ' else 0

        prioritym = re.search('(\d+;\d+;\d+)m (low|medium|high|critical) ', issue['labels'], re.I)
        priority = prioritym.group(2).lower() if prioritym else ' '
        priority_color = get_color(curses.COLOR_WHITE, get_rgb(*map(int, prioritym.group(1).split(';')))) if prioritym else 0

        assigned = 'A' if 'dvdbng' in issue['assignes'].lower() else ' '
        assigned_color = get_color(curses.COLOR_WHITE, curses.COLOR_GREEN) if assigned == 'A' else 0

        return [
            (issue['number'].rjust(8), get_color(curses.COLOR_GREEN)),
            (u' ', 0),
            (status, status_color),
            (priority[0].upper(), priority_color),
            (assigned, assigned_color),
            (u' ' + issue['title'], 0),
        ]


    def show_issue(self, issue):
        if issue is None:
            return "No issue"
        text = issue['body'].replace('\r', '')
        text = "\n".join(textwrap.wrap(text, width=120, replace_whitespace=False))

        formatted = (highlight['-O', 'ansi', '--syntax', 'markdown'] << text)()
        issue['formatted_body'] = formatted
        return textwrap.dedent(u"""
        Title: %(title)s
        Author: %(author)s
        Labels: %(labels)s
        Url: %(url)s
        Assigned: %(assignes)s
        Milestone: %(milestone)s
        Comments: %(comment_count)s

        %(formatted_body)s""") % issue

    def update(self, diff, menu):
        options = []

        i = 0
        last_milestone = None
        for issue in self.issues:
            if last_milestone == None or last_milestone != issue['milestone']:
                options.append([('In milestone %s' % issue['milestone'], get_color(curses.COLOR_BLUE) | curses.A_BOLD)])
                last_milestone = issue['milestone']
            options.append(self.issue_title(issue))

        if len(options) == 0:
            options.append([('no issues', 0)])
        menu.set_options(options)

        issue = self.selected_issue(menu.selected_line())
        if issue:
            diff.set_text(self.show_issue(issue))
        else:
            diff.set_text(menu.selected_line())

    def selected_issue(self, selected_line):
        if selected_line.strip().startswith('#'):
            return self.find_by_id(selected_line.strip().split(' ')[0][1:])
        else:
            return None

    def handle(self, key, menu, win):
        if key == ord('q'):
            sys.exit(0)
            return True
        elif key == curses.KEY_F5:
            start_app.App.app.set_status('Refreshing...')
            self.load_issues()
            return True

        issue = self.selected_issue(menu.selected_line())
        if issue is None:
            return

        if key == ord('g'):
            firefox(issue['url'])
        elif key == ord('b'):
            name = '%s_%s' % (issue['id'], re.sub('[^a-z0-9_]', '', re.sub('\s+', '_', issue['title'].lower())))
            with in_orig_dir():
                open_shell_with('git mkbranch %s ; and exit' % name)
        elif key == ord('c'):
            checkout_branch_starting_with(issue['id'])
        else:
            return False
        return True


app = Issues()
start_app.main(app.handle, app.update)
