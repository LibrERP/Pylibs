import abc
from collections.abc import Sized
import logging
import math
from multiprocessing import Process, Queue, SimpleQueue
import queue
import sys
import typing


from av2000_terminator.misc.exceptions import TaskError
from av2000_terminator.driver import AV2000Driver
from av2000_terminator.navigation import Navigator
from av2000_terminator.misc.connection_params import ConnectionParams
from av2000_terminator.misc.exceptions import LoadingTimeout


_logger = logging.getLogger(__name__)


class AbstractWorker(abc.ABC, Process):

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


class ParallelProducer:

    def __init__(self, connection_params: ConnectionParams, worker_class, tasks_list: typing.List, procs_num: int = 1):

        # Check params
        if procs_num < 1:
            raise ValueError('Number of processes ("procs" parameter) must be at least 1')
        # end if

        self._connection_params = connection_params
        self._worker_class = worker_class
        self._tasks_list = tasks_list
        self._procs_num = procs_num

        # Split the ids in (more or less even) chunks
        chunk_s = math.ceil(len(self._tasks_list) / procs_num)

        # Build the queue
        self._results_queue = Queue(200)

        # Build the tasks
        self._worker_procs = [
            worker_class(
                name=f'sd_{p_num}',
                connection_params=connection_params,
                tasks=tasks_list[chunk_s * p_num:chunk_s * (p_num + 1)],
                q=self._results_queue,
            )
            for p_num in range(procs_num)
        ]
    # end __init__

    def stop_workers(self):
        [p.terminate() for p in self._worker_procs]
    # end stop_workers

    @property
    def workers_alive(self):
        procs_alive = any(p.is_alive() for p in self._worker_procs)
        return procs_alive
    # end procs_alive

    @property
    def workers_error(self):
        error_detected = any(p.exitcode for p in self._worker_procs)
        return error_detected
    # end worker_error

    def get_next(self):

        # Start the tasks
        [p.start() for p in self._worker_procs]

        # Generator
        while (self.workers_alive or not self._results_queue.empty()) and not self.workers_error:

            try:
                x = self._results_queue.get(timeout=3)
                yield x
            except queue.Empty:
                # Nothing to do here, just start the next iteration
                pass
            # end try / except
        # end while

        # Error occurred!!
        if self.workers_error:
            self.stop_workers()
            raise TaskError(self._worker_procs)  # Raise an error
        # end if
    # end get_next
# end ParallelProducer
