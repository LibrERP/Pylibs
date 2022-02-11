from av2000_terminator.navigation.base import AbstractPage, MenuItem, FakePage
from . import ordini_clienti


class MainMenu(AbstractPage):

    PAGE_NAME = 'Gest.area magazzino/vendite/acquisti'

    _MENU_ITEMS = {
         1: MenuItem('Magazzino', FakePage),
         2: MenuItem('Registro vitivinicolo', FakePage),
         3: MenuItem('Produzione', FakePage),
         5: MenuItem('Registro Commercializzazione', FakePage),
         7: MenuItem('Registro Imbottigliamento', FakePage),
         9: MenuItem('Registro Dolcificazione', FakePage),
        10: MenuItem('Vuoti', FakePage),
        11: MenuItem('Gestione offerte', FakePage),
        12: MenuItem('Registro Accisa', FakePage),
        13: MenuItem('Telematizzazione accise', FakePage),
        15: MenuItem('Zuccheri', FakePage),
        16: MenuItem('Condizioni di vendita', FakePage),
        19: MenuItem('Contratti Clienti', FakePage),
        20: MenuItem('Ordini Clienti', ordini_clienti.MainMenu),
        21: MenuItem('Bolle Clienti', FakePage),
        22: MenuItem('Fatture vendita', FakePage),
        24: MenuItem('Provvigioni', FakePage),
        25: MenuItem('Statistiche', FakePage),
        26: MenuItem('Modello INTRA-STAT', FakePage),
        27: MenuItem('Tracciabilita\'', FakePage),
        28: MenuItem('Contratti Fornitori', FakePage),
        29: MenuItem('Ordini Fornitori', FakePage),
        30: MenuItem('Acquisti Fornitori', FakePage),
    }

    def ready(self):

        name_ok = self.name == self.PAGE_NAME
        menu_ok = self._av2000.display_lines[18].strip() == '16 Condizioni di vendita'

        return name_ok and menu_ok

    # end ready

# end MainMenu
