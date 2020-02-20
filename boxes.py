"""
First stab at table stuff in terminal.

This might be useful:

	- https://github.com/adobe-type-tools/box-drawing
	- http://www.tldp.org/HOWTO/NCURSES-Programming-HOWTO/
	- https://stackoverflow.com/a/58033954/9839539
"""

class box_chars:
    top_left = '\u250c'
    top_right = '\u2510'
    bottom_left = '\u2514'
    bottom_right = '\u2518'
    horizontal = '\u2500'
    vertical = '\u2502'
    vertical_break_left = '\u251c'
    vertical_break_right = '\u2524'
    horizontal_break_top = '\u252c'
    horizontal_break_bottom = '\u2534'
    cross = '\u253c'


print(box_chars.top_left + box_chars.horizontal +
      box_chars.horizontal_break_top + box_chars.horizontal +
      box_chars.top_right)
print(box_chars.vertical_break_left + box_chars.horizontal + box_chars.cross +
      box_chars.horizontal + box_chars.vertical_break_right)
print(box_chars.vertical + ' ' + box_chars.vertical + ' ' + box_chars.vertical)
print(box_chars.bottom_left + box_chars.horizontal +
      box_chars.horizontal_break_bottom + box_chars.horizontal +
      box_chars.bottom_right)
