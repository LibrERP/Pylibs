from av2000_terminator.navigation.base import AbstractPage


class ProgressiviBase(AbstractPage):

    PAGE_NAME = 'Progressivi base contabilita\''
    PAGE_LAST_LINE = 22
    LAST_LINE_CONTENT = 'Invio  Esc'

    PROG_CLIENT_LINE = 4
    PROG_CLIENT_COL = 36

    PROG_SUPPLIER_LINE = 6
    PROG_SUPPLIER_COL = 36

    def ready(self):
        # Check for main components of the page to be here
        name_ok = self.name == self.PAGE_NAME

        # Check if last line has been modified
        ll_modified = self.PAGE_LAST_LINE in self._av2000.modified_lines

        # Check last line content
        ll_content_ok = self.LAST_LINE_CONTENT == self._av2000.display_lines[self.PAGE_LAST_LINE].strip()

        # Return result
        return name_ok and ll_modified and ll_content_ok
    # end ready

    @property
    def max_client_id(self):
        line_content = self._av2000.display_lines[self.PROG_CLIENT_LINE]
        str_value = line_content[self.PROG_CLIENT_COL:].strip()
        return int(str_value)
    # end max_client_id

    @property
    def max_supplier_id(self):
        line_content = self._av2000.display_lines[self.PROG_SUPPLIER_LINE]
        str_value = line_content[self.PROG_SUPPLIER_COL:].strip()
        return int(str_value)
    # end max_supplier_id
# end ProgressiviBase
