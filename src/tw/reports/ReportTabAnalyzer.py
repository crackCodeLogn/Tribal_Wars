"""
@author Vivek
@since 31/08/20
"""
from bs4 import BeautifulSoup
from ordered_set import OrderedSet

from src.tw.reports.core.ColorCode import ColorCode
from src.tw.reports.core.TargetNode import TargetNode


class ReportTabAnalyzer:

    def __init__(self):
        self.data = {}  # will store dict of colorCode x targetNode
        self.__init_data()
        pass

    def __init_data(self):
        self.data[ColorCode.GREEN] = OrderedSet()
        self.data[ColorCode.YELLOW] = OrderedSet()
        self.data[ColorCode.RED] = OrderedSet()
        self.data[ColorCode.MISC] = OrderedSet()

    def analyze_op(self, page_html):
        data = BeautifulSoup(page_html, 'html.parser')
        unread_reps = data.find("table", {"id": "report_list"})

        for report in unread_reps.find_all("tr"):
            color_code = self.__fetch_color(report)
            if not color_code: continue
            target_x, target_y = self.__fetch_target_x_y(report)
            report_link = self.__fetch_report_link(report)

            # print(report)
            node = TargetNode(color_code, target_x, target_y, report_link)
            self.data[node.get_color()].add(node)
            # print(node)
            # print(node.get_url())

    def __fetch_color(self, report):
        tooltips = report.find_all("img", {"class": "tooltip"})
        for tip in tooltips:
            try:
                if 'dots' in tip['src']:
                    # <img src="https://dsen.innogamescdn.com/asset/1d2499b/graphic/dots/green.png" title="Complete victory" alt="" class="tooltip"/>
                    return converter_to_ColorCode(tip['src'][tip['src'].rindex('/') + 1:tip['src'].rindex('.')])
            except Exception as e:
                print("Error while fetching color for report: {}. Err: {}".format(report, e))
        return None

    def __fetch_target_x_y(self, report):
        raw_detail = report.find("span", {"class": "quickedit-label"})
        try:
            detail = raw_detail.text.strip()  # ### (Cusco (560|585) K55) attacks Barbarian Village (562|592) K55
            detail = detail[detail.rindex('(') + 1:detail.rindex(')')].split('|')
            return detail[0], detail[1]
        except Exception as e:
            print("Error while fetching target x and y: {}. Err: {}".format(detail, e))
        return -1, -1

    def __fetch_report_link(self, report):
        try:
            """
            <a href="/game.php?village=10546&amp;screen=report&amp;mode=attack&amp;group_id=0&amp;view=7739917" class="report-link" data-id="7739917">
            <span class="quickedit-label">### (Cusco (560|585) K55) attacks Barbarian Village (568|584) K55</span></a>
            """
            return report.find("a", {"class": "report-link"})['href'].strip()
        except Exception as e:
            print("Error while fetching target report link: {}. Err: {}".format(report, e))
        return ""

    def get_data(self):
        return self.data


def converter_to_ColorCode(color):
    code = ColorCode.MISC
    if color == 'green':
        code = ColorCode.GREEN
    elif color == 'yellow':
        code = ColorCode.YELLOW
    elif color == 'red':
        code = ColorCode.RED
    return code


if __name__ == '__main__':
    page_html = open('tw/reports/res/TW_REPORT_PAGE_1.html', 'r').read()

    reports_analyzer = ReportTabAnalyzer()
    reports_analyzer.analyze_op(page_html)
    data = reports_analyzer.get_data()
    for color in data:
        if data[color]:
            print(color)
            [print(node) for node in data[color]]
