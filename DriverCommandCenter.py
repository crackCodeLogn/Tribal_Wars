"""
@author Vivek
@since 26/01/20
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Driver:

    def __init__(self, browser, path):
        self.driver = self.__create_driver__(browser, path)

    def get_driver(self):
        return self.driver

    def __create_driver__(self, browser, path):
        browser = browser.lower()
        if browser == 'firefox':
            print("Spawned Firefox driver!")
            return webdriver.Firefox(executable_path=path)
        elif browser == 'chrome':
            options = Options()
            options.add_argument("start-maximized")
            print("Spawned Chrome driver!")
            return webdriver.Chrome(executable_path=path, options=options)
        return None

    def kill_driver(self):
        print("Killing driver now!")
        self.driver.quit()
