from multiprocessing import Process
from typing import List


class LoadingTimeout(Exception):
    
    def __init__(self, message: str,  av2000_driver=None, navigator=None):
        
        super().__init__(message)
        
        self._av2000 = av2000_driver
        self._navigator = navigator
    # end __init__
    
    @property
    def av2000_driver(self):
        return self._av2000
    # end av2000
    
    @property
    def navigator(self):
        return self._navigator
    # end navigator
    
# end LoadingTimeout


class DriverClosed(Exception):
    pass
# end DriverClosed


class DownloadFailed(Exception):
    pass
# end DownloadFailed


class TaskError(Exception):
    
    def __init__(self, procs: List[Process]):
        super().__init__()
        self._procs = procs
    # end __init__
    
    @property
    def procs(self):
        return self._procs
    # end procs
    
# end TaskError


class NoPreviousPage(Exception):
    pass
# end NoPreviousPage


class NoNextPage(Exception):
    pass
# end NoNextPage
