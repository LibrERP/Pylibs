import abc
from collections import namedtuple
import time
import typing

from av2000_terminator.misc import keys
from av2000_terminator.driver import AV2000Driver


MenuItem = namedtuple('MenuItem', ['descr', 'page_class'])


class AbstractPage(abc.ABC):
    
    _MENU_ITEMS: typing.Dict[str, MenuItem] = dict()
    
    def __init__(self, navigator: 'Navigator'):
        self._navigator: 'Navigator' = navigator
        self._av2000: AV2000Driver = navigator.driver
    # end __init__
    
    @property
    def company(self):
        """
        Return a dictionary with the name and the id of the selected company
        """
        data = self._av2000.display_lines[1]
        return {
            'name': data[2:].strip(),
            'id': data[:2].strip(),
        }
    # end company_name
    
    @property
    def name(self):
        """
        Returns the name of the current page
        """
        return self._av2000.display_lines[0][11:-28].strip()
    # end name
    
    @abc.abstractmethod
    def ready(self):
        """
        True if the server has sent all relevant data for the page
        """
        pass
    # end ready
    
    @property
    def menu(self):
        return {
            k: v.descr for k, v in self._MENU_ITEMS.items()
        }
    # end menu
    
    def menu_select(self, item_num: typing.Union[str, int]):
        
        selection_int = int(item_num)
        
        if selection_int in self._MENU_ITEMS:
            page_class = self._MENU_ITEMS[selection_int].page_class
            selection_str = f'{selection_int:02d}'
            self._av2000.send_line(selection_str)
            self._navigator.set_current_page(page_class)
        else:
            raise ValueError(f'Item {item_num} not found in menu.')
        # end if
        
    # end menu_select
    
    def wait_loading(self, timeout_sec):
        """Wait for page to be completly loaded"""
        self._av2000.wait_ready(self.ready, timeout_sec)
    # end wait_loading
    
    def back(self):
        self._av2000.send_seq(keys.ESC)
    # end back
    
# end AbstractPage


class FakePage(AbstractPage):

    @property
    def name(self):
        return 'Fake page controller'

    # end name

    def ready(self):
        time.sleep(1)
        return True
    # end ready

# end FakePage
