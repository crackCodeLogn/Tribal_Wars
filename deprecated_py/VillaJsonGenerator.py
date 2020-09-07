"""
@author Vivek
@since 12/08/20
"""

from tw.Template import villa_template

fp_input = input("Enter the file path containing the co-ordinates: ")
with open(fp_input, 'r') as file:
    for line in file.readlines():
        spl = line.strip().split('|')
        x, y = spl[0], spl[1]
        pts, axe, lcav = -1, 0, 11
        print(villa_template
              .format(x=x, y=y, pts=pts, axe=0, lcav=11)
              .replace('^', '{')
              .replace('$', '}'))
