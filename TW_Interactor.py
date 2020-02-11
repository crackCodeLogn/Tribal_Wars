"""
@author Vivek
@since 26/01/20
"""
import time
from selenium.webdriver.common.keys import Keys


class TWI:

    def __init__(self, driver, helper):
        self.driver = driver
        self.helper = helper  # for accessing the config.json props

    def login(self, user, cred):
        login_time = 5
        print("Filling up credentials now")
        print("Title : " + str(self.driver.title))
        self.driver.find_element_by_id(self.extract_elements_from_site('id', 'user')).send_keys(user)
        self.driver.find_element_by_id(self.extract_elements_from_site('id', 'password')).send_keys(cred)
        print("Credentials filled, button to be clicked now")
        try:
            self.driver.find_element_by_class_name(self.extract_elements_from_site('class', 'btn.login')).click()
        except Exception as e:
            print("Error occurred whilst logging in.. Err: " + str(e))
        print('Sleeping for {} seconds to allow login!'.format(login_time))
        time.sleep(login_time)

    def create_new_tab_and_switch_to_it(self):
        print(self.driver.current_window_handle)
        self.driver.execute_script("window.open()")
        list = self.driver.window_handles
        print(str(list))
        self.driver.switch_to.window(list[1])
        return list

    def load_page(self, url):
        print('Hitting url => ' + url)
        self.driver.get(url)

    def fill_attack_form_and_attack(self, villa, rally_url):
        units = villa.get_units()
        did_attack_happen = True
        try:
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'spe')).send_keys(units[0])
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'swo')).send_keys(units[1])
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'axe')).send_keys(units[2])
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'spy')).send_keys(units[3])
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'lca')).send_keys(units[4])
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'hca')).send_keys(units[5])  # not-checked, might bug up
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'ram')).send_keys(units[6])
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'cat')).send_keys(units[7])  # not-checked, might bug up

            self.driver.find_element_by_class_name(self.extract_elements_from_site('class', 'input.field')).send_keys(villa.get_coordinates())
            #time.sleep(.150)
            self.driver.find_element_by_class_name(self.extract_elements_from_site('class', 'input.field')).send_keys(Keys.ENTER)
            time.sleep(.5)
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'btn.attack')).click()

            time.sleep(.125)
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'btn.attack.confirm')).click()
            #time.sleep(.5)

            # THE ATTACK HAS BEEN APPROVED
        except Exception as e2:
            print("Exception occurred in this villa's traversal : " + str(e2))
            self.load_page(rally_url)
            did_attack_happen = False
        return did_attack_happen

    def logout(self):
        list = self.driver.find_elements_by_link_text(self.extract_elements_from_site('link.text', 'logout'))
        list[0].click()
        print("Logging out")

    def extract_elements_from_site(self, type, key):
        return self.helper.extract_base_info('elements')[type][key]
