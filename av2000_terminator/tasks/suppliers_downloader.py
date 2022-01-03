from collections.abc import Sized
from multiprocessing import Queue

from . base import AbstractTask
from .. import ConnectionParams


class SuppliersDownloadTask(AbstractTask):
    
    TASK_NAME = 'Suppliers downloader'

    def _task_loop(self):

        # Convinience aliases
        navigator = self._navigator
        queue = self._queue
        ids_list = self._tasks

        # Open connection and load suppliers page
        navigator.current_page.menu_select(3)
        navigator.current_page.menu_select(9)

        # Download suppliers details
        for list_idx in range(self._fetched_items, len(ids_list)):

            tgt_id = ids_list[list_idx]

            # Load supplier data
            navigator.current_page.show_supplier(tgt_id)

            # Save supplier data and set a checkpoint
            queue.put(navigator.current_page.get_data())
            self._fetched_items = self._fetched_items + 1

            # Prepare for the next supplier
            navigator.back()
            
            # Print report
            if (self._fetched_items % 25) == 0:
                print(f'{self.name} {self._fetched_items}')
            # end if

        # end for

    # end _task_loop

# end SuppliersDownloadTask
