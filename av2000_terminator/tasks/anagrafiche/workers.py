import datetime

from av2000_terminator.tasks.base import AbstractWorker


class SuppliersDownloader(AbstractWorker):
    
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
        for list_idx in range(self._processed_items, len(ids_list)):

            tgt_id = ids_list[list_idx]['codice']

            print(f'[{self.name} - {datetime.datetime.now()}] partner {tgt_id}] ({self._processed_items + 1}/{len(ids_list)})')

            # Load supplier data
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] show_partner - begin')
            # ts_start = datetime.datetime.now()
            navigator.current_page.show_partner(tgt_id)
            # elapsed_time = datetime.datetime.now() - ts_start
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] show_partner - end ({elapsed_time} sec)')

            # Save supplier data and set a checkpoint
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] get_data - begin')
            # ts_start = datetime.datetime.now()
            page_data = navigator.current_page.get_data()
            # elapsed_time = datetime.datetime.now() - ts_start
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] get_data - end ({elapsed_time} sec')

            # Save supplier data and set a checkpoint
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] enqueue - begin')
            # ts_start = datetime.datetime.now()
            queue.put(page_data)
            self._processed_items = self._processed_items + 1
            # elapsed_time = datetime.datetime.now() - ts_start
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] enqueue - end ({elapsed_time} sec')

            # Prepare for the next supplier
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] back - begin')
            # ts_start = datetime.datetime.now()
            navigator.back()
            # elapsed_time = datetime.datetime.now() - ts_start
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] back - end ({elapsed_time} sec')

            # Print report
            if (self._processed_items % 25) == 0:
                print(f'{self.name} {self._processed_items}')
            # end if

        # end for
    # end _task_loop
# end SuppliersDownloader


class SuppliersUploader(AbstractWorker):
    TASK_NAME = 'Suppliers uploader'

    def _task_loop(self):

        # Convinience aliases
        navigator = self._navigator
        queue = self._queue
        ids_list = self._tasks

        # Open connection and load suppliers page
        navigator.current_page.menu_select(3)
        navigator.current_page.menu_select(9)

        # Download suppliers details
        for list_idx in range(self._processed_items, len(ids_list)):

            tgt_id = ids_list[list_idx]['codice']

            print(
                f'[{self.name} - {datetime.datetime.now()}] partner {tgt_id}] ({self._processed_items + 1}/{len(ids_list)})')

            # Load supplier data
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] show_partner - begin')
            # ts_start = datetime.datetime.now()
            navigator.current_page.show_partner(tgt_id)
            # elapsed_time = datetime.datetime.now() - ts_start
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] show_partner - end ({elapsed_time} sec)')

            # Save supplier data and set a checkpoint
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] get_data - begin')
            # ts_start = datetime.datetime.now()
            page_data = navigator.current_page.get_data()
            # elapsed_time = datetime.datetime.now() - ts_start
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] get_data - end ({elapsed_time} sec')

            # Save supplier data and set a checkpoint
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] enqueue - begin')
            # ts_start = datetime.datetime.now()
            queue.put(page_data)
            self._processed_items = self._processed_items + 1
            # elapsed_time = datetime.datetime.now() - ts_start
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] enqueue - end ({elapsed_time} sec')

            # Prepare for the next supplier
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] back - begin')
            # ts_start = datetime.datetime.now()
            navigator.back()
            # elapsed_time = datetime.datetime.now() - ts_start
            # print(f'[{self.name} - {datetime.datetime.now()} - id: {tgt_id}] back - end ({elapsed_time} sec')

            # Print report
            if (self._processed_items % 25) == 0:
                print(f'{self.name} {self._processed_items}')
            # end if
        # end for
    # end _task_loop
# end SuppliersUploader
