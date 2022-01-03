import pyte




class ASCIIStyler:
    
    COLOR_CODES = {
        'default': {'fg': '39', 'bg': '49'},
        'black': {'fg': '30', 'bg': '40'},
        'red': {'fg': '31', 'bg': '41'},
        'green': {'fg': '32', 'bg': '42'},
        'yellow': {'fg': '33', 'bg': '43'},
        'blue': {'fg': '34', 'bg': '44'},
        'magenta': {'fg': '35', 'bg': '45'},
        'cyan': {'fg': '36', 'bg': '46'},
        'light gray': {'fg': '37', 'bg': '47'},
        'dark gray': {'fg': '90', 'bg': '100'},
        'light red': {'fg': '91', 'bg': '101'},
        'light green': {'fg': '92', 'bg': '102'},
        'light yellow': {'fg': '93', 'bg': '103'},
        'light blue': {'fg': '94', 'bg': '104'},
        'light magenta': {'fg': '95', 'bg': '105'},
        'light cyan': {'fg': '96', 'bg': '106'},
        'white': {'fg': '97', 'bg': '107'},
    }
    
    def __init__(
        self,
        bold=False, italics=False, underscore=False, strikethrough=False, blink=False, reverse=False,
        fg='default', bg='default'
    ):
        self._bold = bold
        self._italics = italics
        self._underscore = underscore
        self._strikethrough = strikethrough
        self._blink = blink
        self._reverse = reverse
        self._fg = fg
        self._bg = bg
    # end __init__
    
    @property
    def bold(self):
        return self._bold
    # end bold
    
    @bold.setter
    def bold(self, value: bool):
        if type(value) != bool:
            raise TypeError()
        # end if
        
        self._bold = value
    # end bold_setter
    
    @property
    def italics(self):
        return self._italics
    # end italics
    
    @italics.setter
    def italics(self, value: bool):
        if type(value) != bool:
            raise TypeError()
        # end if
        
        self._italics = value
    # end italics_setter
    
    @property
    def underscore(self):
        return self._underscore
    # end underscore
    
    @underscore.setter
    def underscore(self, value: bool):
        if type(value) != bool:
            raise TypeError()
        # end if
        
        self._underscore = value
    # end underscore_setter
    
    @property
    def strikethrough(self):
        return self._strikethrough
    # end strikethrough
    
    @strikethrough.setter
    def strikethrough(self, value: bool):
        if type(value) != bool:
            raise TypeError()
        # end if
        
        self._strikethrough = value
    # end strikethrough_setter
    
    @property
    def blink(self):
        return self._blink
    # end blink
    
    @blink.setter
    def blink(self, value: bool):
        if type(value) != bool:
            raise TypeError()
        # end if
        
        self._blink = value
    # end blink_setter
    
    @property
    def reverse(self):
        return self._reverse
    # end reverse
    
    @reverse.setter
    def reverse(self, value: bool):
        if type(value) != bool:
            raise TypeError()
        # end if
        
        self._reverse = value
    # end reverse_setter
    
    @property
    def fg(self):
        return self._fg
    # end fg
    
    @fg.setter
    def fg(self, value: str):
        
        if value is None:
            self.fg = 'default'
        # end if
        
        if type(value) != str:
            raise TypeError()
        # end if
        
        if value not in self.COLOR_CODES:
            raise ValueError(f'Foreground color code not found ({value})')
        # end if
        
        self._fg = value
    # end fg_setter
    
    @property
    def bg(self):
        return self._bg
    # end bg
    
    @bg.setter
    def bg(self, value):
        
        if value is None:
            self.bg = 'default'
        # end if
        
        if type(value) != str:
            raise TypeError()
        # end if
        
        if value not in self.COLOR_CODES:
            raise ValueError(f'Background color code not found ({value})')
        # end if
        
        self._bg = value
    # end bg_setter
    
    def ascii_sequence(self):
        
        ascii_style = ['0']  # Initial command is "reset style"
    
        if self.bold:
            ascii_style.append('1')
        # end if

        if self.italics:
            ascii_style.append('3')
        # end if

        if self.underscore:
            ascii_style.append('4')
        # end if

        if self.blink:
            ascii_style.append('5')
        # end if

        if self.strikethrough:
            ascii_style.append('9')
        # end if

        if self.reverse:
            fg_code = self.COLOR_CODES[self.bg]['fg']
            bg_code = self.COLOR_CODES[self.fg]['bg']
        else:
            fg_code = self.COLOR_CODES[self.fg]['fg']
            bg_code = self.COLOR_CODES[self.bg]['bg']
        # end if

        ascii_style.append(fg_code)
        ascii_style.append(bg_code)
        
        return f'\x1b[{";".join(ascii_style)}m'
    # end ascii_sequence
    
    def update(self, c: pyte.screens.Char):
        self.bold = c.bold
        self.italics = c.italics
        self.underscore = c.underscore
        self.strikethrough = c.strikethrough
        self.reverse = c.reverse
        
        if c.fg and c.fg != 'default':
            self.fg = c.fg
        # end if
        
        if c.bg and c.bg != 'default':
            self.bg = c.bg
        # end if
    # end update
    
    def styled(self, c: pyte.screens.Char):
        self.update(c)
        data = c.data or ' '
        return self.ascii_sequence() + data
    # end update
    
    def styled_debug(self, c: pyte.screens.Char):
        self.update(c)
        data = c.data or ' '
        return (
            data,
            self.bold, self.italics, self.underscore, self.strikethrough,
            self.fg, self.bg, self.reverse,
        )
    # end update
    
    def reset(self):
        self.bold = False
        self.italics = False
        self.underscore = False
        self.strikethrough = False
        self.blink = False
        self.fg = 'default'
        self.bg = 'default'
    # end reset
    
# end ASCIIStyle
