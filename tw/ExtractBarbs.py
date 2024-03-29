"""
@author Vivek
@since 12/02/20
"""

import os
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from ordered_set import OrderedSet

from core.Villa import FarmVilla as Villa
from tw.ProcessLocalConfig import WorkerProcessor
from util.Helper import read_config_world_level


class _ExtractBarbsList:

    def __init__(self, link, max_distance=10):
        self.url = link
        self.max_distance = max_distance

        self.BARB = 'Barbarian village'
        self.BARB2 = 'Bonus village'
        self.FIRST_BRACE = '('
        self.BAR = '|'
        self.SECOND_BRACE = ')'

        self.ignored_barbs = set()

    def _parse_for_coords(self, line, barb_type):
        line = line[line.index(barb_type) + len(barb_type):]
        line = line[line.index(self.FIRST_BRACE) + 1: line.index(self.SECOND_BRACE)].strip()
        return line[:line.index(self.BAR)], line[line.index(self.BAR) + 1:]

    def _perform_extraction(self, barb_type, line):
        soup = BeautifulSoup(line, 'html.parser')
        rows = soup.findAll('tr')
        barbs = []
        for row in rows:
            cells = row.findAll('td')
            if len(cells) == 9:
                distance, points, x, y = 0, 0, 0, 0
                i = 0
                try:
                    for cell in cells:
                        data = cell.text.strip()
                        if i == 1:
                            distance = float(data)
                        elif i == 5:
                            x, y = self._parse_for_coords(data, barb_type)
                        elif i == 8:
                            points = int(str(data).replace(',', ''))
                        i += 1
                except Exception as e:
                    print('Encountered exception  :' + str(e))
                villa = Villa(x, y, points=points, distance=distance)
                if distance <= self.max_distance:
                    if villa.get_points() > 500: villa.set_ignore(True)
                    barbs.append(villa)
                else:
                    print("Ignoring {} as distance {} > {}".format(villa, distance, self.max_distance))
            else:
                print('TW changed the order of showing barbs... Cannot proceed with info extraction')
        return barbs

    def extract_barbs_from_site(self):
        print("Hitting : " + self.url)
        req = requests.get(self.url)
        lines = req.text.split('\n')
        barbs = set()
        for line in lines:  # iterate over the entire webpage to extract the barb lines
            barb_type = None
            if self.BARB in line: barb_type = self.BARB
            if self.BARB2 in line: barb_type = self.BARB2
            if barb_type:
                obtained = self._perform_extraction(barb_type, line)
                [barbs.add(barb) for barb in obtained]

        return barbs

    def read_in_villas_to_be_farmed(self, config):
        raw_farm_villas_list = config['farming']
        raw_farm_villas_list = [Villa(**villa) for villa in raw_farm_villas_list]
        return self._filter_villas_to_farm(raw_farm_villas_list)

    def _filter_villas_to_farm(self, raw_farm_villas_list):
        targets = set()
        for villa in raw_farm_villas_list:
            if not villa.is_ignored():
                targets.add(villa)
            else:
                self.ignored_barbs.add(villa)
        return targets

    def get_ignored_barbs(self):
        return self.ignored_barbs


def generate_link_twstats_barbs_list(code, world, x, y):
    """Generates the link to the twstats page which provides a list of all the barbs in the 12-15 fields radius"""
    return 'https://www.twstats.com/en{}{}/index.php?page=village_locator&stage=4&source=player&village_coords={}|{}&searchstring=vivekthewarrior&tribe_id=0&filter=abandoned'.format(code, world, x, y)


class BarbsManager:

    def __init__(self, base_working_dir, mode, world, x, y, max_distance):
        self.base_working_dir = base_working_dir
        self.mode = mode
        self.world = world
        self.x = x
        self.y = y
        self.max_distance = max_distance

        print("Invoking New barb extractor!")

    def orchestrator(self, verbose=False):
        link = generate_link_twstats_barbs_list(self.mode, self.world, self.x, self.y)
        barb_lister = _ExtractBarbsList(link, max_distance=self.max_distance)
        barbs = barb_lister.extract_barbs_from_site()
        if verbose: [print(barb) for barb in barbs]

        config_villas = barb_lister.read_in_villas_to_be_farmed(read_config_world_level(self.base_working_dir, self.world, mode=self.mode))
        config_villas = OrderedSet(config_villas)
        if verbose: [print(barb) for barb in config_villas]

        print('Number of villas in barb list from site before comparing with config : ' + str(len(barbs)))
        [barbs.remove(villa) for villa in config_villas if villa in barbs]
        barbs = barbs.difference(barb_lister.get_ignored_barbs())  # removing barbs which have already been set to ignore mode in config list
        # print('Found {} in existing attack list'.format(villa))
        print('Number of new villas in site barb list after comparing with config : ' + str(len(barbs)))
        [print(barb) for barb in barbs]
        base_villa = Villa(x=self.x, y=self.y)
        if barbs:
            print('Creating as-is config to be added in config.json:-')
            print("Base villa: " + str(base_villa))
            for villa in barbs:
                distance = base_villa.get_distance_from_another_villa(villa)
                axe, lcav, scouts = 0, 11, 1
                if distance <= 5 or villa.get_points() <= 100: axe, lcav = 101, 5
                villa.set_axes(axe)
                villa.set_lcav(lcav)
                villa.set_scouts(scouts)
                villa.set_name("Barb")
            print("The new list of barbs:-")
            pprint(barbs)
            worker = WorkerProcessor(self.base_working_dir, self.world, self.mode)
            delta = worker.orchestrate_addition(barbs)
            return delta
        else:
            print('Discovered no new barbs in the tool!')
        return 0


if __name__ == '__main__':
    mode = 'p'  # blank=normal, 'p'=casual, 'c'=classic
    world = 12
    x, y = 520, 434
    max_distance = 35
    base_working_dir = os.path.dirname(os.path.realpath(__file__)) + '/../'

    orch = BarbsManager(base_working_dir, mode, world, x, y, max_distance)
    orch.orchestrator()
