import abc
import time

from sshterminal import keys

from av2000_terminator.terminal import AV2000Terminal


class AbstractPage(abc.ABC):
    
    def __init__(self, navigator: 'Navigator'):
        self._navigator: 'Navigator' = navigator
        self._av2000: AV2000Terminal = navigator.driver
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
