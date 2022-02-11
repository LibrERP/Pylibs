import re

from av2000_terminator.misc import keys, Xtractor
from av2000_terminator.navigation.base import AbstractPage

from . partner import PartnersListPage, PartnersMainPage


# - - - - - - - - - - - - - -
# Clienti
# - - - - - - - - - - - - - -
class ListaClienti(PartnersListPage):
    pass
# end ListaClienti


class DettagliClienti(AbstractPage):

    PAGE_NAME = 'Anagrafica clienti'
    _LAST_DATA_LINE_RE = re.compile(r'^\s*Sconto a litro .*Provvigioni .*Sc\.tot\.bolla S/N .\s*')
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
        data = {
            'codice': xt.x(3, (6, 14)),
            'ragione_sociale': xt.x(3, 30),
            'ragione_sociale_agg': xt.x(4, 30),
            'indirizzo': xt.x(5, 23),
            'cap': xt.x(6, (30, 36)),
            'localita': xt.x(6, (37, 77)),
            'provincia': xt.x(6, (78, 80)),
            'piano_conti': {
                'l1': xt.x(7, (30, 34), int),
                'l2': xt.x(7, (35, 39), int),
                'nome': xt.x(7, 40),
            },
            'attributi': {
                'tip': xt.x(9, (10, 13), int),
                'pro': xt.x(9, (14, 17), int),
                'int': xt.x(9, (18, 21)),
            },
            'stato_giuridico': xt.x(10, (16, 17)),
            'nascita': {
                'sesso': xt.x(10, (23, 26)),
                'data': xt.x(10, (38, 50)),
                'comune': xt.x(10, (56, 65)),
                'provincia': xt.x(10, 74),
            },
            'cognome': xt.x(11, (8, 28)),
            'nome': xt.x(11, (36, 56)),
            'associazione': xt.x(11, (75, 76)),
            'partita_iva': xt.x(12, (6, 22)),
            'codice_fiscale': xt.x(12, (39, 55)),
            'registro_imprese': xt.x(12, (67, 78)),
            'fatturazione_elettronica': {
                'destinazione': xt.x(13, (22, 29)),
                'ipa': xt.x(13, (34, 40)),
                'cig': xt.x(13, (45, 60)),
                'cup': xt.x(13, (65, 80)),
            },
            'comune': {
                'cod': xt.x(14, (34, 40), int),
                'nome': xt.x(14, (41, 76)),
            },
            'regione': {
                'cod': xt.x(15, (34, 36), int),
                'nome': xt.x(15, 37),
            },
            'nazione': {
                'cod': xt.x(16, (34, 37), int),
                'nome': xt.x(16, 38),
            },
            'lingua': {
                'cod': xt.x(17, (34, 37), int),
                'nome': xt.x(17, 38),
            },
            'pagamento': {
                'split_payment': xt.x(18, (76, 77)),
                'iban_banca': xt.x(19, (17, 49)),
            },
            'agente': {
                'cod': xt.x(20, (20, 25)),
                'nome': xt.x(20, 27),
            },
            'listino': {
                'cod': xt.x(21, (20, 25)),
                'nome': xt.x(21, 27),
            },
            'trasportatore': {
                'cod': xt.x(22, (20, 25)),
                'nome': xt.x(22, 27),
            },
            'codice_iva': {
                'cod': xt.x(24, (20, 24)),
                'nome': xt.x(24, 27),
            },
            'porto': {
                'cod': xt.x(25, (20, 24)),
                'nome': xt.x(25, 27),
            },
            'giorno_chiusura': {
                'cod': xt.x(26, (20, 24)),
                'nome': xt.x(26, 27),
            },
            'zona_consegna_merce': {
                'cod': xt.x(28, (20, 24)),
                'nome': xt.x(28, 27),
            },
            'banca_interna_prev': {
                'cod': xt.x(29, (20, 24)),
                'nome': xt.x(29, 27),
            },
            'obsoleto': xt.x(30, (20, 21)),
            'sconto_commerciale': [
                xt.x(31, (20 + (ix * 6), 20 + (ix * 6) + 5))
                for ix in range(4)
            ],
            'sconto_merce': xt.x(31, (75, 76)),
            'sconto_a_litro': xt.x(32, (20, 26)),
            'provvigioni': [
                xt.x(32, (39 + (ix * 6), 39 + (ix * 6) + 5))
                for ix in range(2)
            ],
            'sconto_totale_bolla': xt.x(32, (75, 76)),
        }

        # Other data - 1
        self._av2000.send_seq(keys.F[9])
        self._av2000.wait_ready(self._ready_other_1, timeout_sec=2)

        data_other_1 = {}

        # TODO: EXTRACT DATA FOR "Other data - 1"

        # Other data - 2
        self._av2000.send_seq(keys.PG_DN)
        self._av2000.wait_ready(self._ready_other_2, timeout_sec=2)

        data_other_1 = {}

        # TODO: EXTRACT DATA FOR "Other data - 1"

        # Other data - 3
        self._av2000.send_seq(keys.PG_DN)
        self._av2000.wait_ready(self._ready_other_3, timeout_sec=2)

        data_other_1 = {}

        # TODO: EXTRACT DATA FOR "Other data - 3"

        # Back to main detail page
        self._av2000.send_seq('\n')
        self._av2000.wait_ready(self.ready, timeout_sec=2)

        # Return extracted data
        return data

    # end get_data
# end DettagliClienti


class AnagraficaClienti(PartnersMainPage):
    
    PAGE_NAME = 'Anagrafica clienti'

    PARTNERS_LIST_PAGE = ListaClienti
    PARTNER_DETAILS_PAGE = DettagliClienti

    def _query_wizard_ready(self) -> bool:
        scrn = self._av2000.display_lines

        lls_query_ok = scrn[19][3:].strip().startswith(
            'Visualizza clienti obsoleti S/N'
        )
        lls_window_ok = scrn[38].startswith('Invio Fine')

        return lls_query_ok and lls_window_ok
    # end _query_ui_ready
# end AnagraficaClienti
