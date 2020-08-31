"""
@author Vivek
@since 31/08/20
"""
import json

from bs4 import BeautifulSoup

from src.tw.reports.core.ColorCode import ColorCode
from src.tw.reports.core.TargetNode import TargetNode


class AtomicReportAnalyzer:

    def __init__(self, color_code, target_node, driver=None, forced_page_source=''):
        self.color_code = color_code
        self.node = target_node
        self.driver = driver
        self.forced_page_source = forced_page_source if forced_page_source else driver.get_page_source()

    def fetch_scouted_resources(self):
        report = BeautifulSoup(self.forced_page_source, 'html.parser')
        try:
            scouted_res = report.find("table", {"id": "attack_spy_resources"}).find("td")
            """
            <td><span class="nowrap"><span class="icon header wood" title="Wood"> </span>170</span>
                <span class="nowrap"><span class="icon header stone" title="Clay"> </span>266</span>
                <span class="nowrap"><span class="icon header iron" title="Iron"> </span>195</span>
            </td>
            """
            # print(scouted_res)
            return self.__perform_refinement_resources(scouted_res)
        except Exception as e:
            print("Error while fetching resources for report: {}. Err: {}".format(report, e))
        return None, None, None

    def fetch_wall_level(self):
        report = BeautifulSoup(self.forced_page_source, 'html.parser')
        try:
            building_data = report.find("input", {"id": "attack_spy_building_data"})['value'].strip()
            building_data = json.loads(building_data)
            building_data = [Building(**building) for building in building_data]
            return [building.get_level() for building in building_data if building.get_name() == 'Wall'][0]
        except Exception as e:
            print("Error while fetching wall level for report. Err: {}".format(e))
        return None

    def __perform_refinement_resources(self, scouted_res):
        res = scouted_res.find_all("span", {"class": "nowrap"})
        local_map = {}
        local_map['Wood'], local_map['Clay'], local_map['Iron'] = None, None, None
        for row in res:
            # print(row)
            try:
                l1 = row.find("span")
                local_map[l1['title']] = row.text.strip()
            except Exception:
                pass
        return local_map['Wood'], local_map['Clay'], local_map['Iron']


class Building:

    def __init__(self, name, id, level, **kwargs):
        self.name = name
        self.id = id
        self.level = level

    def __repr__(self):
        return "{}: {}".format(self.name, self.level)

    def __eq__(self, other):
        if other is None and other == self: return False
        if isinstance(other, Building): return other.__repr__() == self.__repr__()
        return False

    def __hash__(self):
        return hash(self.__repr__())

    def get_name(self):
        return self.name

    def get_level(self):
        return self.level


if __name__ == '__main__':
    # page_html = open('tw/reports/res/TW_REPORT_ACTUAL_RES_GREEN.html', 'r').read()
    page_html = open('tw/reports/res/TW_REPORT_ACTUAL_RES_YELLOW.html', 'r').read()
    color = ColorCode.GREEN
    url = 'https://enp9.tribalwars.net/game.php?village=10546&screen=report&mode=attack&group_id=0&view=7607567'
    target = TargetNode(color, 556, 595, url)

    report = AtomicReportAnalyzer(color, target, forced_page_source=page_html)
    wood, clay, iron = report.fetch_scouted_resources()
    print("Wood:", wood)
    print("Clay:", clay)
    print("Iron:", iron)
    wall_lvl = report.fetch_wall_level()
    print("Wall:", wall_lvl)
