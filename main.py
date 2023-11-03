#!/usr/bin/env python3
"""
get ideas from https://wasimlorgat.com/posts/editor.html ?

"""

import curses
import io
import os
from contextlib import contextmanager


def refresh_all_windows(windows):
    for window in windows:
        window.noutrefresh()
    curses.doupdate()


@contextmanager
def restore_position(stdscr:curses.window):
    y,x = stdscr.getyx()
    yield
    stdscr.move(y,x)
    stdscr.refresh()


class Editor:
    stdscr: curses.window
    def __init__(self):
        self.stdscr: curses.window

    def banner(self, text):
        with restore_position(self.stdscr):
            self.stdscr.addstr(0, 0, text, curses.A_REVERSE)

    def addtext(self, text:str):
        y0,x0 = self.stdscr.getyx()
        self.stdscr.addstr(text)
        y1,x1 = self.stdscr.getyx()

        ydiff = y1 - y0
        xdiff = x1 - x0


    def main(self, stdscr:curses.window):
        self.stdscr = stdscr
        messages = []

        self.stdscr.clear()

        # begin_x = 20; begin_y = 7
        # height = 5; width = 40
        # # win = curses.newwin(height, width, begin_y, begin_x)

        self.stdscr.move(1,0)
        self.banner("Current mode: Typing mode; alt-q to quit")
        # self.stdscr.refresh()

        # top left
        # (0,0)
        # bottom right
        # (curses.LINES - 1, curses.COLS - 1)

        # alt is detected as a separate key '\x1b' while ctrl changes the character code entirely

        last_key = key = None
        bio = io.BytesIO()
        # self.stdscr.addstr('\n')
        line_length = 0
        line_lengths = []
        while True:
            last_key = key
            try:
                key = self.stdscr.getkey()
            except (KeyboardInterrupt, curses.error):
                continue

            # backspace
            if key == '\x7f':
                y, x = self.stdscr.getyx()
                if x == 0:
                    if line_lengths:
                        self.stdscr.move(y-1, line_lengths.pop())
                else:
                    self.stdscr.addstr('\b \b')
                bio.seek(-1, os.SEEK_CUR)
                bio.write(b'\0')
                bio.seek(-1, os.SEEK_CUR)
            elif key == 'KEY_RESIZE':
                pass
            # alt-q to quit
            elif last_key == '\x1b' and key == 'q':
                # messages.append('detected alt-q')
                break
            elif key == '\n':
                line_lengths.append(line_length)
                line_length = 0
                self.stdscr.addstr('\n')
                pass
                # bio.seek(0)
                # self.stdscr.addstr(bio.read().split(b'\0', 1)[0].decode()+'\n')
                # bio.truncate(0)
                # bio.seek(0)
            elif '\\' in repr(key):
                # ignore any non-printing character
                pass
            elif len(key) > 1:
                pass
            elif key:
                self.stdscr.addstr(key)
                line_length += len(key)
                # we want to see \ sequences when they appear
                # if len(repr(key))>3:
                #     key = repr(key)

                bio.write(key.encode())

            # self.stdscr.clear()
            # self.stdscr.addstr(1,0,repr(last_key)+repr(key))

        return messages


if __name__ == '__main__':
    editor = Editor()
    messages = curses.wrapper(editor.main)
    print(messages)
