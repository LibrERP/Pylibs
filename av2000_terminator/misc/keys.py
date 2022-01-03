ESC = '\x1b'
HOME = ESC + '[1~'
END = ESC + '[4~'
PG_UP = ESC + '[5~'
PG_DN = ESC + '[6~'

ARROW = {
    'up': ESC + '[A',
    'down': ESC + '[B',
    'right': ESC + '[C',
    'left': ESC + '[D',
}


# Generate CTRL sequences indexed by letter (both uppercase and lowercase ==> case insensitive)
CTRL = dict(
    **{chr(ord('A') + x): ESC + chr(1 + x) for x in range(0, 26)},
    **{chr(ord('a') + x): ESC + chr(1 + x) for x in range(0, 26)},
)

# For F-keys sequences see
# https://invisible-island.net/xterm/xterm-function-keys.html
# "xterm-r6" column
F = {
     1: ESC + '[11~',
     2: ESC + '[12~',
     3: ESC + '[13~',
     4: ESC + '[14~',
     5: ESC + '[15~',
     6: ESC + '[17~',
     7: ESC + '[18~',
     8: ESC + '[19~',
     9: ESC + '[20~',
    10: ESC + '[21~',
    11: ESC + '[23~',
    12: ESC + '[24~',
    13: ESC + '[25~',
    14: ESC + '[26~',
    15: ESC + '[28~',
    16: ESC + '[29~',
    17: ESC + '[31~',
    18: ESC + '[32~',
    19: ESC + '[33~',
    20: ESC + '[34~',
}

SHIFT_F = {
     1: ESC + '[23~',
     2: ESC + '[24~',
     3: ESC + '[25~',
     4: ESC + '[26~',
     5: ESC + '[28~',
     6: ESC + '[29~',
     7: ESC + '[31~',
     8: ESC + '[32~',
     9: ESC + '[33~',
    10: ESC + '[34~',
}
