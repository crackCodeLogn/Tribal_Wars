"""
@author Vivek
@since 16/08/20
"""

from jinja2 import Template
from ordered_set import OrderedSet

from core.Villa import FarmVilla as Villa
from util.Helper import read_json_obj_world_level, write_json_obj_to_fileSystem
from util.Template import local_config_template


class JsonProcessor:

    def __init__(self, world, mode='', title='local_config'):
        self.json_src = read_json_obj_world_level(world, mode=mode, title=title)
        self.world = world
        self.mode = mode
        self.title = title

    def compute(self, trash_barbs):
        self.trash_barbs = trash_barbs
        barbs_set_base = OrderedSet()
        [barbs_set_base.add(Villa(**villa)) for villa in self.json_src['farming']]
        print("Barbs set base populated with {} records".format(len(barbs_set_base)))
        [barbs_set_base.remove(trash) for trash in trash_barbs]
        print("Barbs set base reduced to {} records".format(len(barbs_set_base)))

        templ = Template(local_config_template)
        output = templ.render(self.json_src, base=self.json_src['villa'], villas=barbs_set_base, villa_count=len(barbs_set_base))
        print(output)

        write_json_obj_to_fileSystem(self.json_src, world=self.world, mode=self.mode, title=self.title)


if __name__ == '__main__':
    world = 9
    mode = 'p'
    title = 'local_config_2'
    process = JsonProcessor(world, mode=mode, title=title)

    print("Initiating back-loading of farms.")
    input_list = []
    while True:
        inp = input()
        if not inp: break
        input_list.append(inp.strip())

    trash_barbs = []
    for line in input_list:
        spl = line[0:line.index('.')].split('|')
        x, y = spl[0], spl[1]
        trash_barbs.append(Villa(x, y))
    print("Trash barbs: ", trash_barbs)

    process.compute(trash_barbs)
