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

    def get_data(self):
        xt = Xtractor(self._av2000.display_lines)

        # Extract data
        # ts_start = datetime.datetime.now()
        # print(f'[page_fornito - {datetime.datetime.now()}] data main - start')
        data = {
            'codice': xt.x(3, (6, 14)),
            'ragione_sociale': xt.x(3, 29),
            'ragione_sociale_agg': xt.x(4, 30),
            'indirizzo': xt.x(5, 23),
            'cap': xt.x(6, (30, 35)),
            'localita': xt.x(6, (37, 77)),
            'provincia': xt.x(6, (78, 81)),
            'piano_conti': {
                'l1': xt.x(7, (30, 34), int),
                'l2': xt.x(7, (35, 39), int),
                'nome': xt.x(7, 40),
            },
            'cf_rappresentante': xt.x(8, (37, 54)),
            'usare_per_spesometro': xt.x(8, (79, 80)),
            'partita_iva': xt.x(9, (26, 42)),
            'codice_fiscale': xt.x(9, (53, 69)),
            'registro_imprese': xt.x(9, (82, 93)),
            'telefono': xt.x(10, (26, 49)),
            'fax': xt.x(10, (53, 73)),
            'stato_giuridico': xt.x(10, (92, 93)),
            'email': xt.x(11, (26, 66)),
            'cellulare': xt.x(11, (73, 93)),
            'pec': xt.x(12, 26),
            'url_internet': xt.x(14, 34),
            'pagamento': {
                'codice': xt.x(15, (34, 40)),
                'descizione': xt.x(15, 40),
            },
            'iban': (
                xt.x(16, (31, 33)),
                xt.x(16, (35, 36)),
                xt.x(16, (37, 38)),
                xt.x(16, (39, 44)),
                xt.x(16, (45, 50)),
                xt.x(16, (51, 63))
            ),
            'codici_iva':{
                'primario': {
                    'codice': xt.x(17, (34, 37)),
                    'descrizione': xt.x(17, (38, 76)),
                },
                'altri': [
                    {
                        'codice': xt.x(17, (83, 86)),
                        'descrizione': '',
                    },
                    {
                        'codice': xt.x(17, (88, 91)),
                        'descrizione': '',
                    },
                ]
            },
            'codice_comune': {
                'cod': xt.x(18, (34, 40), int),
                'nome': xt.x(18, (41, 76)),
            },
            'codice_regione': {
                'cod': xt.x(19, (34, 36), int),
                'nome': xt.x(19, 37),
            },
            'codice_nazione': {
                'cod': xt.x(20, (34, 37), int),
                'nome': xt.x(20, 38),
            },
            'codice_comune_2018': {
                'cod': xt.x(18, (95, 101), int),
            },
            'porto': {
                'cod': xt.x(21, (34, 37), int),
                'nome': xt.x(21, 38),
            },
            'banca_interna_prev': {
                'cod': xt.x(22, (34, 37), int),
                'nome': xt.x(21, 38),
            },
            'icqrf': xt.x(20, (34, 42)),
            'nascita': {
                'data': xt.x(24, (28, 38)),
                'comune': xt.x(24, (46, 52)),
                'provincia': xt.x(24, (72, 74)),
                'sesso': xt.x(24, (82, 83)),
            },
            'allegato': xt.x(26, (28, 29)),
            'ritenuta_acconto_pct': xt.x(26, (99, 104), float),
            'contropartite': [
                {
                    'l1': xt.x(l_ix, (28, 32)),
                    'l2': xt.x(l_ix, (33, 37)),
                    'l3': xt.x(l_ix, (38, 44)),
                    'descrizione': xt.x(l_ix, 45),
                }
                for l_ix in range(27, 30)
                if xt.x(l_ix, (28, 32))
            ],
            'note_estratto_conto': xt.x(31, (38, 68)),
            'persona_da_contattare': xt.x(32, (38, 68)),
            'obsoleto': xt.x(32, (92, 93)),
            'codice_ipa': xt.x(33, (25, 32)),
            'sconti': [
                xt.x(35, (72 + (ix * 6), 72 + 5 + (ix * 6)))
                for ix in range(4)
                if xt.x(35, (72 + (ix * 6), 72 + 5 + (ix * 6)))
            ],
            'cognome': xt.x(36, (25, 45)),
            'nome': xt.x(36, (51, 71)),
            'pct_imponibile_calcolo_ra': xt.x(36, (89, 95)),
            'annotazioni': {
                'generiche': '',
                'iso': '',
            },
        }
        # ts_end = datetime.datetime.now()
        # print(f'[page_fornito - {datetime.datetime.now()}] data main - end ({ts_end - ts_start} sec)')

        # Annotations
        # ts_start = datetime.datetime.now()
        self._av2000.send_seq(keys.F[3])
        time.sleep(0.1)
        # ts_end = datetime.datetime.now()
        # print(f'[page_fornito - {datetime.datetime.now()}] annotazioni open ({ts_end - ts_start} sec)')

        # Annotations 1
        # ts_start = datetime.datetime.now()
        self._av2000.send_line('1')
        time.sleep(0.1)
        data['annotazioni']['generiche'] = '\n'.join(map(
            lambda line: line.strip(),
            self._av2000.display_lines[9:32]
        )).strip()
        # ts_end = datetime.datetime.now()
        # print(f'[page_fornito - {datetime.datetime.now()}] annotazioni open - generiche ({ts_end - ts_start} sec)')

        # ts_start = datetime.datetime.now()
        self._av2000.send_seq(keys.END)
        time.sleep(0.1)
        # ts_end = datetime.datetime.now()
        # print(f'[page_fornito - {datetime.datetime.now()}] back ({ts_end - ts_start} sec)')

        # Annotations 2
        # ts_start = datetime.datetime.now()
        self._av2000.send_line('2')
        time.sleep(0.1)
        data['annotazioni']['iso'] = '\n'.join(map(
            lambda line: line.strip(),
            self._av2000.display_lines[9:32]
        )).strip()
        # ts_end = datetime.datetime.now()
        # print(f'[page_fornito - {datetime.datetime.now()}] annotazioni open - ISO ({ts_end - ts_start} sec)')

        # ts_start = datetime.datetime.now()
        self._av2000.send_seq(keys.END)
        time.sleep(0.1)
        # ts_end = datetime.datetime.now()
        # print(f'[page_fornito - {datetime.datetime.now()}] back ({ts_end - ts_start} sec)')

        # Back to main partner page
        # ts_start = datetime.datetime.now()
        self._av2000.send_seq(keys.END)
        time.sleep(0.1)
        # ts_end = datetime.datetime.now()
        # print(f'[page_fornito - {datetime.datetime.now()}] annotazioni close ({ts_end - ts_start} sec)')

        # Return extracted data
        return data
    # end get_data

    def commit_changes(self):
        super().commit_changes()

        time.sleep(0.1)

        # Manage possible errors
        if self._av2000.display_lines[-3].startswith('MSG0239 Partita IVA gia\' usata per'):
            self._av2000.send_seq('\n')

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
