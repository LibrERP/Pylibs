import abc
import re
import time
import typing

from sshterminal import keys
from av2000_terminator.misc.exceptions import LoadingTimeout, NoNextPage
from av2000_terminator.navigation.base import AbstractPage


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Generic Partner
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class PartnersListPage(AbstractPage):
    # Last line of the list of supplier/clients
    LIST_LAST_LINE = 38

    def __init__(self, navigator):
        super().__init__(navigator)

        self._load_status = 'ready'

    # end __init__

    def scroll_next(self):
        """
            Loads the next page of the suppliers list.
        """

        # Check what sequence must be sent to load the next page
        self._av2000.send_seq(keys.PG_DN)

        # Wait for next page to be loaded.
        try:
            self._av2000.wait_ready(self.ready, self._navigator.timeout_sec)
        except LoadingTimeout as lte:
            if self.is_last_page():
                raise NoNextPage
            else:
                raise lte
            # end if
        # end try / except

    # end scroll_next

    def extract_data(self):

        data_lines = self._av2000.display_lines[6:20]

        entities_list = list(
            map(
                lambda line: {
                    'codice': int(line[2:8].strip()),
                    'rag_soc': line[9:50].strip(),
                    'p_iva': line[50:66].strip(),
                },
                # Exclude empty lines
                filter(lambda x: x[2:66].strip() != '', data_lines)
            )
        )

        return entities_list

    # end extract_data

    def is_last_page(self):

        # Try to be reasonably sure the last line has been fully loaded
        time.sleep(2)
        self._av2000.update()

        # Get the lst line and perform the check
        ll = self._av2000.display_lines[self.LIST_LAST_LINE]
        is_l_p = ll.strip() in ('Invio Fine', 'Invio Fine  PPrec')

        # Return the result
        return is_l_p

    # end is_last_page

    def has_next_page(self):
        ll = self._av2000.display_lines[self.LIST_LAST_LINE]
        has_next = bool(re.match(r'^Invio Fine  (PPrec PSucc|PSucc)\s*$', ll))
        return has_next

    # end has_next_page

    def ready(self) -> bool:

        # NOTE: last page case deliberately ignore!!
        # If the page is the last page it will never be ready and a
        # call to this method will raise a LoadingTimeout Exception.
        # It's up to the caller to check if the exception has been
        # raised because it's the last page.
        # The choice to ignore "last page case" was made for performance
        # reasons and because 99% of the times the exception will be
        # handled by the scroll_next() method.

        # Check if last line has been modified
        ll_modified = self.LIST_LAST_LINE in self._av2000.modified_lines

        return ll_modified

    # end ready

    def back(self):
        # First "END" closes the list and reopens the query window
        self._av2000.send_seq(keys.END)
        time.sleep(0.5)
        # Second "END" closes the query window and returns to the
        # main "Anagrafica Fornitori" page
        self._av2000.send_seq(keys.END)
        time.sleep(0.5)
    # end back
# end ListaPartner


class PartnersMainPage(AbstractPage):
    PAGE_NAME = None

    PARTNERS_LIST_PAGE = None
    PARTNER_DETAILS_PAGE = None

    def show_partner(self, supplier_id: typing.Union[int, str]):
        self._av2000.send_line(str(supplier_id))
        self._navigator.set_current_page(self.PARTNER_DETAILS_PAGE)

    # end show_partner

    def open_partners_list(self):
        page_load_timeout = 3

        # Open query form
        self._av2000.send_seq(keys.SHIFT_F[1])
        self._av2000.wait_ready(self._query_wizard_ready, page_load_timeout)

        # Include obsolete suppliers
        self._av2000.send_seq(keys.ARROW['down'])
        self._av2000.send_seq(keys.ARROW['down'])
        self._av2000.send_seq(keys.ARROW['down'])
        self._av2000.send_seq('S')

        self._av2000.send_line()

        self._navigator.set_current_page(self.PARTNERS_LIST_PAGE)

    # end open_partners_list

    def ready(self):
        text = self._av2000.text_lines
        last_line = text and text[-1] or ''

        name_ok = self.name == self.PAGE_NAME
        menu_ok = 'Codici in sequenza' in last_line

        return name_ok and menu_ok

    # end ready

    @abc.abstractmethod
    def _query_wizard_ready(self) -> bool:
        scrn = self._av2000.display_lines

        lls_query_ok = scrn[19][3:].startswith(
            'Visualizza fornitore obsoleti (S/N)'
        )
        lls_window_ok = scrn[38].startswith('Invio Fine')

        return lls_query_ok and lls_window_ok
    # end _query_ui_ready
# end PartnersMain
