ESC = '\x1b'

# Generate CTRL sequences indexed by letter (both uppercase and lowercase ==> case insensitive)
CTRL = dict(
    **{chr(ord('A') + x): ESC + chr(1 + x) for x in range(0, 26)},
    **{chr(ord('a') + x): ESC + chr(1 + x) for x in range(0, 26)},
)

F = {
     0: ESC + '[10~',
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
}
