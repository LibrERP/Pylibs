from av2000_terminator.tasks.base import AbstractWorker


class DestinationsConversionDownloader(AbstractWorker):
    
    TASK_NAME = 'LIDL destinations conversions downloader'
    
    def __init__(self, *args, **kwargs):
        
        # Call the superclass constructor
        super().__init__(*args, **kwargs)
        
        # Ensure max retry is 1 since this is
        # a non resumable task
        if self._max_retry != 1:
            raise ValueError(
                f'"max_retry" parameter must be set to 1 for {self.TASK_NAME} task'
            )
        # end if
    
    # end __init__

    def _task_loop(self):
        
        # Variables
        last_page_processed = False

        # Convinience aliases
        navigator = self._navigator

        # Open connection and load suppliers page
        navigator.menu_select(8)
        navigator.menu_select(20)
        navigator.menu_select(4)
        navigator.menu_select(3)
        
        while not last_page_processed:
            yield navigator.current_page.extract_data()
            last_page_processed = navigator.current_page.is_last_page()
            navigator.current_page.scroll_next()
        # end while
        
    # end _task_loop

# end SuppliersDownloadTask


class ProductsConversionDownloader(AbstractWorker):
    TASK_NAME = 'LIDL products conversions downloader'

    def __init__(self, *args, **kwargs):

        # Call the superclass constructor
        super().__init__(*args, **kwargs)

        # Ensure max retry is 1 since this is
        # a non resumable task
        if self._max_retry != 1:
            raise ValueError(
                f'"max_retry" parameter must be set to 1 for {self.TASK_NAME} task'
            )
        # end if

    # end __init__

    def _task_loop(self):

        # Variables
        last_page_processed = False

        # Convinience aliases
        navigator = self._navigator

        # Open connection and load suppliers page
        navigator.menu_select(8)
        navigator.menu_select(20)
        navigator.menu_select(4)
        navigator.menu_select(4)

        while not last_page_processed:
            yield navigator.current_page.extract_data()
            last_page_processed = navigator.current_page.is_last_page()
            navigator.current_page.scroll_next()
        # end while

    # end _task_loop

# end ProductsConversionDownloader
