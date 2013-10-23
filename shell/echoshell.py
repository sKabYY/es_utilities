#!/usr/bin/env python

import curses
import curses.ascii as ca
from curses.ascii import ctrl, iscntrl, isprint


def write_tmp(s):
    with open('log.out', 'a') as f:
        print >>f, s


def ctrlc(c):
    return ord(ctrl(c))


def ctrl_unknown(sb):
    pass


def ctrl_goto_start_of_line(sb):
    pass


def ctrl_move_left(sb):
    sb.move_left()


def ctrl_delete_current(sb):
    pass


def ctrl_goto_end_of_line(sb):
    pass


def ctrl_move_right(sb):
    sb.move_right()


def ctrl_delete_backward(sb):
    pass


def ctrl_execute(sb):
    sb.execute()


def ctrl_newline_or_execute(sb):
    if sb.is_end_of_line():
        sb.execute()
    else:
        sb.addnewline()


def ctrl_clear_to_end(sb):
    pass


def ctrl_refresh_screen(sb):
    pass


def ctrl_move_down(sb):
    sb.move_down()


def ctrl_insert_newline(sb):
    pass


def ctrl_move_up(sb):
    sb.move_up()


def key_map(key_code):
    m = {
        curses.KEY_UP: ctrlc('p'),
        curses.KEY_DOWN: ctrlc('n'),
        curses.KEY_LEFT: ctrlc('b'),
        curses.KEY_RIGHT: ctrlc('f'),
    }
    try:
        return m[key_code]
    except KeyError:
        return key_code


def mknewline():
    return ctrlc('j')


def is_newline(key_code):
    return key_code == ctrlc('j')


def control_keys(key_code):
    return {
        ctrlc('a'): ctrl_goto_start_of_line,
        ctrlc('b'): ctrl_move_left,
        ctrlc('d'): ctrl_delete_current,
        ctrlc('e'): ctrl_goto_end_of_line,
        ctrlc('f'): ctrl_move_right,
        ctrlc('g'): ctrl_unknown,
        ctrlc('h'): ctrl_delete_backward,
        ctrlc('j'): ctrl_execute,
        ctrlc('k'): ctrl_clear_to_end,
        ctrlc('l'): ctrl_refresh_screen,
        ctrlc('n'): ctrl_move_down,
        ctrlc('o'): ctrl_insert_newline,
        ctrlc('p'): ctrl_move_up,
        ca.CR: ctrl_newline_or_execute,
    }[key_code]


def do_ctrl(sb, key_code):
    control_keys(key_code)(sb)


class FIFOBuf(object):
    def __init__(self, max_size):
        self.__l = []
        self.__max_size = max_size

    def add(self, elem):
        if len(self.__l) == self.__max_size:
            self.__l.pop(0)
        self.__l.append(elem)

    def addall(self, elems):
        for elem in elems:
            self.add(elem)

    def __getitem__(self, idx):
        return self.__l[idx]

    def __len__(self):
        return len(self.__l)

    def __str__(self):
        return str(self.__l)

    def __repr__(self):
        return repr(self.__l)


def char_buf_to_lines(buf, width):
    lines = []
    tmpbuf = []
    for key_code in buf:
        if is_newline(key_code) or len(tmpbuf) == width:
            lines.append(''.join(tmpbuf))
            tmpbuf = []
        if isprint(key_code):
            tmpbuf.append(chr(key_code))
    lines.append(''.join(tmpbuf))
    return lines


def string_to_lines(string, width):
    lines = []
    tmpbuf = []
    for c in string:
        if c == '\n' or len(tmpbuf) == width:
            lines.append(''.join(tmpbuf))
            tmpbuf = []
        if isprint(c):
            tmpbuf.append(c)
    lines.append(''.join(tmpbuf))
    return lines


MAX_BUFF = 500


class ScreenBuf(object):
    def __init__(self, window):
        self.window = window
        self.get_size()
        write_tmp('h=%s' % self.height)
        write_tmp('w=%s' % self.width)
        self.history_buf = FIFOBuf(MAX_BUFF)
        self.prompt = '> '
        self.reset_input_buf()
        self.refresh()

    def reset_input_buf(self):
        self.input_buf = []
        self.input_pos = 0

    def input_buf_to_string(self):
        def to_char(key_code):
            if is_newline(key_code):
                return '\n'
            else:
                return chr(key_code)

        return map(to_char, self.input_buf)

    def get_size(self):
        self.height, self.width = self.window.getmaxyx()

    def refresh(self):

        def find_pos(buf, pos, width):
            y = 0
            x = 0
            idx = 0
            while idx != pos:
                c = buf[idx]
                if is_newline(c):
                    y += 1
                    x = 0
                    idx += 1
                elif x == width:
                    y += 1
                    x = 0
                else:
                    x += 1
                    idx += 1
            return y, x

        def display_line(line):
            self.window.addnstr(line, self.width)

        def display_backward(lines, num, lineno):
            if num <= 0:
                return
            if num >= len(lines):
                start = 0
            else:
                start = len(lines) - num
            for i in xrange(start, len(lines)):
                self.window.move(lineno, 0)
                display_line(lines[i])
                lineno += 1
            return lineno

        self.window.clear()
        prompt_buf = map(ord, self.prompt)
        all_buf = prompt_buf + self.input_buf
        inp_lines = char_buf_to_lines(all_buf, self.width)
        y, x = find_pos(
            all_buf,
            self.input_pos + len(prompt_buf),
            self.width
        )
        write_tmp(str(self.history_buf))
        write_tmp(str(inp_lines))
        self.window.move(0, 0)
        if len(inp_lines) >= self.height:
            display_backward(inp_lines, self.height, 0)
        else:
            rest_num = self.height - len(inp_lines)
            next_lineno = display_backward(self.history_buf, rest_num, 0)
            display_backward(inp_lines, len(inp_lines), next_lineno)
            y += next_lineno
        self.window.move(y, x)

    def addch(self, ch):
        self.input_buf.insert(self.input_pos, ch)
        self.input_pos += 1

    def is_end_of_line(self):
        return self.input_pos == len(self.input_buf)

    def execute(self):
        def to_char(key_code):
            if is_newline(key_code):
                return '\n'
            else:
                return chr(key_code)

        #source = ''.join(map(to_char, self.input_buf))
        lines = char_buf_to_lines(
            map(ord, self.prompt) + self.input_buf,
            self.width
        )
        self.history_buf.addall(lines)
        self.reset_input_buf()

    def addnewline(self):
        self.addch(mknewline())

    def newline_with_prompt(self):
        pass

    def move_up(self):
        pass

    def move_down(self):
        pass

    def move_left(self):
        if self.input_pos > 0:
            self.input_pos -= 1

    def move_right(self):
        if self.input_pos < len(self.input_buf):
            self.input_pos += 1


def driver_loop(stdscr):
    sb = ScreenBuf(stdscr)
    while True:
        inp = stdscr.getch()
        inp = key_map(inp)
        #write_tmp(inp)
        if iscntrl(inp):
            do_ctrl(sb, inp)
        else:
            sb.addch(inp)
        sb.refresh()


class open_curses(object):
    def __enter__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.nonl()
        curses.cbreak()
        self.stdscr.keypad(1)
        return self.stdscr

    def __exit__(self, type, value, traceback):
        curses.echo()
        self.stdscr.keypad(0)
        curses.nocbreak()
        curses.endwin()


def my_wrapper(proc, *args, **kwargs):
    with open_curses() as stdscr:
        proc(stdscr, *args, **kwargs)


my_wrapper(driver_loop)
