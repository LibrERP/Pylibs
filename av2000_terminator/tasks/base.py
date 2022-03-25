import abc
from collections.abc import Sized
import logging
from multiprocessing import Process, Queue, SimpleQueue
import queue
import sys
import typing


from av2000_terminator.misc.exceptions import TaskError
from av2000_terminator.terminal import AV2000Terminal
from av2000_terminator.navigation import Navigator
from av2000_terminator.misc.connection_params import ConnectionParams
from av2000_terminator.misc.exceptions import LoadingTimeout


_logger = logging.getLogger(__name__)


class AbstractReadWorker(abc.ABC, Process):

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
        # Number fo items downloaded: it's equal to list index of the last downloaded item plus 1.
        self._processed_items = 0
        self._iterations_counter = 0
        self._max_retry = max_retry
        self._av2000 = None
        self._navigator = None
        self._exception_queue = SimpleQueue()
    # end __init__

    @property
    def out_queue(self):
        return self._queue
    # end queue

    @property
    def tasks(self):
        return self._tasks
    # end queue

    def run(self):

        while self._max_retry_ok() and not self._error() and not self._task_completed():

            # Open connection to av2000
            self._av2000 = AV2000Terminal(self._connection_params)
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
        return len(self._tasks) == self._processed_items
    # end task completed

    def _error(self):
        return not self._exception_queue.empty()
    # end _error

    @abc.abstractmethod
    def _task_loop(self):
        pass
    # end _task_loop
# end AbstractReadWorker


class AbstractWriteWorker(abc.ABC, Process):

    # NOTE: TASK_NAME must be overridden by derived classes
    TASK_NAME = None

    def __init__(
            self,
            name: str,
            connection_params: ConnectionParams,
            q: Queue,
            max_retry: int = 4
    ):
        super().__init__(name=name)

        self._connection_params: ConnectionParams = connection_params
        self._queue: Queue = q
        # Number fo items downloaded: it's equal to list index of the last downloaded item plus 1.
        self._processed_items: int = 0
        self._iterations_counter: int = 0
        self._max_retry: int = max_retry
        self._av2000: AV2000Terminal
        self._navigator: Navigator
        self._exception_queue: SimpleQueue = SimpleQueue()
    # end __init__

    @property
    def in_queue(self):
        return self._queue
    # end queue

    def run(self):

        while self._max_retry_ok() and not self._error() and not self._task_completed():

            # Open connection to av2000
            self._av2000 = AV2000Terminal(self._connection_params)
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
        return len(self._tasks) == self._processed_items
    # end task completed

    def _error(self):
        return not self._exception_queue.empty()
    # end _error

    @abc.abstractmethod
    def _task_loop(self):
        pass
    # end _task_loop
# end AbstractWriteWorker


class ParallelProducer:

    def __init__(
            self,
            connection_params: ConnectionParams,
            worker_class,
            tasks_list: typing.List,
            procs_num: int = 1,
    ):

        # Check params
        if procs_num < 1:
            raise ValueError('Number of processes ("procs" parameter) must be at least 1')
        # end if

        self._connection_params = connection_params
        self._worker_class = worker_class
        self._tasks_list = tasks_list
        self._procs_num = procs_num

        # Split the ids in (more or less even) chunks
        self._workers = [
            worker_class(
                name=f'sd_{worker_id}',
                connection_params=connection_params,
                tasks=self._tasks_list[worker_id::procs_num],
                q=Queue(20),
            )
            for worker_id in range(procs_num)
        ]
    # end __init__

    def stop_workers(self):
        [wrk.terminate() for wrk in self._workers]
    # end stop_workers

    @property
    def workers_alive(self):
        procs_alive = any(wrk.is_alive() for wrk in self._workers)
        return procs_alive
    # end procs_alive

    @property
    def workers_error(self):
        error_detected = any(wrk.exitcode for wrk in self._workers)
        return error_detected
    # end worker_error

    def get_next(self):

        # Start the tasks
        [worker.start() for worker in self._workers]

        # Number of batches
        batches = max([len(worker.tasks) for worker in self._workers])

        # For each batch
        batch_index = 0
        while not self.workers_error and batch_index < batches:

            # Get the workers involved in this batch
            workers = [w for w in self._workers if batch_index < len(w.tasks)]

            # Get the batch result for the valid workers
            batch_results = self._ordered_fetch(workers)

            # Return the result serially
            for result in batch_results:
                yield result
            # end for

            _logger.info(f'Batch {batch_index + 1}/{batches} completed')

            # Update the index
            batch_index = batch_index + 1
        # end for

        # Error occurred!!
        if self.workers_error:
            self.stop_workers()
            raise TaskError(self._workers)  # Raise an error
        # end if
    # end get_next

    def _ordered_fetch(self, workers_list: typing.List[AbstractReadWorker]) -> typing.List[typing.Any]:

        batch_result = list()

        for worker in workers_list:

            result_fetched = False

            # Retrieve a batch
            while not self.workers_error and not result_fetched:
                try:
                    batch_result.append(worker.out_queue.get(timeout=3))
                    result_fetched = True
                except queue.Empty:
                    pass  # Nothing to do here, just start the next iteration
                # end try / except
            # end while
        # end for

        return batch_result
    # end _get_batch
# end ParallelProducer
