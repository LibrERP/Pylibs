import abc
from collections.abc import Sized
import logging
from multiprocessing import Process, Queue, SimpleQueue
import sys

from av2000_terminator.driver import AV2000Driver
from av2000_terminator.navigation import Navigator
from av2000_terminator.misc.connection_params import ConnectionParams
from av2000_terminator.misc.exceptions import LoadingTimeout


_logger = logging.getLogger(__name__)


class AbstractTask(abc.ABC, Process):
    
    # NOTE: TASK_NAME must be overridden by derived classes
    TASK_NAME = None

    def __init__(
        self,
        name: str,
        connection_params: ConnectionParams,
        tasks: Sized,
        q: Queue,
        max_retry: int = 4
    ):
        super().__init__(name=name)

        self._connection_params = connection_params
        self._queue = q
        self._tasks = tasks
        # Number fo items downloaded: It's equal to list index of the last downloaded item plus 1.
        self._fetched_items = 0
        self._iterations_counter = 0
        self._max_retry = max_retry
        self._av2000 = None
        self._navigator = None
        self._exception_queue = SimpleQueue()
        
    # end __init__

    def run(self):

        while self._max_retry_ok() and not self._error() and not self._task_completed():

            # Open connection to av2000
            self._av2000 = AV2000Driver(self._connection_params)
            self._navigator = Navigator(self._av2000)
            
            # Notify task starting
            print(f'{self.name} Running task {self.TASK_NAME}', flush=True)
            
            try:
                self._task_loop()

            except LoadingTimeout as lte:
                # Increase the iterations counter
                print(f'{self.name} ERROR: LoadingTimeout', flush=True)
                self._iterations_counter = self._iterations_counter + 1

                _logger.error(' - ' * 10 + 'TERMINAL DUMP - BEGIN' + ' - ' * 10)
                for dline in lte.av2000_driver.display_lines:
                    _logger.error(dline)
                # end for
                _logger.error(' - ' * 10 + 'TERMINAL DUMP - END  ' + ' - ' * 10)

            except Exception as e:
                # Unexpected error
                print(f'{self.name} ERROR', flush=True)
                print(e, flush=True)
                self._exception_queue.put(e)

            finally:
                # Always close the connection when exiting the loop
                print(f'{self.name} finally', flush=True)
                self._navigator.exit()

            # end try / except

        # end while

        # Loop completed, let's check what happened
        if self._task_completed():
            sys.exit(0)
        elif self._error():
            sys.exit(1)
        else:
            sys.exit(2)
        # end if

    # end run

    def _max_retry_ok(self):
        return self._iterations_counter < self._max_retry
    # end _iterations_ok

    def _task_completed(self):
        return len(self._tasks) == self._fetched_items
    # end task completed

    def _error(self):
        return not self._exception_queue.empty()
    # end _error

    @abc.abstractmethod
    def _task_loop(self):
        pass
    # end _task_loop

# end SuppliersDownloadTask
