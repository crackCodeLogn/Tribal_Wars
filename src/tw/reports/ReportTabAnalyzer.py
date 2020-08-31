"""
@author Vivek
@since 31/08/20
"""
from bs4 import BeautifulSoup

from src.tw.reports.core.ColorCode import ColorCode
from src.tw.reports.core.TargetNode import TargetNode


class ReportTabAnalyzer:

    def __init__(self):
        pass

    def analyze_op(self, page_html):
        data = BeautifulSoup(page_html, 'html.parser')
        unread_reps = data.find("table", {"id": "report_list"})

        for report in unread_reps.find_all("tr"):
            color_code = self.__fetch_color(report)
            if not color_code: continue
            target_x, target_y = self.__fetch_target_x_y(report)
            report_link = self.__fetch_report_link(report)

            print(report)
            node = TargetNode(color_code, target_x, target_y, report_link)
            print(node)
            print(node.get_url())

    def __fetch_color(self, report):
        tooltips = report.find_all("img", {"class": "tooltip"})
        for tip in tooltips:
            try:
                if 'dots' in tip['src']:
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
            return report.find("a", {"class": "report-link"})['href'].strip()
        except Exception as e:
            print("Error while fetching target report link: {}. Err: {}".format(report, e))
        return ""


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
    page_html = open('tw/reports/res/TW_REPORT_PAGE.html', 'r').read()

    report_tab = ReportTabAnalyzer()
    report_tab.analyze_op(page_html)
