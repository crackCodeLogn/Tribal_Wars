"""
@author Vivek
@since 26/01/20
"""
import datetime
import json

import pytz
from deprecated import deprecated


def read_config_world_level(world, title='local_config', mode=''):
    src = "../en{}{}/{}.json".format(mode, world, title)
    return json.loads(open(src, 'r').read())


def read_json_obj_world_level(world, title='local_config', mode=''):
    src = "../en{}{}/{}.json".format(mode, world, title)
    return json.load(open(src, 'r'))


def read_config_world_level_with_actual_level(world, title='local_config'):
    src = "en{}/{}.json".format(world, title)
    return json.loads(open(src, 'r').read())


def read_generic_config(config, key):
    return config[key]


def write_json_obj_to_fileSystem(json_obj, world, title='local_config', mode=''):
    src = open("../en{}{}/{}.json".format(mode, world, title), 'w')
    json.dump(json_obj, src, indent=4)
    src.close()


def write_json_to_fileSystem(json_string, world, title='local_config', mode=''):
    src = open("../en{}{}/{}.json".format(mode, world, title), 'w')
    src.write(json_string)
    src.close()


def print_list(data):
    [print(val) for val in data]
    # print(str(data))


def get_current_time():
    return datetime.datetime.now(pytz.timezone('Asia/Kolkata'))


class Helper:
    """Generic Helper class for TW"""

    def __init__(self, config):
        self.config = config

    def extract_base_info(self, key):
        return self.config['base'][key]

    def extract_driver_info(self, browser):
        return self.extract_base_info('driver')[browser]

    @deprecated(reason="This key is not present in the config.json, rather in local_config.json")
    def extract_villa_info(self, key):
        return self.config['villa'][key]

    def extract_screen(self, screen):
        return self.config['screens'][screen]

    def extract_base_screen_url(self, mode, world, id):
        """Ending screen key to be passed by the final caller"""
        return str(self.extract_base_info('screen')).format(mode=mode, world=world, id=id, screen="{screen}")

    def extract_sso(self, key):
        return self.config['sso'][key]

    def extract_ckt_breakers(self):
        return self.config['ckt.breakers']
