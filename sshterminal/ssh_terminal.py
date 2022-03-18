import codecs
import datetime
import time
import typing
from collections import namedtuple

import pyte

from . import keys
from .ascii_styler import ASCIIStyler


class SSHShell:
    
    def __init__(
            self, ssh_connection, rows, cols, read_delay_sec: float = 0, recv_buffer_size: int = 65536, encoding='utf-8'
    ):
        self._recv_buffer_size: int = recv_buffer_size
        self._read_delay_sec: float = read_delay_sec
        
        self._ssh_session = ssh_connection.get_transport().open_session()
        self._ssh_session.get_pty(width=cols, height=rows)
        self._ssh_session.invoke_shell()
    # end SSHShell
    
    def send(self, data: bytes) -> None:
        self._ssh_session.send(data)
    # end send
    
    def recv(self) -> bytes:
        """
        Generator method for reading data from SSH session
        """
        
        while True:
            
            # Give the server a bit of time to send the reply
            time.sleep(self._read_delay_sec)
            
            # Check for incoming data
            if self._ssh_session.recv_ready():
                yield self._ssh_session.recv(self._recv_buffer_size)
            else:
                break
            # end if
            
        # end while
    # end recv
    
    def data_ready(self) -> bool:
        return self._ssh_session.recv_ready()
    # end data_ready

    def close(self) -> None:
        self._ssh_session.close()
    # end close

    @property
    def closed(self) -> bool:
        return self._ssh_session.closed
    # end close
# end SSHShell


class ScreenManager:

    ScreenSize = namedtuple('ScreenSize', ['lines', 'cols'])
    
    def __init__(self, proxy: 'TerminalComponentsProxy', rows, cols, encoding='utf-8'):
        
        now = datetime.datetime.now()
        
        self._proxy: 'TerminalComponentsProxy' = proxy
        self._encoding = encoding
        self._decoder_fn = codecs.getdecoder(self._encoding)
        
        self._stream: pyte.Stream = pyte.Stream()
        
        self._screen: pyte.Screen = pyte.Screen(cols, rows)
        self._stream.attach(self._screen)
    # end __init__
    
    @property
    def encoding(self) -> str:
        return self._encoding
    # pass encoding

    @property
    def cursor(self) -> pyte.screens.Cursor:
        return self._screen.cursor
    # end cursor
    
    @property
    def display_lines(self) -> typing.List[str]:
        """
        Returns a list containing one string sequence for each row of the screen.
        Each row contains the character displayed bu the screen WITHOUT formatting
        """
        return self._screen.display.copy()
    # end lines

    @property
    def buffer(self):
        return self._screen.buffer
    # end buffer
    
    @property
    def modified_lines(self) -> typing.Set[int]:
        """
        Return a set containig the indexes of lines modified by data received
        from the server since last input sent.
        NOTE: This property is automatically cleared when the
              update() method gets called
        """
        return self._screen.dirty
    # end new_lines
    
    def print_lines(self, new_line: str = '\n') -> None:
        """
        Returns a list containing one string sequence for each row of the screen.
        Each row contains the character displayed bu the screen WITHOUT formatting
        """
        print(new_line.join(self._screen.display))
    # end lines

    def render(self, debug=False) -> None:
        """
        Renders the screen buffer by printing each character in the screen prepending
        by the ascii formatting escape sequence
        """
        for line in self.styled_ascii(debug=debug):
            print(''.join(line))
        # end for
    # end render
    
    def update(self) -> None:
        """
        Receive data from remote host and update the screen.
        NOTE: calling this method will clear the list of new lines returned by
              the modified_lines property
        """
        self._screen.dirty.clear()
        
        for data_in in self._proxy.ssh_shell.recv():
            chars_in = data_in.decode(self._encoding, errors='replace')  # Decode from bytes to chars
            self._stream.feed(chars_in)  # Update the screen
        # end while
    # end update
    
    def reset(self) -> None:
        self._screen.reset()
    # end reset

    def styled_ascii(self, debug=False) -> typing.List[list]:
        """
        Returns each character in the screen buffer prepended by the ascii escape sequence
        defining the formatting for the character
        """

        lines = list()
        ascii_style_obj = ASCIIStyler()
        
        if debug:
            styler = ascii_style_obj.styled_debug
        else:
            styler = ascii_style_obj.styled
        # end if

        buffer_copy = self._screen.buffer.copy()
        cursor = self._screen.cursor

        for line in range(self._screen.lines):

            current_line = list()

            for col in range(self._screen.columns):
                current_char = buffer_copy[line][col]

                # If this is the cursor position apply a special style
                if line == cursor.y and col == cursor.x:

                    # Set the styler state as if the normal style were used and save it
                    styler(current_char)
                    styler_state = ascii_style_obj.state

                    # Style the cursor character
                    cursor_char = pyte.screens.Char(
                        data=current_char.data,
                        fg='cursor',
                        bg='cursor',
                        underscore=True,
                        bold=True,
                    )
                    styled_char = styler(cursor_char)

                    # Restore the previous state of the styler
                    # as if cursor_char were never processed
                    ascii_style_obj.state = styler_state

                else:
                    styled_char = styler(current_char)
                # end if

                current_line.append(styled_char)
            # end for

            lines.append(current_line)
        # end for

        return lines
    # end styled_ascii

    @property
    def actual_size(self) -> ScreenSize:
        return self.ScreenSize(lines=self._screen.lines, cols=self._screen.columns)
    # end actual_size
# end ScreenManager


class InputManager:
    """
    Manages the input data with 2 methods:
    - chars: converts the passed data in bytes and sends them without any addition
    - line: converts the passed data in bytes and sends them without appending the
            "line_end" sequence (which is also converted to bytes)
    
    The "line_end" sequence is specified using the "line_end" property and defaults to "\n"
    """
    
    def __init__(self, proxy: 'TerminalComponentsProxy', line_end='\n'):
        """
        The "line_end" parameter can be passed as str or as bytes, it will be stored as bytes
        """
        self._proxy = proxy
        self.line_end = line_end  # Set _line_end through the line_end property
    # end __init__
    
    def seq(self, data) -> None:
        """
            Sanityze data and send to the remote system
            NOTE: calling this function reasults in the screen modified_lines
                  property to be cleared before updating the screen with new
                  data received by the server
        """

        # Sanitize data and send it to the remote system
        sanitized_data = self.sanitize_data(data)
        #print(f'InputManager.seq - sending "{sanitized_data}"')
        self._proxy.ssh_shell.send(sanitized_data)
        
        # Update the screen with the replay of the remote system
        self._proxy.screen.update()
    # end chars
    
    def line(self, data='') -> None:
        """
            Sanityze data and send to the remote system followed
            by "line_end" sequence
            NOTE: calling this function reasults in the screen modified_lines
                  property to be cleared before updating the screen with new
                  data received by the server
        """
        self.seq(data)
        self.seq(self.line_end)
    # end chars
    
    @property
    def line_end(self) -> str:
        """Return the "line_end" sequence"""
        return self._line_end.decode()
    # end line_end
    
    @line_end.setter
    def line_end(self, value) -> None:
        """Set the "line_end" sequence"""
        self._line_end = self.sanitize_data(value)
    # end line_end

    @staticmethod
    def sanitize_data(data) -> bytes:
        """Ensures data to be send is in a compatible form"""
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode()
        else:
            raise TypeError('"data" must be str or bytes')
        # end if
    # end sanitize_data
# end InputManager


class TerminalComponentsProxy:
    
    def __init__(self):
        self._ssh_shell: SSHShell = None
        self._screen: ScreenManager = None
        self._input: InputManager = None
    # end __init__
    
    @property
    def ssh_shell(self) -> SSHShell:
        return self._ssh_shell
    # end ssh_shell
    
    @ssh_shell.setter
    def ssh_shell(self, ssh_shell: SSHShell) -> None:
        self._ssh_shell = ssh_shell
    # end ssh_shell.setter
    
    @property
    def screen(self) -> ScreenManager:
        return self._screen
    # end screen
    
    @screen.setter
    def screen(self, screen_manager: ScreenManager) -> None:
        self._screen = screen_manager
    # end screen
    
    @property
    def input(self) -> InputManager:
        return self._input
    # end input
    
    @input.setter
    def input(self, input_manager: InputManager) -> None:
        self._input = input_manager
    # end input
# end TerminalComponentsProxy


class Cursor:

    MOVES = {
        'u': keys.ARROW['up'],
        'd': keys.ARROW['down'],
        'l': keys.ARROW['left'],
        'r': keys.ARROW['right'],
        't': keys.TAB_FWD,
        'T': keys.TAB_BACK,
    }

    CursorPosition = namedtuple('CursorPosition', ['line', 'col'])

    def __init__(self, pyte_cursor: pyte.screens.Cursor, input_manager: InputManager):
        self._pyte_cursor: pyte.screens.Cursor = pyte_cursor
        self._input_manager = input_manager
    # end __init__

    @property
    def position(self) -> CursorPosition:
        """Returns current cursor position as (line, col). Index starts from 0."""
        return self.CursorPosition(
            line=self._pyte_cursor.y,
            col=self._pyte_cursor.x
        )
    # end position

    @property
    def x(self) -> int:
        return self._pyte_cursor.x
    # end x

    @property
    def col(self) -> int:
        return self._pyte_cursor.x
    # end col

    @property
    def y(self) -> int:
        return self._pyte_cursor.y
    # end y

    @property
    def line(self) -> int:
        return self._pyte_cursor.y
    # end line

    def move(self, where: str) -> None:

        # Verify commands are valid
        for single_move in where:
            assert single_move in self.MOVES
        # end for

        ascii_commands = ''.join(map(lambda x: self.MOVES[x], where))
        ascii_sequence = ''.join(ascii_commands)

        self._input_manager.seq(ascii_sequence)
    # end up

    def up(self) -> None:
        self.move('u')
    # end up

    def down(self) -> None:
        self.move('d')
    # end down

    def left(self) -> None:
        self.move('l')
    # end left

    def right(self) -> None:
        self.move('r')
    # end right

    def tab_fwd(self) -> None:
        self.move('t')
    # end tab_back

    def tab_back(self) -> None:
        self.move('T')
    # end tab_back

    def write(self, data: str) -> None:
        self._input_manager.seq(data)
    # end write

    def writeln(self, data: str = '') -> None:
        self._input_manager.line(data)
    # end writeln

    def delete(self, n: int = 1) -> None:
        self.write(keys.DELETE * n)
    # end delete

    def backsp(self, n: int = 1) -> None:
        self.write(keys.BACKSPACE * n)
    # end backsp
# end Cursor


class SSHTerminal:
    
    def __init__(
        self, ssh_connection, rows: int = 25, cols: int = 80, encoding: str = 'utf-8', read_delay_sec: float = 0.05
    ):
        
        # Initialize components
        self._proxy: TerminalComponentsProxy = TerminalComponentsProxy()

        shell = SSHShell(ssh_connection=ssh_connection, rows=rows, cols=cols, read_delay_sec=read_delay_sec)
        self._proxy.ssh_shell = shell

        input_mgr = InputManager(self._proxy)
        self._proxy.input = input_mgr

        screen_mgr = ScreenManager(self._proxy, rows=rows, cols=cols, encoding=encoding)
        self._proxy.screen = screen_mgr
        
        # Update the screen
        self._proxy.screen.update()
    # end __init__
    
    @property
    def screen(self) -> ScreenManager:
        return self._proxy.screen
    # end screen
    
    @property
    def input(self) -> InputManager:
        return self._proxy.input
    # end input

    @property
    def cursor(self) -> Cursor:
        return Cursor(
            input_manager=self._proxy.input,
            pyte_cursor=self._proxy.screen.cursor,
        )
    # end cursor
    
    @property
    def closed(self) -> bool:
        return self._proxy.ssh_shell.closed
    # end close
    
    def close(self) -> None:
        self._proxy.ssh_shell.close()
        self._proxy.screen.reset()
    # end close
# end SSHTerminal
