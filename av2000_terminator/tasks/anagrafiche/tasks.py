from av2000_terminator.misc.connection_params import ConnectionParams
from av2000_terminator.driver import AV2000Driver
from av2000_terminator.navigation import Navigator
from av2000_terminator.misc.exceptions import NoNextPage

from av2000_terminator.tasks.base import ParallelProducer

from . workers import SuppliersDownloader
from ...navigation.pages.contabilita.anagrafiche.fornitori import ListaFornitori


def suppliers_list(connection_params: ConnectionParams):

    # Number of items read
    counter = 0
    trigger_print = 100

    # Build the driver object
    av2000: AV2000Driver = AV2000Driver(connection_params)

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


def suppliers_get_batch(connection_params: ConnectionParams, ids_list, procs_num: int = 1) -> ParallelProducer:
    return ParallelProducer(
        connection_params=connection_params,
        worker_class=SuppliersDownloader,
        tasks_list=ids_list,
        procs_num=procs_num,
    )
# end suppliers_get_batch


def suppliers_get_all(connection_params: ConnectionParams, procs_num: int = 1) -> ParallelProducer:

    all_suppliers = list(suppliers_list(connection_params))

    return ParallelProducer(
        connection_params=connection_params,
        worker_class=SuppliersDownloader,
        tasks_list=all_suppliers,
        procs_num=procs_num,
    )
# end suppliers_get_batch
