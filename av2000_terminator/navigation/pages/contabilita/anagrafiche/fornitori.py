import re
import time
from pathlib import Path

from sshterminal import keys
from sshterminal.xtractor import Xtractor
from av2000_terminator.navigation.base import AbstractForm

from .partner import PartnersListPage, PartnersMainPage


# - - - - - - - - - - - - - -
# Fornitori
# - - - - - - - - - - - - - -
class ListaFornitori(PartnersListPage):
    pass
# end ListaFornitori


class DettagliFornitore(AbstractForm):

    PAGE_NAME = 'Anagrafica fornitori'

    DATA_FILE_PATH = Path(__file__).parent.resolve() / 'DettagliFornitore.json'

    _LAST_DATA_LINE_RE = re.compile(r'^\s*Cognome .*Nome .*% imp calcolo RA \s*')
    _LAST_SCREEN_LINE = 'F7   Invio  Esc  Fine   F3   Note  F6   Collegamenti'

    def ready(self):
        lines = self._av2000.display_lines

        last_data_line_ok = self._LAST_DATA_LINE_RE.match(lines[36])
        bottom_menu_ok = lines[38].strip() == self._LAST_SCREEN_LINE
        name_ok = self.name == self.PAGE_NAME

        return last_data_line_ok and bottom_menu_ok and name_ok
    # end ready

    def back(self):
        self._av2000.send_seq(keys.END)
    # end back

    def commit_changes(self):
        super().commit_changes()

        time.sleep(0.1)

        # Manage possible errors
        if self._av2000.display_lines[-3].startswith('MSG0239 Partita IVA gia\' usata per'):
            self._av2000.send_seq(self._av2000.RETURN_CHAR)

        elif self._av2000.display_lines[-3].startswith('MSG00"% Partita IVA errata'):
            self._av2000.send_seq(keys.F[4])

        elif self._av2000.display_lines[-3].startswith('MSG'):
            raise self.FormError(self._av2000.display_lines[-3].replace('q', '').strip())

        # end if
    # end commit

    def _ready_other_1(self):
        lines = self._av2000.display_lines

        last_data_line_ok = lines[32].strip().endswith('Pag.Avanti per altri dati')
        bottom_menu_ok = lines[34].strip() == 'F1   Invio  Esc  Fine   F6   Collegamenti trasversali PSucc Altri Dati'

        return last_data_line_ok and bottom_menu_ok
    # end _ready_other_1

    def _ready_other_2(self):
        lines = self._av2000.display_lines

        last_data_line_ok = lines[32].strip().endswith('Pagina avanti per altri dati')
        bottom_menu_ok = lines[35].strip() == 'PSucc Altri dati'

        return last_data_line_ok and bottom_menu_ok
    # end _ready_other_2

    def _ready_other_3(self):
        lines = self._av2000.display_lines

        last_data_line_ok = lines[30].strip().endswith('2=EAN bottiglia')
        bottom_menu_ok = lines[
            35
        ].strip() == 'F1   Invio  Esc  Fine   F6   Collegamenti trasversali PPrec Dati Precedenti'

        return last_data_line_ok and bottom_menu_ok
    # end _ready_other_3
# end DettagliFornitore


class AnagraficaFornitori(PartnersMainPage):
    PAGE_NAME = 'Anagrafica fornitori'

    PARTNERS_LIST_PAGE = ListaFornitori
    PARTNER_DETAILS_PAGE = DettagliFornitore

    def _query_wizard_ready(self) -> bool:
        scrn = self._av2000.display_lines

        lls_query_ok = scrn[19][3:].strip().startswith(
            'Visualizza fornitore obsoleti (S/N)'
        )
        lls_window_ok = scrn[38].startswith('Invio Fine')

        return lls_query_ok and lls_window_ok
    # end _query_ui_ready
# end AnagraficaFornitori
