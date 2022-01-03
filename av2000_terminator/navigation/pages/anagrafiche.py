import re
import time
import typing

from av2000_terminator.misc import keys, Xtractor
from av2000_terminator.misc.exceptions import LoadingTimeout, NoNextPage

from . base import AbstractPage


class ListaFornitori(AbstractPage):
    
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
        
        # NOTE: last page case deliberatly ignore!!
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

# end ListaFornitori


class DettagliFornitore(AbstractPage):
    
    PAGE_NAME = 'Anagrafica fornitori'
    _LAST_DATA_LINE_RE = re.compile(r'^\s*Cognome .*Nome .*% imp calcolo RA \s*')
    _LAST_SCREEN_LINE = 'F7   Invio  Esc  Fine   F3   Note  F6   Collegamenti'
    
    def ready(self):
        
        lines = self._av2000.display_lines
        
        last_data_line_ok = self._LAST_DATA_LINE_RE.match(lines[36])
        bottom_menu_ok = lines[38].strip() == self._LAST_SCREEN_LINE
        name_ok = self.name == self.PAGE_NAME
        
        return last_data_line_ok and bottom_menu_ok
    
    # end ready
    
    def back(self):
        self._av2000.send_seq(keys.END)
    # end back
    
    def get_data(self):
        
        xt = Xtractor(self._av2000.display_lines)
        
        # Extract data
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
                'cod': xt.x(15, (34, 40)),
                'descizione': xt.x(15, 40),
            },
            'iban': (
                xt.x(16,(31, 33)),
                xt.x(16,(35, 36)),
                xt.x(16,(37, 38)),
                xt.x(16,(39, 44)),
                xt.x(16,(45, 50)),
                xt.x(16,(51, 63))
            ),
            'banca': xt.x(16, 64),
            'iva_primaria': {
                'codice': xt.x(17, (34, 37)),
                'descrizione': xt.x(17, (38, 76)),
            },
            'iva_altro_1': {
                'codice': xt.x(17, (83, 86)),
                'descrizione': '',
            },
            'iva_altro_2': {
                'codice': xt.x(17, (88, 91)),
                'descrizione': '',
            },
            'comune': {
                'cod': xt.x(18, (34, 40), int),
                'nome': xt.x(18, (41, 76)),
            },
            'regione': {
                'cod': xt.x(19, (34, 36), int),
                'nome': xt.x(19, 37),
            },
            'nazione': {
                'cod': xt.x(20, (34, 37), int),
                'nome': xt.x(20, 38),
            },
            'comune_2018': {
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
            'controllo_soglia': xt.x(26, (51, 52)),
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
            'codice_ipa': xt.x(33, (25,32)),
            'sconti': [
                xt.x(35, (72 + (ix * 6), 72 + 5 + (ix * 6)))
                for ix in range(4)
                if xt.x(35, (72 + (ix * 6), 72 + 5 + (ix * 6)))
            ],
            'cognome': xt.x(36, (25, 45)),
            'cognome': xt.x(36, (51, 71)),
            'pct_imponibile_calcolo_ra': xt.x(36, (89, 95)),
        }
        
        # Return extracted data
        return data
    
    # end get_data
    
# end DettagliFornitore


class AnagraficaFornitori(AbstractPage):
    
    PAGE_NAME = 'Anagrafica fornitori'
    
    def show_supplier(self, supplier_id: typing.Union[int, str]):
        self._av2000.send_line(str(supplier_id))
        self._navigator.set_current_page(DettagliFornitore)
    # end show_supplier
    
    def open_suppliers_list(self):
        
        page_load_timeout = 3
        
        # Open query form
        self._av2000.send_seq(keys.SHIFT_F[1])
        self._av2000.wait_ready(self._query_ui_ready, page_load_timeout)
        
        # Include obsolete suppliers
        self._av2000.send_seq(keys.ARROW['down'])
        self._av2000.send_seq(keys.ARROW['down'])
        self._av2000.send_seq(keys.ARROW['down'])
        self._av2000.send_seq('S')
        
        self._av2000.send_line()
        
        self._navigator.set_current_page(ListaFornitori)
        
    # end open_suppliers_list
    
    def ready(self):
        
        text = self._av2000.text_lines
        last_line = text and text[-1] or ''
        
        name_ok = self.name == self.PAGE_NAME
        menu_ok = 'Codici in sequenza' in last_line
        
        return name_ok and menu_ok
    
    # end ready
    
    def _query_ui_ready(self) -> bool:
        scrn = self._av2000.display_lines
        
        lls_query_ok = scrn[19][3:].startswith(
            'Visualizza fornitore obsoleti (S/N)'
        )
        lls_window_ok = scrn[38].startswith('Invio Fine')
        
        return lls_query_ok and lls_window_ok
    # end _query_ui_ready
        
    
# end AnagraficaFornitori


class AnagraficaClienti(AbstractPage):
    
    PAGE_NAME = 'Anagrafica clienti'
    
# end AnagraficaClienti
