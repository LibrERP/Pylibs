import typing


class Xtractor:
    
    def __init__(self, lines_list: typing.List[str]):
        self._lines = lines_list
    # end lines
    
    def x(self, line_num: int, index: typing.Union[typing.Tuple[int, int], int], to_type=str):
        
        line = self._lines[line_num]
        
        if isinstance(index, int):
            portion = line[index:]
        elif isinstance(index, (tuple, list)):
            if len(index) == 2:
                portion = line[index[0]:index[1]]
            else:
                raise ValueError('When "index" is a list/tuple it must be of length 2')
            # end if
        else:
            raise TypeError('Index must be str or a tuple/list with 2 elements')
        # end if
        
        portion_strip = portion.strip()
        
        if portion_strip:
            return to_type(portion_strip)
        else:
            return None
        # end if
    # end x
    
# end Xtractor
