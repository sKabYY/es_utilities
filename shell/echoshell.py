#!/usr/bin/env python

import curses
import curses.ascii as ca
from curses.ascii import ctrl, iscntrl, isprint


def write_tmp(s):
    with open('log.out', 'a') as f:
        print >>f, s


def mknewline_code():
    return ctrlc('j')


def mknewline_char():
    return chr(mknewline_code())


def is_newline(c):
    if isinstance(c, int):
        return c == mknewline_code()
    elif isinstance(c, str):
        return c == mknewline_char()
    return False


def is_tab(c):
    if isinstance(c, int):
        return c == ord('\t')
    elif isinstance(c, str):
        return c == '\t'
    else:
        return False


def expand_tab():
    tabstop = 2
    return ' ' * tabstop


def code_to_string(code):
    if ca.isprint(code):
        return chr(code)
    elif is_newline(code):
        return mknewline_char()
    elif is_tab(code):
        return expand_tab()
    else:
        raise ValueError('Unknown code %s' % code)


def printable_code(code):
    return isprint(code) or is_tab(code)


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
        sb.newline()


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


def control_keys(key_code):
    r'''
        LF: \n, ^J.  Execute.
        CR: \r, ^M.  Execute if cursor is at the end of line.
        EOT: ^D.  Delete current char or exit
    '''
    return {
        ctrlc('a'): ctrl_goto_start_of_line,
        ctrlc('b'): ctrl_move_left,
        ctrlc('d'): ctrl_delete_current,
        ctrlc('e'): ctrl_goto_end_of_line,
        ctrlc('f'): ctrl_move_right,
        ctrlc('g'): ctrl_unknown,
        ctrlc('h'): ctrl_delete_backward,
        ctrlc('j'): ctrl_execute,
        ctrlc('m'): ctrl_newline_or_execute,
        ctrlc('k'): ctrl_clear_to_end,
        ctrlc('l'): ctrl_refresh_screen,
        ctrlc('n'): ctrl_move_down,
        ctrlc('o'): ctrl_insert_newline,
        ctrlc('p'): ctrl_move_up,
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


def code_list_to_string(buf):
    return ''.join(map(code_to_string, buf))


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
        return code_list_to_string(self.input_buf)

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
                elif x >= width:
                    y += x / width
                    x %= width
                else:
                    x += len(code_to_string(c))
                    idx += 1
            if x > width:
                y += x / width
                x %= width
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
        # The result of string_to_lines and find_pos must be concordance.
        inp_lines = string_to_lines(
            self.prompt + self.input_buf_to_string(),
            self.width
        )
        y, x = find_pos(
            map(ord, self.prompt) + self.input_buf,
            self.input_pos + len(self.prompt),
            self.width
        )
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
        #source = self.input_buf_to_string()
        lines = string_to_lines(
            self.prompt + self.input_buf_to_string(),
            self.width
        )
        self.history_buf.addall(lines)
        self.reset_input_buf()

    def newline(self):
        self.addch(mknewline_code())

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
        write_tmp(inp)
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
