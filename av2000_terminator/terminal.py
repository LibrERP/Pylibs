import copy
from copy import deepcopy
import datetime
import re
import time
import typing

from paramiko import SSHClient

from sshterminal import SSHTerminal, keys
from sshterminal.ssh_terminal import ScreenManager

from . misc import ConnectionParams
from . misc.exceptions import DriverClosed, LoadingTimeout


def ensure_open(method):
    """
    Ensures the connection to av2000 is open
    before calling the decodated method.
    """
    
    def decorated_method(*args, **kwargs):
        target_obj = args[0]  # args[0] is always "self" for methods
        if target_obj.closed:
            raise DriverClosed
        else:
            return method(*args, **kwargs)
        # end if
    # end decorated_method
    
    return decorated_method
# end ensure_open


class AV2000Terminal:
    
    SCREEN_COLS = 100
    SCREEN_ROWS = 40
    
    PAGE_LOAD_TIMEOUT_SEC = 4
    
    MAX_EXIT_ITERATIONS = 20
    
    RETURN_CHAR = '\r'
    
    def __init__(self, connection_params: ConnectionParams):

        self._connection_params = connection_params
        cp = self._connection_params
        
        # SSH client initialization
        print('Initializing SSH clienti')
        self._client = SSHClient()
        self._client.load_system_host_keys()
        
        # SSH connection
        print(f'Connectiong to host {cp.host}')
        self._client.connect(
            hostname=cp.host,
            port=cp.port,
            username=cp.username,
            password=cp.password,
        )
        
        # Terminal emulator initialization
        print('Initializing terminal emulator')
        self._terminal = SSHTerminal(
            ssh_connection=self._client,
            rows=self.SCREEN_ROWS,
            cols=self.SCREEN_COLS,
            encoding=cp.encoding,
            read_delay_sec=cp.read_delay_sec,
        )
        
        # Start AV2000 program
        print('Starting AV2000 interface')
        # NOTE: "TERM" environment variable must be set to putty for F-keys
        #       to work correctly
        self._terminal.input.line('TERM=putty ./av2000')
        time.sleep(2)
        
        # Set company
        self.send_line(str(cp.company_id))
        
        print('Connection ready')
    # end __init__
    
    @property
    def connection_params(self):
        return deepcopy(self._connection_params)
    # end connection_params
    
    @property
    def closed(self):
        return self._terminal.closed
    # end close
    
    @property
    def display_lines(self):
        return deepcopy(self._terminal.screen.display_lines)
    # end display_lines
    
    @property
    def text_lines(self):
        return [ln for ln in self.display_lines if ln.strip()]
    # end text_lines

    @property
    def terminal_buffer(self):
        return copy.deepcopy(self._terminal.screen.buffer)
    # end text_lines
    
    def print_lines(self):
        print('\n'.join(self.display_lines))
    # end print_lines
    
    @property
    def modified_lines(self) -> typing.Set[int]:
        """
        Return a set containig the indexes of lines modified by data received
        from the server since last input sent.
        NOTE: This property is automatically cleared when the
              update() method gets called
        """
        return self._terminal.screen.modified_lines
    # end new_lines
    
    @ensure_open
    def update(self):
        """
        Receive data from remote host and update the screen.
        NOTE: calling this method will clear the list of new lines returned by
              the modified_lines property
        """
        self._terminal.screen.update()
    # end update
    
    @ensure_open
    def get_back_key(self):
        
        back_key = None
        
        text = self.text_lines
        last_line = text and text[-1] or ''
        
        end = re.match(r'.*\s[Ff]ine\s', last_line)
        esc = re.match(r'.*\s[Ee]sc\s', last_line)
        f10 = re.match(r'.*\sF10\s+Uscita', last_line)
        
        if f10:
            back_key = keys.F[10]
        elif esc:
            back_key = keys.ESC
        elif end:
            back_key = keys.END
        else:
            pass
        # end if
        
        return back_key
    # end get_back_key
    
    @ensure_open
    def exit(self):
        
        for counter in range(self.MAX_EXIT_ITERATIONS):
            
            text = self.text_lines
            last_line = text and text[-1] or ''
            back_key = self.get_back_key()
            
            if back_key:
                self.send_seq(back_key)
            # end if
            
            if back_key == keys.F[10]:
                # If F10 was sent the exit the loop
                # and close the connection
                break
            # end if
            
            time.sleep(1)
            self.update()
        # end for
        
        # Close the connection
        self.close()
    # end exit
    
    @ensure_open
    def close(self):
        self._terminal.close()
        print('AV2000 Connection closed', flush=True)
    # end close
    
    @ensure_open
    def send_line(self, data: str = ''):
        self._terminal.input.seq(data + self.RETURN_CHAR)
    # end
    
    @ensure_open
    def send_seq(self, data: str):
        self._terminal.input.seq(data)
    # end
    
    @ensure_open
    def wait_ready(
        self, is_ready: typing.Callable[[], bool], timeout_sec: float
    ):
        """
            Wait for something to be ready.
            The AV2000Terminal.update() will be executed at the end of
            each iteration so next call of readiness_fn() will find an
            up to date screen.
        """
        ts_start = datetime.datetime.now().timestamp()

        while not is_ready():
            # Check for timeout
            ts_now = datetime.datetime.now().timestamp()
            if (ts_now - ts_start) > timeout_sec:
                raise LoadingTimeout(
                    'Timeout waiting for page to load',
                    av2000_driver=self,
                )
            # end if

            # Update the screen
            # NB: the update() method already includes a bit of delay
            #     before checking for new data.
            self.update()
        # end
    # end wait_ready

    @ensure_open
    def print_screen(self):
        self._terminal.screen.render()
    # end print_screen

    @property
    @ensure_open
    def cursor(self):
        return self._terminal.cursor
    # end if

    @property
    def actual_size(self) -> ScreenManager.ScreenSize:
        return self._terminal.screen.actual_size
    # end actual_size
    
# end AV2000Terminal
