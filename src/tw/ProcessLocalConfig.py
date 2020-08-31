"""
@author Vivek
@since 16/08/20
"""

import enum
import os

from jinja2 import Template
from ordered_set import OrderedSet

from src.core.Villa import FarmVilla as Villa
from src.tw.Template import local_config_template
from src.util.Helper import read_json_obj_world_level, write_json_to_fileSystem, get_current_time


class WorkerProcessor:

    def __init__(self, base_working_dir, world, mode='', title='local_config', logging_debug=False):
        self.base_working_dir = base_working_dir
        self.json_src = read_json_obj_world_level(base_working_dir, world, mode=mode, title=title)
        self.world = world
        self.mode = mode
        self.title = title
        self.logging_debug = logging_debug

        print("Invoking worker processor for world {} and mode {} for json src '{}'".format(self.world, self.mode, self.title))

    def __compute(self, requisite_barbs, op_mode):
        barbs_set_base = OrderedSet()
        [barbs_set_base.add(Villa(**villa)) for villa in self.json_src['farming']]
        print("Barbs set base populated with {} records".format(len(barbs_set_base)))
        state, pre_size = "", len(barbs_set_base)
        if op_mode == OpMode.INCR:
            [barbs_set_base.add(barb) for barb in requisite_barbs]
            state = "increased"
        elif op_mode == OpMode.DECR:
            [barbs_set_base.remove(barb) for barb in requisite_barbs if barb in barbs_set_base]
            state = "reduced"
        print("Barbs set base {} to {} records".format(state, len(barbs_set_base)))
        return barbs_set_base, len(barbs_set_base) - pre_size

    def __generate_local_config_post_compute(self, barbs_set_base):
        _templ = Template(local_config_template)
        self.json_src['villa']['last_updated'] = get_current_time()
        jsonFromJinjaTempl = _templ.render(self.json_src, base=self.json_src['villa'], villas=barbs_set_base, villa_count=len(barbs_set_base))
        if self.logging_debug: print(jsonFromJinjaTempl)
        return jsonFromJinjaTempl

    def __write_new_local_config(self, jsonFromJinjaTempl):
        try:
            write_json_to_fileSystem(jsonFromJinjaTempl, self.base_working_dir, world=self.world, mode=self.mode, title=self.title)
            print("WRITE COMPLETE!")
        except Exception as e:
            print("Failed to WRITE the new local config. Err: ", e)

    def __orchestrator(self, new_barbs, op_mode):
        barbs_set_base, delta = self.__compute(new_barbs, op_mode)
        jsonFromJinjaTempl = self.__generate_local_config_post_compute(barbs_set_base)
        self.__write_new_local_config(jsonFromJinjaTempl)
        return delta

    def orchestrate_addition(self, new_barbs):
        return self.__orchestrator(new_barbs, OpMode.INCR)

    def orchestrate_removal(self, trash_barbs):
        return self.__orchestrator(trash_barbs, OpMode.DECR)


class OpMode(enum.Enum):
    INCR = 1
    DECR = 2


if __name__ == '__main__':
    world = 9
    mode = 'p'
    title = 'local_config_2'
    base_working_dir = os.path.dirname(os.path.realpath(__file__)) + '/../'

    process = WorkerProcessor(base_working_dir, world, mode=mode, title=title)

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

    process.orchestrate_removal(trash_barbs)
