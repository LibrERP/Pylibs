import math
import multiprocessing
from queue import Empty as QueueEmpty
import typing

from av2000_terminator.driver import AV2000Driver
from av2000_terminator.navigation import Navigator
from av2000_terminator.misc import ConnectionParams
from av2000_terminator.misc.exceptions import NoNextPage, TaskError
from av2000_terminator.tasks import SuppliersDownloadTask


class Tasker:

    NAMES = {
        'main_menu': 'AV2000'
    }

    def __init__(self, connection_params: ConnectionParams):
        self._connection_params = connection_params
    # end __init__

    def lidl_warehouses_info_list(self):

        # Convinience aliases
        av2000: AV2000Driver = AV2000Driver(self._connection_params)

        # Get a navigator
        navigator: Navigator = Navigator(av2000)

        # Open connection and load suppliers page
        navigator.back_to_main_menu()
        navigator.menu_select(8)
        navigator.menu_select(20)
        navigator.menu_select(4)
        navigator.menu_select(3)

        try:
            while True:
                yield navigator.current_page.extract_data()
                navigator.current_page.scroll_next()
            # end while
        except NoNextPage:
            pass  # End of data reached
        # end try / except

        # Politely close connection
        navigator.exit()

    # end lidl_warehouses_info_list

    def lidl_products_info_list(self):

        # Convinience aliases
        av2000: AV2000Driver = AV2000Driver(self._connection_params)

        # Get a navigator
        navigator: Navigator = Navigator(av2000)

        # Open connection and load suppliers page
        navigator.back_to_main_menu()
        navigator.menu_select(8)
        navigator.menu_select(20)
        navigator.menu_select(4)
        navigator.menu_select(4)

        # Download data
        try:
            while True:
                yield navigator.current_page.extract_data()
                navigator.current_page.scroll_next()
            # end while
        except NoNextPage:
            pass  # End of data reached
        # end try / except

        # end while

        # Politely close connection
        navigator.exit()

    # end lidl_products_info_list

    def suppliers_list(self):

        # Convinience aliases
        av2000: AV2000Driver = AV2000Driver(self._connection_params)

        # Get a navigator
        navigator: Navigator = Navigator(av2000)

        # Load suppliers list page
        navigator.current_page.menu_select(3)
        navigator.current_page.menu_select(9)
        navigator.current_page.open_suppliers_list()

        try:
            while True:
                yield navigator.current_page.extract_data()
                navigator.current_page.scroll_next()
            # end while
        except NoNextPage:
            pass  # End of data reached
        # end try / except
        
        navigator.exit()

    # end suppliers_list

    def suppliers_batch_get(self, ids_list, procs_num=1):
        return self._build_parallel_producer(
            task_class=SuppliersDownloadTask,
            tasks_list=ids_list,
            procs_num=procs_num,
            max_retry=4,
        )
    # end suppliers_get
    
    def exit(self):
        self._navigator.exit()
    # end exit

    def _build_parallel_producer(
        self,
        task_class,
        tasks_list: typing.List,
        procs_num: int = 1,
        max_retry: int = 4
    ):
        
        # Status variables
        procs_alive = True
        error = False
        
        # Check params
        if procs_num < 1:
            raise ValueError('Number of processes ("procs" parameter) must be at least 1')
        # end if
        
        # Build the queue
        results_queue = multiprocessing.Queue(200)
        
        # Split the ids in (more or less even) chunks
        chunk_s = math.ceil(len(tasks_list) / procs_num)
        
        # Build the tasks
        procs = [
            task_class(
                name=f'sd_{p_num}',
                connection_params=self._connection_params,
                tasks=tasks_list[chunk_s * p_num:chunk_s * (p_num + 1)],
                q=results_queue,
            )
            for p_num in range(procs_num)
        ]
        
        # Start the tasks
        [p.start() for p in procs]
        
        # Generator
        while (procs_alive or not results_queue.empty()) and not error:

            try:
                x = results_queue.get(timeout=3)
                yield x
            except QueueEmpty:
                # Nothing to do here, just start the next iteration
                pass
            # end try / except

            # Update status variables
            procs_alive = any(p.is_alive() for p in procs)
            error = any(p.exitcode for p in procs)
        # end while
        
        # Error occurred!!
        if error:
            [p.terminate() for p in procs]  # Terminate running tasks
            raise TaskError(procs)  # Raise an error
        # end if
        
    # end _get_paralle_producer

# end Tasker
