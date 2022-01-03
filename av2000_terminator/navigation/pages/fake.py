import time

from . base import AbstractPage

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
