import typing

from av2000_terminator.driver import AV2000Driver
from av2000_terminator.misc.exceptions import NoPreviousPage

from . pages import MainMenu


class Navigator:
    
    def __init__(self, av2000: AV2000Driver, page_load_timeout_sec: float = 5):
        
        # AV2000 instance used to initiate pages
        self._av2000 = av2000
        
        # Timeout for page loading
        self._timeout_sec = page_load_timeout_sec
        
        # Navigation history stack
        self._pages_breadcrumb = list()
        
        # Start from MainMenu page
        self.set_current_page(MainMenu)
        
    # end __init__
    
    @property
    def timeout_sec(self):
        return self._timeout_sec
    # end current_page
    
    @property
    def driver(self):
        return self._av2000
    # end current_page
    
    @property
    def current_page(self):
        return self._pages_breadcrumb[-1]
    # end current_page
    
    def set_current_page(self, page_class):
        page = page_class(self)
        self._pages_breadcrumb.append(page)
        page.wait_loading(self._timeout_sec)
    # end set_current_page
    
    def back(self):
        
        if len(self) > 1:
        
            # Remove current page and send the "back" sequence
            page_current = self._pages_breadcrumb.pop()
            page_current.back()
            
            # Wait for the new current page to be loaded
            page_prev = self._pages_breadcrumb[-1]
            page_prev.wait_loading(self._timeout_sec)
            
        else:
            raise NoPreviousPage(
                'Current page is Main Menu, cannot go back. '
                'Call the exit() method to close the connection.'
            )
        # end if
        
    # end page_back
    
    def back_to_main_menu(self):
        while len(self) > 1:
            self.back()
        # end while
        assert self.current_page.name == MainMenu.PAGE_NAME
    # end back_to_main_menu
    
    @property
    def menu(self):
        return self.current_page.menu
    # end menu
    
    def menu_select(self, item_num: typing.Union[str, int]):
        self.current_page.menu_select(item_num)
    # end menu_select
    
    def exit(self):
        self._av2000.exit()
    # end exit
    
    def __len__(self):
        return len(self._pages_breadcrumb)
    # end __len__
    
# end Navigator
