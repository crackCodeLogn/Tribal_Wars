"""
@author Vivek
@since 13/03/20
"""
import requests

from Helper import read_config_world_level_with_actual_level
from core.Villa import FarmVilla as Villa

url = "https://www.twstats.com/en112/index.php?page=rankings&mode=villages&x={x}&y={y}"

# 8-directional - NOT USED ANYMORE
x_rotate = [1, +1, 0, -1, -1, -1, 0, 1]
y_rotate = [0, -1, -1, -1, 0, +1, 1, 1]

central_x = 525
central_y = 526

skimmed_barbs = []
already_visited_coords = set()
counter = 0


def read_in_villas_to_be_farmed(config):
    raw_farm_villas_list = config['farming']
    raw_farm_villas_list = [Villa(**villa) for villa in raw_farm_villas_list]
    return _filter_villas_to_farm(raw_farm_villas_list)


def _filter_villas_to_farm(raw_farm_villas_list):
    return set([villa for villa in raw_farm_villas_list if not villa.is_ignored()])


def operate_on_coord(x, y):
    url_to_hit = url.format(x=x, y=y)
    co_ord = "{}|{}".format(x, y)
    if co_ord in already_visited_coords:
        # print('Hitting already read-in co-ord: ' + co_ord)
        return
    already_visited_coords.add(co_ord)
    global counter
    counter += 1
    print("{}. {} => {}".format(counter, co_ord, url_to_hit))
    req = requests.get(url_to_hit)
    if "Barbarian" in req.text:
        print("This is a Barbarian villa!!")
        skimmed_barbs.append(Villa(x, y))


def mine_out_the_coords_to_visit(radius):
    print("Going for radius:: {}".format(radius))
    x_base = central_x - radius
    y_base = central_y + radius

    """Goes from west to east (Top border)"""
    y = y_base
    [operate_on_coord(x, y) for x in range(x_base, x_base + radius * 2 + 1)]

    """Goes from north to south (Left border)"""
    x = x_base
    [operate_on_coord(x, y) for y in range(y_base, y_base - radius * 2 - 1, -1)]

    x_base = central_x + radius
    y_base = central_y - radius

    """Goes from south to north (Right border)"""
    x = x_base
    [operate_on_coord(x, y) for y in range(y_base, y_base + radius * 2 + 1)]

    """Goes from east to west (Bottom border)"""
    y = y_base
    [operate_on_coord(x, y) for x in range(x_base, x_base - radius * 2 - 1, -1)]


if __name__ == '__main__':
    world = 112
    max_distance = 10  # fields

    [mine_out_the_coords_to_visit(radius) for radius in range(1, max_distance + 1)]

    config_villas = read_in_villas_to_be_farmed(read_config_world_level_with_actual_level(world))
    config_villas = set(config_villas)

    print("\nPrinting out the barbs until the max distance:-")
    counter = 1
    for villa in skimmed_barbs:
        print("{}. {}".format(counter, villa))
        counter += 1

    barbs = skimmed_barbs
    print('Number of villas in barb list before comparing with config : ' + str(len(barbs)))
    [barbs.remove(villa) for villa in config_villas if villa in barbs]
    # print('Found {} in existing attack list'.format(villa))
    print('Number of villas in barb list after comparing with config : ' + str(len(barbs)))
    [print(barb) for barb in barbs]
    if barbs:
        print('Creating as-is config to be added in config.json:-')
        data = """
^
  "x": {x},
  "y": {y},
  "name": "Barb",
  "points": {pts},
  "units": [0,0,0,1,5,0,0,0]
$"""
        final_list = ",\n\t".join([data.format(x=villa.get_x(), y=villa.get_y(), pts=villa.get_points()).replace('^', '{').replace('$', '}') for villa in barbs])
        print("The final list of barbs to be added:-")
        print("\n\t" + final_list)
    else:
        print('Discovered no new barbs in the tool!')

'''
# DISCARDED APPROACH
for radius in range(1, 2):
    print("Going for radius:: {}".format(radius))
    for i in range(0, len(x_rotate)):
        x = central_x + x_rotate[i] * radius
        y = central_y + y_rotate[i] * radius
        url_to_hit = url.format(x=x, y=y)

        print("Hitting info for {}|{} => {}".format(x, y, url_to_hit))
        req = requests.get(url_to_hit)
        if "Barbarian" in req.text:
            print("This is a Barbarian villa!!")
'''
