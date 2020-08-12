"""
@author Vivek
@since 12/02/20
"""

import requests
from bs4 import BeautifulSoup

from core.Villa import FarmVilla as Villa
from util.Helper import read_config_world_level, villa_template


class ExtractBarbsList:

    def __init__(self, link, max_distance=10):
        self.url = link
        self.max_distance = max_distance

        self.BARB = 'Barbarian village'
        self.BARB2 = 'Bonus village'
        self.FIRST_BRACE = '('
        self.BAR = '|'
        self.SECOND_BRACE = ')'

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
        return set([villa for villa in raw_farm_villas_list if not villa.is_ignored()])


def generate_link_twstats_barbs_list(code, world, x, y):
    """Generates the link to the twstats page which provides a list of all the barbs in the 12-15 fields radius"""
    return 'https://www.twstats.com/en{}{}/index.php?page=village_locator&stage=4&source=player&village_coords={}|{}&searchstring=vivekthewarrior&tribe_id=0&filter=abandoned'.format(code, world, x, y)


if __name__ == '__main__':
    mode = 'p'  # blank=normal, 'p'=casual, 'c'=classic
    world = 9
    x, y = 560, 585
    max_distance = 20

    link = generate_link_twstats_barbs_list(mode, world, x, y)
    barb_lister = ExtractBarbsList(link, max_distance=max_distance)
    barbs = barb_lister.extract_barbs_from_site()
    # [print(barb) for barb in barbs]

    config_villas = barb_lister.read_in_villas_to_be_farmed(read_config_world_level(world, mode=mode))
    config_villas = set(config_villas)
    # [print(barb) for barb in config_villas]

    print('Number of villas in barb list before comparing with config : ' + str(len(barbs)))
    [barbs.remove(villa) for villa in config_villas if villa in barbs]
    # print('Found {} in existing attack list'.format(villa))
    print('Number of villas in barb list after comparing with config : ' + str(len(barbs)))
    [print(barb) for barb in barbs]
    base_villa = Villa(x=x, y=y)
    if barbs:
        print('Creating as-is config to be added in config.json:-')
        print("Base villa: " + str(base_villa))
        final_list = []
        for villa in barbs:
            distance = base_villa.get_distance_from_another_villa(villa)
            axe, lcav = 0, 11
            if distance <= 5 or villa.get_points() <= 100: axe, lcav = 31, 4
            final_list.append(villa_template.format(x=villa.get_x(), y=villa.get_y(), pts=villa.get_points(), axe=axe, lcav=lcav)
                              .replace('^', '{')
                              .replace('$', '}'))
        print("The final list of barbs to be added:-")
        print("\n".join(final_list))
    else:
        print('Discovered no new barbs in the tool!')
