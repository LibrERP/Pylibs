from av2000_terminator.misc import keys
import time

from av2000_terminator.navigation.base import AbstractPage, MenuItem, FakePage
from av2000_terminator.misc.exceptions import NoNextPage

_TABLE_LIMIT = ('q' * 80, '-' * 80)


class TabellaClientiDestinatariLidl(AbstractPage):

    PAGE_NAME = 'Tabella clienti/destinatari Lidl'
    LIST_LAST_LINE = 20
    PAGE_LAST_LINE = 22

    def ready(self):
        # Check for main components of the page to be here
        name_ok = self.name == self.PAGE_NAME
        table_end_ok = self._av2000.display_lines[self.LIST_LAST_LINE + 1].strip() in _TABLE_LIMIT

        # Check if last line has been modified
        ll_modified = self.PAGE_LAST_LINE in self._av2000.modified_lines

        return name_ok and table_end_ok and ll_modified

    # end ready

    def extract_data(self):

        data_lines = self._av2000.display_lines[4:20]

        data_records = [
            {
                'nazione': line[0:5].strip(),
                'lager': line[41:51].strip(),
                'cliente': line[52:59].strip(),
                'destinazione': line[59:65].strip(),
                'luogo_consegna': line[66:73].strip(),
                'pallet': line[73:76].strip() and int(line[73:76].strip()),
                'giorni_consegna': line[76:].strip() and int(line[76:].strip()),
            }
            for line in data_lines
            if line.strip()
        ]

        return data_records

    # end get_page_data

    def scroll_next(self):
        """
            Loads the next page of the suppliers list.
        """
        if self.is_last_page():
            raise NoNextPage()
        else:
            self._av2000.send_seq(keys.PG_DN)
        # end if

        # Wait for next page to be loaded before returning.
        self._av2000.wait_ready(self.ready, self._navigator.timeout_sec)

    # end scroll_next

    def is_last_page(self):
        # Try to be reasonably sure the last line has been fully loaded
        time.sleep(0.5)
        self._av2000.update()

        # The page is the last one if the last line of the list is empty
        last_page = self._av2000.display_lines[self.LIST_LAST_LINE].strip() == ''

        # Return the result
        return last_page

    # end is_last_page

# end TabellaClientiDestinatariLidl


class TabellaArticoliLidl(AbstractPage):

    PAGE_NAME = 'Tabella articoli Lidl'
    LIST_LAST_LINE = 20
    PAGE_LAST_LINE = 22

    def ready(self):

        # Check for main components of the page to be here
        name_ok = self.name == self.PAGE_NAME
        table_end_ok = self._av2000.display_lines[self.LIST_LAST_LINE + 1].strip() in _TABLE_LIMIT

        # Check if last line has been modified
        ll_modified = self.PAGE_LAST_LINE in self._av2000.modified_lines

        return name_ok and table_end_ok and ll_modified

    # end ready

    def extract_data(self):

        data_lines = self._av2000.display_lines[5:21]

        records = [
            (x[0].strip(), x[1].strip())
            for x in
            zip(data_lines[::2], data_lines[1::2])
        ]

        data_records = [
            {
                'country': rec[0],
                'lidl_code': rec[1][0:40].strip(),
                'unit': rec[1][41:49].strip(),
                'code_av2000': rec[1][49:64].strip(),
                'description': rec[1][65:].strip(),
            }
            for rec in records
            if rec[0].strip()
        ]

        return data_records

    # end get_page_data

    def scroll_next(self):
        """
            Loads the next page of the suppliers list.
        """
        if self.is_last_page():
            raise NoNextPage
        else:
            self._av2000.send_seq(keys.PG_DN)
        # end if

        # Wait for next page to be loaded before returning.
        self._av2000.wait_ready(self.ready, self._navigator.timeout_sec)

    # end scroll_next

    def is_last_page(self):
        # Try to be reasonably sure the last line has been fully loaded
        time.sleep(0.5)
        self._av2000.update()

        # The page is the last one if the last line of the list is empty
        last_page = self._av2000.display_lines[self.LIST_LAST_LINE].strip() == ''

        # Return the result
        return last_page

    # end is_last_page

# end TabellaArticoliLidl


class MainMenu(AbstractPage):

    PAGE_NAME = 'Import ordini da xls Lidl'

    _MENU_ITEMS = {
        1: MenuItem('Import ordini dal xls Lidl', FakePage),
        2: MenuItem('Assegnazione lotti/prezzi assenti', FakePage),
        3: MenuItem('Tabella clienti/destinatari Lidl', TabellaClientiDestinatariLidl),
        4: MenuItem('Tabella articoli Lidl', TabellaArticoliLidl),
        6: MenuItem('Definizione lotti confezionamento', FakePage),
        16: MenuItem('Parametri import ordini xls Lidl', FakePage),
        22: MenuItem('Stampa definizione lotti confez.', FakePage),
    }

    def ready(self):

        name_ok = self.name == self.PAGE_NAME
        menu_ok = self._av2000.display_lines[18].strip() == '16 Parametri import ordini xls Lidl'

        return name_ok and menu_ok

    # end ready

# end MainMenu
