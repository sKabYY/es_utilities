import sys
import curses
import curses.ascii as ca
from curses.ascii import ctrl, iscntrl, isprint

from interp.tilib import dostring, tostring, isvoid
from tieslib.tieslib import setup_ties_environment


def write_tmp(s):  # TODO
    with open('log.out', 'a') as f:
        f.write(s)


# Key code and char #######################################


def ctrlc(c):
    return ord(ctrl(c))


def mknewline_code():
    return ctrlc('j')


def mknewline_char():
    return chr(mknewline_code())


def is_newline(c):
    r'''
    newline is "\n"
    '''
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


def code_list_to_string(buf):
    return ''.join(map(code_to_string, buf))


###########################################################


class FIFOBuf(object):
    '''
    An FIFO struct with a max size.
    '''
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


def string_to_lines(string, width):
    lines = []
    tmpbuf = []
    for c in string:
        if is_newline(c) or len(tmpbuf) == width:
            lines.append(''.join(tmpbuf))
            tmpbuf = []
        if isprint(c):
            tmpbuf.append(c)
    lines.append(''.join(tmpbuf))
    return lines


class TiTerminal(object):
    '''
    This is a state machine.
    '''
    def __init__(self, window):
        self.command_mode = CommandMode(window)
        self.view_mode = ViewMode(window)
        self.current_mode = None
        self.enter_mode(self.command_mode)

    def enter_mode(self, mode):
        if self.current_mode is not None:
            self.current_mode.exit()
        self.current_mode = mode
        if self.current_mode is not None:
            self.current_mode.enter()

    def close(self):
        self.enter_mode(None)

    def handle_input(self, key_code):
        self.current_mode.handle_input(key_code)

    def refresh(self):
        self.current_mode.refresh()


class CommandMode(object):
    MAX_BUFF = 500
    STATE_INPUT = '*INPUT MODE*'
    STATE_OUTPUT = '*OUTPUT MODE*'

    def __init__(self, window):
        self.enter_input_mode()
        self.window = window
        self.fetch_size()
        # history buffer
        self.history_buf = FIFOBuf(CommandMode.MAX_BUFF)
        # input buffer
        self.prompt = '> '
        self.reset_input_buf()
        # output buffer
        self.reset_output_buf()

    def is_input_mode(self):
        return self.state == CommandMode.STATE_INPUT

    def is_output_mode(self):
        return self.state == CommandMode.STATE_OUTPUT

    def enter_input_mode(self):
        self.state = CommandMode.STATE_INPUT

    def enter_output_mode(self):
        self.state = CommandMode.STATE_OUTPUT

    def state_name(self):
        return self.state

    def enter(self):
        # redirect stdout, maybe stderr?
        self.backup_stdout = sys.stdout
        sys.stdout = self
        # environment
        self.global_env = setup_ties_environment()

    def exit(self):
        sys.stdout = self.backup_stdout

    def fetch_size(self):
        '''
        Update the height and width of the window.
        '''
        self.height, self.width = self.window.getmaxyx()

    def reset_input_buf(self):
        '''
        Clean the input buffer.
        '''
        self.input_buf = []
        self.input_pos = 0

    def input_buf_to_string(self):
        '''
        Translate input buffer to a string.
        '''
        return code_list_to_string(self.input_buf)

    def reset_output_buf(self):
        '''
        Clean the output buffer.
        '''
        self.output_buf = ['']

    def output_buf_to_string(self):
        '''
        Translate input buffer to a string.
        '''
        return ''.join(self.output_buf)

    def reset_all_buf(self):
        '''
        Clean the input buffer and output buffer.
        '''
        self.reset_input_buf()
        self.reset_output_buf()

    def handle_input(self, key_code):
        '''
        Handle keyboard input.
        '''

        def key_map(key_code):
            m = {
                curses.KEY_UP: ctrlc('p'),
                curses.KEY_DOWN: ctrlc('n'),
                curses.KEY_LEFT: ctrlc('b'),
                curses.KEY_RIGHT: ctrlc('f'),
                curses.KEY_BACKSPACE: ctrlc('h'),
                curses.KEY_DC: ctrlc('d'),
            }
            try:
                return m[key_code]
            except KeyError:
                return key_code

        def control_keys(scr, key_code):
            r'''
                LF: \n, ^J.  Execute.
                CR: \r, ^M.  Execute if cursor is at the end of line.
                EOT: ^D.  Delete current char or exit
            '''
            return {
                ctrlc('a'): scr.ctrl_goto_start_of_line,
                ctrlc('b'): scr.ctrl_move_left,
                ctrlc('d'): scr.ctrl_delete_current,
                ctrlc('e'): scr.ctrl_goto_end_of_line,
                ctrlc('f'): scr.ctrl_move_right,
                ctrlc('g'): scr.ctrl_unknown,
                ctrlc('h'): scr.ctrl_delete_backward,
                ctrlc('j'): scr.ctrl_execute,
                ctrlc('m'): scr.ctrl_newline_or_execute,
                ctrlc('k'): scr.ctrl_clear_to_end,
                ctrlc('l'): scr.ctrl_refresh_screen,
                ctrlc('n'): scr.ctrl_move_down,
                ctrlc('o'): scr.ctrl_insert_newline,
                ctrlc('p'): scr.ctrl_move_up,
            }[key_code]

        def do_ctrl(scr, key_code):
            control_keys(scr, key_code)()

        key_code = key_map(key_code)
        if iscntrl(key_code):
            do_ctrl(self, key_code)
        else:
            self.addch(key_code)
        self.refresh()

    def write(self, string):
        self.output_buf.append(string)

    def flush_output_buf_except_last(self):
        output = self.output_buf_to_string()
        outlines = string_to_lines(output, self.width)
        self.output_buf = [outlines.pop()]
        self.history_buf.addall(outlines)

    def flush(self):
        self.flush_output_buf_except_last()
        self.refresh()

    def refresh(self):
        '''
        Refresh the histroy buffer and input buffer to screen
        '''

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
        if self.is_input_mode():
            input_string = self.input_buf_to_string()
            output_string = self.output_buf_to_string()
            prompt = output_string + self.prompt
            last_lines = string_to_lines(
                prompt + input_string,
                self.width
            )
            y, x = find_pos(
                map(ord, prompt) + self.input_buf,
                self.input_pos + len(prompt),
                self.width
            )
        elif self.is_output_mode():
            last_lines = string_to_lines(
                self.output_buf_to_string(),
                self.width
            )
            y = len(last_lines) - 1
            x = len(last_lines[-1])
        else:
            raise Exception('Unknown state %s' % self.state_name())

        self.window.move(0, 0)
        if len(last_lines) >= self.height:
            display_backward(last_lines, self.height, 0)
        else:
            rest_num = self.height - len(last_lines)
            next_lineno = display_backward(self.history_buf, rest_num, 0)
            display_backward(last_lines, len(last_lines), next_lineno)
            y += next_lineno
        self.window.move(y, x)

    def addch(self, ch):
        '''
        Insert a char.
        '''
        self.input_buf.insert(self.input_pos, ch)
        self.input_pos += 1

    def is_end_of_line(self):
        '''
        Is the input_pos at the end of the input line.
        '''
        return self.input_pos == len(self.input_buf)

    def execute(self):
        '''
        Execute.
        '''
        source = self.input_buf_to_string()
        lines = string_to_lines(
            self.output_buf_to_string() + self.prompt + source,
            self.width
        )
        self.history_buf.addall(lines)
        self.reset_all_buf()

        self.enter_output_mode()
        result = dostring(source, self.global_env)
        if not isvoid(result):
            self.write(tostring(result))
            self.write(mknewline_char())
        self.flush()
        self.enter_input_mode()

    def newline(self):
        r'''
        Insert a newline "\n"
        '''
        self.addch(mknewline_code())

    def ctrl_unknown(self):
        pass

    def ctrl_goto_start_of_line(self):
        self.input_pos = 0

    def ctrl_move_left(self):
        '''
        Cursor left, wrapping to previous line if appropriate
        '''
        if self.input_pos > 0:
            self.input_pos -= 1

    def ctrl_move_right(self):
        '''
        Cursor right, wrapping to previous line if appropriate
        '''
        if self.input_pos < len(self.input_buf):
            self.input_pos += 1

    def ctrl_move_up(self):
        pass

    def ctrl_move_down(self):
        pass

    def ctrl_delete_current(self):
        if self.input_pos < len(self.input_buf):
            self.input_buf.pop(self.input_pos)

    def ctrl_goto_end_of_line(self):
        self.input_pos = len(self.input_buf)

    def ctrl_delete_backward(self):
        if self.input_pos > 0:
            self.input_pos -= 1
            self.input_buf.pop(self.input_pos)

    def ctrl_execute(self):
        self.execute()

    def ctrl_newline_or_execute(self):
        if self.is_end_of_line():
            self.execute()
        else:
            self.newline()

    def ctrl_clear_to_end(self):
        length = len(self.input_buf) - self.input_pos
        for _ in xrange(length):
            self.input_buf.pop()

    def ctrl_refresh_screen(self):
        '''
        Do nothing
        '''
        pass

    def ctrl_insert_newline(self):
        self.newline()


class ViewMode(object):
    def __init__(self, window):
        self.window = window


def curses_wrapper(proc, *args, **kwargs):

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

    with open_curses() as stdscr:
        proc(stdscr, *args, **kwargs)


def driver_loop():

    def main_loop(stdscr):
        terminal = TiTerminal(stdscr)
        while True:
            terminal.refresh()
            inp = stdscr.getch()
            terminal.handle_input(inp)

    curses_wrapper(main_loop)
