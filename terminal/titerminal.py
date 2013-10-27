import sys
import curses
import curses.ascii as ca
from curses.ascii import ctrl, iscntrl, isprint

from interp.tilib import tostring, isvoid, InterpError


def write_tmp(s):  # TODO
    with open('log.out', 'a') as f:
        f.write(s)


# Key code and char #######################################


def ctrlc(c):
    return ord(ctrl(c))


def is_resize_event(key_code):
    return key_code == curses.KEY_RESIZE


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


def is_print_or_newline(code):
    return ca.isprint(code) or is_newline(code)


def code_to_string(code):
    if ca.isprint(code):
        return chr(code)
    elif is_newline(code):
        return mknewline_char()
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

    def flush_tmpbuf():
        lines.append(''.join(tmpbuf))
        del tmpbuf[:]  # ugly! clear list tmpbuf

    for c in string:
        if is_newline(c):
            flush_tmpbuf()
        elif isprint(c):
            tmpbuf.append(c)
            if len(tmpbuf) == width:
                flush_tmpbuf()
    flush_tmpbuf()
    return lines


class TiTerminal(object):
    '''
    This is a state machine.
    '''
    def __init__(self, window, prompt, interpreter):
        self.window = window
        self.command_mode = CommandMode(self, prompt, interpreter)
        self.view_mode = ViewMode(self, self.command_mode.history_buf)
        self.current_mode = None
        self.enter_command_mode()
        self.isclosed = lambda: False

    def close(self):
        self.isclosed = lambda: True
        self.enter_mode(None)

    def enter_mode(self, mode):
        if mode != self.current_mode:
            if self.current_mode is not None:
                self.current_mode.exit()
            self.current_mode = mode
            if self.current_mode is not None:
                self.current_mode.enter()

    def enter_command_mode(self):
        self.enter_mode(self.command_mode)

    def enter_view_mode(self):
        self.enter_mode(self.view_mode)

    def resize(self):
        self.current_mode.resize()

    def handle_input(self, key_code):
        if is_resize_event(key_code):
            self.resize()
        else:
            self.current_mode.handle_input(key_code)

    def refresh(self):
        self.current_mode.refresh()


class BaseMode(object):
    def __init__(self, terminal):
        self.terminal = terminal
        self.window = terminal.window
        self.fetch_size()

    def fetch_size(self):
        '''
        Update the height and width of the window.
        '''
        self.height, self.width = self.window.getmaxyx()

    def resize(self):
        self.fetch_size()
        self.window.resize(self.height, self.width)
        self.refresh()


class CommandMode(BaseMode):
    MAX_BUFF = 500
    STATE_INPUT = '*INPUT MODE*'
    STATE_OUTPUT = '*OUTPUT MODE*'

    def __init__(self, terminal, prompt, interpreter):
        super(CommandMode, self).__init__(terminal)
        self.enter_input_mode()
        # interpreter
        self.interpreter = interpreter
        # history buffer
        self.history_buf = FIFOBuf(CommandMode.MAX_BUFF)
        # input buffer
        self.prompt = prompt
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

    def enter(self):
        # redirect stdout, where is stderr?
        self.backup_stdout = sys.stdout
        sys.stdout = self
        # reset interpreter
        self.interpreter.reset()

    def exit(self):
        sys.stdout = self.backup_stdout

    def state_name(self):
        return self.state

    def reset_input_buf(self):
        '''
        Clean the input buffer.
        '''
        self.input_buf = []
        self.input_pos = 0

    def input_buf_is_empty(self):
        return len(self.input_buf) == 0

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

    def output_buf_is_empty(self):
        return len(self.output_buf) == 1 and self.output_buf[0] == ''

    def output_buf_to_string(self):
        '''
        Translate output buffer to a string.
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
                curses.KEY_HOME: ctrlc('a'),
                curses.KEY_END: ctrlc('e'),
            }
            try:
                return m[key_code]
            except KeyError:
                return key_code

        def get_ctrl_handler(scr, key_code):
            r'''
                LF: \n, ^J.  Execute.
                CR: \r, ^M.  Execute if cursor is at the end of line.
                EOT: ^D.  Delete current char or exit
            '''
            m = {
                ctrlc('a'): scr.ctrl_goto_start_of_line,
                ctrlc('b'): scr.ctrl_move_left,
                ctrlc('c'): scr.ctrl_keyboard_interrupt,
                ctrlc('d'): scr.ctrl_delete_current_or_exit,
                ctrlc('e'): scr.ctrl_goto_end_of_line,
                ctrlc('f'): scr.ctrl_move_right,
                ctrlc('g'): scr.ctrl_beep,
                ctrlc('h'): scr.ctrl_delete_backward,
                ctrlc('j'): scr.ctrl_execute,
                ctrlc('m'): scr.ctrl_newline_or_execute,
                ctrlc('k'): scr.ctrl_clear_to_end,
                ctrlc('l'): scr.ctrl_refresh_screen,
                ctrlc('n'): scr.ctrl_move_down,
                ctrlc('o'): scr.ctrl_insert_newline,
                ctrlc('p'): scr.ctrl_move_up,
                ca.ESC: scr.ctrl_change_to_view_mode,
            }
            try:
                return m[key_code]
            except KeyError:
                return scr.ctrl_unknown

        def do_ctrl(scr, key_code):
            get_ctrl_handler(scr, key_code)()

        key_code = key_map(key_code)
        if iscntrl(key_code):
            do_ctrl(self, key_code)
        elif is_print_or_newline(key_code):
            self.addch(key_code)
        else:
            # do nothing
            pass

    def write(self, string):
        self.output_buf.append(string)

    def flush_output_buf_except_last(self):
        if not self.output_buf_is_empty():
            output = self.output_buf_to_string()
            outlines = string_to_lines(output, self.width)
            self.output_buf = [outlines.pop()]
            self.history_buf.addall(outlines)

    def flush_output_buf_all(self):
        self.flush_output_buf_except_last()
        if not self.output_buf_is_empty():
            self.history_buf.add(self.output_buf[0])
            self.reset_output_buf()

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
                if x >= width:
                    y += x / width
                    x %= width
                elif is_newline(c):
                    y += 1
                    x = 0
                    idx += 1
                else:
                    x += len(code_to_string(c))
                    idx += 1
            if x >= width:
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
        # y and x is the position relative to last_lines.
        prompt = self.prompt()
        if self.is_input_mode():
            last_lines = string_to_lines(
                prompt + self.input_buf_to_string(),
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
            if x == self.width:
                y += 1
                x = 0
        else:
            raise Exception('Unknown state %s' % self.state_name())

        self.window.move(0, 0)
        if len(last_lines) >= self.height:
            display_backward(last_lines, self.height, 0)
            y -= len(last_lines) - self.height
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
            self.prompt() + source,
            self.width
        )
        self.history_buf.addall(lines)
        self.reset_all_buf()

        self.enter_output_mode()
        try:
            output = self.interpreter.eval(source)
            if not isvoid(output):
                self.write(tostring(output))
                self.write(mknewline_char())
        except InterpError as e:
            self.write('[Error] %s' % str(e))
        except Exception as e:
            import traceback
            traceback.print_exc(None, self)
        self.flush_output_buf_all()
        self.refresh()
        self.enter_input_mode()

    def newline(self):
        r'''
        Insert a newline "\n"
        '''
        self.addch(mknewline_code())

    def ctrl_unknown(self):
        pass

    def ctrl_beep(self):
        curses.beep()

    def ctrl_keyboard_interrupt(self):
        lines = string_to_lines(
            self.prompt() + self.input_buf_to_string(),
            self.width
        )
        self.history_buf.addall(lines)
        self.reset_input_buf()

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

    def ctrl_delete_current_or_exit(self):
        if self.input_pos < len(self.input_buf):
            self.input_buf.pop(self.input_pos)
        elif self.input_buf_is_empty():
            self.terminal.close()

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

    def ctrl_change_to_view_mode(self):
        self.terminal.enter_view_mode()


class ViewMode(BaseMode):
    def __init__(self, terminal, text_buf):
        super(ViewMode, self).__init__(terminal)
        self.text_buf = text_buf
        self.offset = 0

    def enter(self):
        self.offset = 0

    def exit(self):
        pass

    def resize(self):
        super(ViewMode, self).resize()

    def num_text_lines(self):
        return self.height - 1

    def adjust_offset(self):
        max_offset = len(self.text_buf) - self.num_text_lines()
        if max_offset < 0:
            max_offset = 0
        if self.offset < 0:
            self.offset = 0
        elif self.offset > max_offset:
            self.offset = max_offset

    def set_offset(self, offset):
        self.offset = offset
        self.adjust_offset()

    def handle_input(self, key_code):

        def key_map(key_code):
            m = {
            }
            try:
                return m[key_code]
            except KeyError:
                return key_code

        def get_ctrl_handlers(scr, key_code):
            m = {
                ord('q'): scr.ctrl_change_to_command_mode,
                ord('j'): scr.ctrl_move_down,
                ord('k'): scr.ctrl_move_up,
            }
            try:
                return m[key_code]
            except KeyError:
                return scr.ctrl_unknown

        get_ctrl_handlers(self, key_code)()

    def ctrl_change_to_command_mode(self):
        self.terminal.enter_command_mode()

    def ctrl_unknown(self):
        '''
        Do nothing.
        '''
        pass

    def ctrl_move_down(self):
        self.set_offset(self.offset - 1)

    def ctrl_move_up(self):
        self.set_offset(self.offset + 1)

    def refresh(self):
        self.window.clear()
        num_lines = self.num_text_lines()
        start_lineno = len(self.text_buf) - num_lines
        start_lineno -= self.offset
        if start_lineno < 0:
            start_lineno = 0
        for i in xrange(start_lineno, start_lineno + num_lines):
            line = self.text_buf[i]
            self.window.move(i - start_lineno, 0)
            self.window.addnstr(line, self.width)
        self.window.move(num_lines, 0)
        self.window.addnstr('*** VIEW MODE ***', self.width)


def curses_wrapper(proc, *args, **kwargs):

    class open_curses(object):
        def __enter__(self):
            self.stdscr = curses.initscr()
            curses.start_color()
            curses.use_default_colors()
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


def driver_loop(get_prompt, interpreter):

    def main_loop(stdscr):
        terminal = TiTerminal(stdscr, get_prompt, interpreter)
        while not terminal.isclosed():
            terminal.refresh()
            try:
                inp = stdscr.getch()
                terminal.handle_input(inp)
            except KeyboardInterrupt:
                # This may be a bug of module curses.
                # Python version: 2.7.4
                # getch() cannot catch Ctrl-C.
                # Moreover, after catching the KeyboardInterrupt exception,
                # the calling of getch() failed and a unknown character
                # whose code is -1 remains in the keyboard input buffer.
                # So I have to call getch() again to clear the -1 character
                # and call ungetch(ctrlc('c')) to help curses catch Ctrl-C.
                stdscr.getch()  # This will return -1.
                curses.ungetch(ctrlc('c'))

    curses_wrapper(main_loop)
