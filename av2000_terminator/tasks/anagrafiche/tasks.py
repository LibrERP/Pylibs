import logging

import typing

from av2000_terminator.misc.connection_params import ConnectionParams
from av2000_terminator.terminal import AV2000Terminal
from av2000_terminator.navigation import Navigator
from av2000_terminator.misc.exceptions import NoNextPage

from av2000_terminator.tasks.base import ParallelProducer
from sshterminal import keys

from . workers import SuppliersDownloader
from ...navigation.base.form import Field
from ...navigation.pages.contabilita.anagrafiche.fornitori import ListaFornitori


class SuppliersReader:

    def __init__(self, connection_params: ConnectionParams):
        self._connection_params = connection_params
    # end __init__

    def list_suppliers(self):

        # Number of items read
        counter = 0
        trigger_print = 100

        # Build the driver object
        av2000: AV2000Terminal = AV2000Terminal(self._connection_params)

        # Get a navigator
        navigator: Navigator = Navigator(av2000)

        # Load suppliers list page
        navigator.current_page.menu_select(3)  # contabilita.MainMenu
        navigator.current_page.menu_select(9)  # AnagraficaFornitori
        navigator.current_page.open_partners_list()  # ListaFornitori

        current_page: ListaFornitori = navigator.current_page

        print('Suppliers list - Start downloading process...')

        try:
            while True:
                page_data = current_page.extract_data()

                counter += len(page_data)
                if counter > trigger_print:
                    trigger_print += 100
                    print(f'Suppliers list - Downloaded {counter} items.')
                # end if

                for row in page_data:
                    yield row
                # end for

                current_page.scroll_next()
            # end while

        except NoNextPage:
            # End of data reached
            print(f'Suppliers list - Download completed. Total items: {counter}')
        # end try / except

        navigator.exit()
    # end suppliers_list

    def get_suppliers_producer(self, ids_list: typing.List = None, procs_num: int = 1) -> ParallelProducer:
        '''
            Returns a list of suppliers ordered by AV2000 id from the smallest id to the largest id,
            this should be equivalent to ordering from the oldest record to the most recent one,
            this way if a record collides with another the most recent version is actually imported.

            If ids_list
        '''

        # Dowload list of all suppliers if parameter ids_list is not specified
        if ids_list in (None, False):
            ids_list = list(self.list_suppliers())
            ids_list.sort(key=lambda r: r['codice'])

            # Solo per test rapidi
            # ids_list = all_suppliers[:48]
        # end if

        return ParallelProducer(
            connection_params=self._connection_params,
            worker_class=SuppliersDownloader,
            tasks_list=ids_list,
            procs_num=procs_num,
        )
    # end get_suppliers
# end SuppliersReader


class SuppliersWriter:

    def __init__(self, connection_params: ConnectionParams):

        class_obj = self.__class__
        self._logger = logging.getLogger(f'{class_obj.__module__}.{class_obj.__qualname__}')

        self._connection_params = connection_params

        self._av2000: AV2000Terminal = None
        self._navigator: Navigator = None
    # end __init__

    @property
    def connected(self):
        if self._av2000 and not self._av2000.closed:
            return True
        else:
            return False
        # end if
    # end connected

    def connect(self):

        if not self.connected:
            self._av2000 = AV2000Terminal(self._connection_params)
            self._navigator = Navigator(self._av2000)

            self._logger.info('Back to main menu')
            self._navigator.back_to_main_menu()
            self._logger.info('Open "Archivi di base area contabile"')
            self._navigator.current_page.menu_select(3)
            self._logger.info('Open "Anagrafica fornitori"')
            self._navigator.current_page.menu_select(9)
            self._logger.info('Writer ready!')
        # end if

    # end connect

    def close(self):
        if self.connected:
            self._navigator.exit()
        # end if
    # end close

    def write_data(self, supplier_code: typing.Union[int, str], data: dict):

        sc = str(supplier_code)

        # Open supplier page
        self._logger.info(f'[supplier {sc:>5s}] Opening partner page')
        self._navigator.current_page.show_partner(sc)

        # Write data
        self._logger.info(f'[supplier {sc:>5s}] Setting values for fields')
        for key, value in data.items():

            if isinstance(key, (int, str)):
                # Single level key
                tgt_field = self._navigator.current_page.fields[key]
            elif isinstance(key, tuple):
                # Multi level key
                pointer = self._navigator.current_page.fields
                for key_part in key:
                    pointer = pointer[key_part]
                # end for

                tgt_field = pointer
            else:
                assert False
            # end if

            tgt_field.data = value
        # end for

        # Save and close page
        self._logger.info(f'[supplier {sc:>5s}] Committing changes')

        try:
            self._navigator.commit_changes()

        except Field.FieldValueError as fve:
            self._logger.error(str(fve))
            self.exit_on_error()
            self._av2000.print_screen()
            raise fve

        except Exception as e:
            self._av2000.print_screen()
            raise e
        # end try / except

        self._logger.info(f'[supplier {sc:>5s}] Completed')
    # end write_data

    def exit_on_error(self):
        self._av2000.send_seq(keys.END)
        self._av2000.send_seq(keys.END)
    # end exit_on_error
# end SuppliersWriter


class AnagraficheID:
    """
    Ritorna gli ID di AV2000 dell'ultimo record creato in AV2000 per clienti e fornitori
    """

    def __init__(self, connection_params: ConnectionParams):

        class_obj = self.__class__
        self._logger = logging.getLogger(f'{class_obj.__module__}.{class_obj.__qualname__}')

        self._connection_params = connection_params

        self._av2000: AV2000Terminal = None
        self._navigator: Navigator = None
    # end __init__

    @property
    def connected(self):
        if self._av2000 and not self._av2000.closed:
            return True
        else:
            return False
        # end if
    # end connected

    def connect(self):

        if not self.connected:
            self._av2000 = AV2000Terminal(self._connection_params)
            self._navigator = Navigator(self._av2000)

            self._logger.info('Back to main menu')
            self._navigator.back_to_main_menu()
            self._logger.info('Open "Archivi di base area contabile"')
            self._navigator.current_page.menu_select(3)
            self._logger.info('Ready to retrieve ids!')
        # end if

    # end connect

    def close(self):
        if self.connected:
            self._navigator.exit()
        # end if
    # end close

    def get_ids(self):

        # Ensure we are connected to AV2000
        self.connect()

        # Open page
        self._logger.info('Open "Progressivi base contabilità"')
        self._navigator.current_page.menu_select(3)

        # Retrieve data
        self._logger.info('Getting IDs')
        last_used_ids = {
            'client': self._navigator.current_page.max_client_id,
            'supplier': self._navigator.current_page.max_supplier_id,
        }

        # Back to menu
        self._logger.info('Back to menu "Archivi di base area contabile"')
        self._navigator.back()

        # Return  data
        return last_used_ids
    # end get_ids
# end SuppliersWriter
