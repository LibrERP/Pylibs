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


def suppliers_list(connection_params: ConnectionParams):

    # Number of items read
    counter = 0
    trigger_print = 100

    # Build the driver object
    av2000: AV2000Terminal = AV2000Terminal(connection_params)

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


def suppliers_get_batch(
        connection_params: ConnectionParams, ids_list, procs_num: int = 1
) -> ParallelProducer:
    return ParallelProducer(
        connection_params=connection_params,
        worker_class=SuppliersDownloader,
        tasks_list=ids_list,
        procs_num=procs_num,
    )
# end suppliers_get_batch


def suppliers_get_all(
        connection_params: ConnectionParams, procs_num: int = 1
) -> ParallelProducer:
    '''
        Return a list of suppliers ordered by AV2000 id from the smallest id to the largest id,
        this should be equivalent to ordering from the oldest record to the most recent one,
        this way if a record collides with another the most recent version is actually imported.
    '''

    all_suppliers = list(suppliers_list(connection_params))
    all_suppliers.sort(key=lambda r: r['codice'])

    # Solo per test rapidi
    # all_suppliers = all_suppliers[:48]

    return suppliers_get_batch(
        connection_params=connection_params,
        ids_list=all_suppliers,
        procs_num=procs_num,
    )
# end suppliers_get_batch


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

            self._navigator.back_to_main_menu()
            self._navigator.current_page.menu_select(3)
            self._navigator.current_page.menu_select(9)
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
            self._navigator.current_page.fields[key].data = value
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
