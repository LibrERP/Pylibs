from av2000_terminator.misc import keys
from . base import AbstractPage, MenuItem
from . fake import FakePage
from . import contabilita
from . import magazzino_vendite_acquisti


class MainMenu(AbstractPage):
    
    PAGE_NAME = 'AV2000'
    
    _MENU_ITEMS = {
         1: MenuItem('Tabelle multiaziendali', FakePage),
         3: MenuItem('Archivi di base area contabile', contabilita.MainMenu),
         4: MenuItem('Gestione area contabile', FakePage),
         5: MenuItem('Gestione cespiti', FakePage),
         7: MenuItem('Archivi di base area magazzino', FakePage),
         8: MenuItem('Gest.area magazzino/vendite/acquisti', magazzino_vendite_acquisti.MainMenu),
        11: MenuItem('Export analisi redditivita\'', FakePage),
        18: MenuItem('Gestione area vendemmia', FakePage),
        19: MenuItem('Anomalie varie area vendemmia', FakePage),
        20: MenuItem('Import/Export dati vendemmia', FakePage),
        32: MenuItem('Utilita\'', FakePage),
    }
    
    def ready(self):
        name_ok = self.name == self.PAGE_NAME
        menu_ok = self._av2000.display_lines[18].strip() == '32 Utilita\''
        
        return name_ok and menu_ok
    # end ready
    
    def back(self):
        self._av2000.send_seq(keys.F[10])
    # end back
    
# end MainMenu
