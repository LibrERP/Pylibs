from . base import AbstractPage
from . main_menu import MainMenu


class SelectCompany(AbstractPage):
    
    PAGE_NAME = 'Codice azienda'
    
    @property
    def company(self):
        """
        Return a dictionary with the name and the id of the selected company
        """
        return None
    # end company_name
    
    @property
    def name(self):
        return self._av2000.display_lines[11].strip()
    # end name
    
    def ready(self):
        return self.name == self.PAGE_NAME
    # end ready
    
    def set_company(self, company_id: int):
        if not isinstance(company_id, int):
            return TypeError('Only integers values between 1 (included) and 99 (included) are accepter')
        
        if not 1 <= company_id <= 99:
            return ValueError('Only integers values between 1 (included) and 99 (included) are accepter')
        
        if company_id != 99:
            return RuntimeError('For safety reasons only company id 99 is accepted')
        

    # end set_company
    
# end SelectCompany
