"""
@author Vivek
@since 31/08/20
"""
from src.tw.reports.miner.ReportMiner import ReportTabsAnalyzer

if __name__ == '__main__':
    page_html = open('tw/reports/res/TW_REPORT_PAGE_1.html', 'r').read()

    reports_analyzer = ReportTabsAnalyzer()
    reports_analyzer.analyze_op(page_html)  # series of all tw report + attack page to go here

    data = reports_analyzer.get_data()
    for color in data:
        if data[color]:
            print(color)
            [print(node) for node in data[color]]

