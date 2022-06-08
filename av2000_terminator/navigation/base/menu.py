import abc
from collections import namedtuple
import typing

from . page import AbstractPage


MenuItem = namedtuple('MenuItem', ['descr', 'page_class'])


class AbstractMenu(AbstractPage, abc.ABC):

    _MENU_ITEMS: typing.Dict[int, MenuItem] = dict()

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
# end AbstractMenu
