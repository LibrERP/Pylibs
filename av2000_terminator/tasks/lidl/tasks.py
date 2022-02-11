from av2000_terminator.driver import AV2000Driver
from av2000_terminator.navigation import Navigator
from av2000_terminator.misc import ConnectionParams
from av2000_terminator.misc.exceptions import NoNextPage
from av2000_terminator.navigation.pages.magazzino_vendite_acquisti.ordini_clienti.lidl import(
    TabellaClientiDestinatariLidl, TabellaArticoliLidl
)


def warehouses_info_list(connection_params: ConnectionParams):

    # Convinience aliases
    av2000: AV2000Driver = AV2000Driver(connection_params)

    # Get a navigator
    navigator: Navigator = Navigator(av2000)

    # Open connection and load suppliers page
    navigator.back_to_main_menu()
    navigator.menu_select(8)
    navigator.menu_select(20)
    navigator.menu_select(4)
    navigator.menu_select(3)

    current_page: TabellaClientiDestinatariLidl = navigator.current_page

    try:

        while True:
            for row in current_page.extract_data():
                yield row
            # end for

            current_page.scroll_next()
        # end while

    except NoNextPage:
        pass  # End of data reached
    # end try / except

    # Politely close connection
    navigator.exit()

# end lidl_warehouses_info_list


def products_info_list(connection_params: ConnectionParams):

    # Convinience aliases
    av2000: AV2000Driver = AV2000Driver(connection_params)

    # Get a navigator
    navigator: Navigator = Navigator(av2000)

    # Open connection and load suppliers page
    navigator.back_to_main_menu()
    navigator.menu_select(8)
    navigator.menu_select(20)
    navigator.menu_select(4)
    navigator.menu_select(4)

    current_page: TabellaArticoliLidl = navigator.current_page

    # Download data
    try:

        while True:
            for row in current_page.extract_data():
                yield row
            # end for

            current_page.scroll_next()
        # end while

    except NoNextPage:
        pass  # End of data reached
    # end try / except

    # end while

    # Politely close connection
    navigator.exit()

# end lidl_products_info_list
