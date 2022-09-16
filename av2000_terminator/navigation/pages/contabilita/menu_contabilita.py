from av2000_terminator.navigation.base import AbstractPage, AbstractMenu, MenuItem, FakePage
from . anagrafiche import AnagraficaClienti, AnagraficaFornitori
from . anagrafiche.progressivi_base import ProgressiviBase


class MainMenu(AbstractMenu):
    
    PAGE_NAME = 'Archivi di base area contabile'
    
    _MENU_ITEMS = {
        1: MenuItem("Parametri area contabile", FakePage),
        2: MenuItem("Tabelle area contabile", FakePage),
        3: MenuItem("Progressivi base contabilita'", ProgressiviBase),
        4: MenuItem("Piano dei conti", FakePage),
        6: MenuItem("Anagrafica clienti", AnagraficaClienti),
        7: MenuItem("Flags      clienti", FakePage),
        9: MenuItem("Anagrafica fornitori", AnagraficaFornitori),
        11: MenuItem("Prog.IVA Cli,Fornit,Confer.", FakePage),
        13: MenuItem("Gestione dic. d'intento clienti", FakePage),
        17: MenuItem("Stampe parametri area contabile", FakePage),
        18: MenuItem("Stampe tabelle area contabile", FakePage),
        20: MenuItem("Stampa Piano Conti", FakePage),
        22: MenuItem("Stampa anagrafica clienti", FakePage),
        23: MenuItem("Stampa circolari/etichette clienti", FakePage),
        24: MenuItem("Stampa annotazioni clienti", FakePage),
        25: MenuItem("Stampa anagrafica fornitori", FakePage),
        26: MenuItem("Stampa circolari/etichette fornitori", FakePage),
        27: MenuItem("Stampa annotazioni fornitori", FakePage),
        28: MenuItem("Stampa annotazioni ISO fornitori", FakePage),
        32: MenuItem("Utilita' base contabile", FakePage),
    }
    
    @property
    def name(self):
        """Returns the name of the current page"""
        return self._av2000.display_lines[0][10:].strip()
    # end name
    
    def ready(self):
        name_ok = self.name == self.PAGE_NAME
        menu_ok = self._av2000.display_lines[18].strip() == "32 Utilita' base contabile"
        
        return name_ok and menu_ok
    # end ready
    
# end ContabilitaArchiviBase
