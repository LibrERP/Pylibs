import codecs
import datetime
import time
import typing

import pyte

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
    
    def send(self, data: bytes):
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
    
    def data_ready(self):
        return self._ssh_session.recv_ready()
    # end data_ready

    def close(self):
        self._ssh_session.close()
    # end close

    @property
    def closed(self):
        return self._ssh_session.closed
    # end close
    
# end SSHShell


class ScreenManager:
    
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
    def encoding(self):
        return self._encoding
    # pass encoding
    
    @property
    def lines(self) -> typing.List[str]:
        """
        Returns a list containig one string sequence for each row of the screen.
        Each row contains the character displayed bu the screen WITHOUT formatting
        """
        return self._screen.display.copy()
    # end lines
    
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
    
    def print_lines(self, new_line: str = '\n'):
        """
        Returns a list containing one string sequence for each row of the screen.
        Each row contains the character displayed bu the screen WITHOUT formatting
        """
        print(new_line.join(self._screen.display))
    # end lines

    def render(self):
        """
        Renders the screen buffer by printing each character in the screen prependind
        by the ascii formatting escape sequence
        """
        for line in self.styled_ascii():
            print(''.join(line))
        # end for
    # end render
    
    def update(self):
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
    
    def reset(self):
        self._screen.reset()
    # end reset

    def styled_debug(self):
        """Returns the screen buffer as a tuple for each character with the setted style"""
        return self._styled(debug=True)
    # end styled_debug

    def styled_ascii(self) -> typing.List[list]:
        """
        Returns each character in the screen buffer prepended by the ascii escape sequence
        defining the formatting for the character
        """
        return self._styled(debug=False)
    # end styled_ascii

    def _styled(self, debug=False):

        lines = list()
        ascii_style_obj = ASCIIStyler()
        
        if debug:
            styler = ascii_style_obj.styled_debug
        else:
            styler = ascii_style_obj.styled
        # end if

        buffer_copy = self._screen.buffer.copy()

        for line in range(self._screen.lines):

            current_line = list()

            for col in range(self._screen.columns):
                current_char = buffer_copy[line][col]
                styled_char = styler(current_char)
                current_line.append(styled_char)
            # end for

            lines.append(current_line)

        # end for

        return lines
        
    # end _styled
    
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
    
    def seq(self, data):
        """
            Sanityze data and send to the remote system
            NOTE: calling this function reasults in the screen modified_lines
                  property to be cleared before updating the screen with new
                  data received by the server
        """

        # Sanitize data and send it to the remote system
        sanitized_data = self.sanitize_data(data)
        self._proxy.ssh_shell.send(sanitized_data)
        
        # Update the screen with the replay of the remote system
        self._proxy.screen.update()
    # end chars
    
    def line(self, data=''):
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
    def line_end(self, value):
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
    def ssh_shell(self, ssh_shell: SSHShell):
        self._ssh_shell = ssh_shell
    # end ssh_shell.setter
    
    @property
    def screen(self) -> ScreenManager:
        return self._screen
    # end screen
    
    @screen.setter
    def screen(self, screen_manager: ScreenManager):
        self._screen = screen_manager
    # end screen
    
    @property
    def input(self) -> InputManager:
        return self._input
    # end input
    
    @input.setter
    def input(self, input_manager: InputManager):
        self._input = input_manager
    # end input

# end TerminalComponentsProxy


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
    def closed(self) -> bool:
        return self._proxy.ssh_shell.closed
    # end close
    
    def close(self):
        self._proxy.ssh_shell.close()
        self._proxy.screen.reset()
    # end close
    
# end SSHTerminal
