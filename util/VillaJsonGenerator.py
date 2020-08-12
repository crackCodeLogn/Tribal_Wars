"""
@author Vivek
@since 12/08/20
"""
villa_template = """        ^
            "x": {xc},
            "y": {yc},
            "name": "Barb",
            "points": {pts},
            "units": [0,0,0,1,11,0,0,0]
        $,"""

fp_input = input("Enter the file path containing the co-ordinates: ")

with open(fp_input, 'r') as file:
    for line in file.readlines():
        spl = line.strip().split('|')
        x, y, pts = spl[0], spl[1], -1
        print(villa_template.format(xc=x, yc=y, pts=pts)
              .replace('^', '{')
              .replace('$', '}'))
