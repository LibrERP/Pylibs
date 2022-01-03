from .base import AbstractPage, MenuItem
from .fake import FakePage
from . import ordini_lidl


class MainMenu(AbstractPage):

    PAGE_NAME = 'Ordini Clienti'

    _MENU_ITEMS = {
        1: MenuItem('Causali ordini Clienti', FakePage),
        3: MenuItem('Import ordini da EDI', FakePage),
        4: MenuItem('Import ordini da xls Lidl', ordini_lidl.MainMenu),
        6: MenuItem('Import ordini da EDI nuovo', FakePage),
        9: MenuItem('Manutenzione ordini Clienti', FakePage),
        14: MenuItem('Ordini di carico Terrossa', FakePage),
        16: MenuItem('Ordini di carico S.Bonifacio (WISE)', FakePage),
        17: MenuItem('St. ordini x cliente/articolo', FakePage),
        18: MenuItem('St. ordini x cliente/data consegna', FakePage),
        19: MenuItem('St. ordini x articolo/data consegna', FakePage),
        21: MenuItem('St. riepilogo ordini x articolo', FakePage),
        22: MenuItem('Stampa ordini con relative bolle', FakePage),
        24: MenuItem('Situazione bancali ordinati x lotto', FakePage),
        29: MenuItem('Imputazione rapida lotti ordini', FakePage),
        30: MenuItem('Stampa ordine di carico', FakePage),
    }

    def ready(self):

        name_ok = self.name == self.PAGE_NAME
        menu_ok = self._av2000.display_lines[18].strip() == '16 Ordini di carico S.Bonifacio (WISE)'

        return name_ok and menu_ok

    # end ready

# end MainMenu
