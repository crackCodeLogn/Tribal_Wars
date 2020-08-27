"""
@author Vivek
@since 26/01/20
"""
import operator
import time

from selenium.webdriver.common.keys import Keys


class TWI:

    def __init__(self, driver, helper):
        self.driver = driver
        self.helper = helper  # for accessing the config.json props

        self.populate_ckt_breakers(self.helper.extract_ckt_breakers())

    def populate_ckt_breakers(self, ckt_breakers_content):
        self.ckt_breakers = {}
        for key in ckt_breakers_content:
            self.ckt_breakers[key] = ckt_breakers_content[key]
        self.list_value_ckt_breakers = list(self.ckt_breakers.values())

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

    def set_available_units(self, avail):
        self.available_units = avail  # Performing the sin of maintaining the state
        self.switch_to_axe = False  # Because there will always be a higher population of axe than lcav
        self.failed_attack_cmds = 0

    def check_for_ckt_breakers(self, failed_attack_cnt):
        if failed_attack_cnt in self.list_value_ckt_breakers:
            ckt_breaker_key = list(self.ckt_breakers.keys())[self.list_value_ckt_breakers.index(failed_attack_cnt)]
            print("Encountered '{}' ckt-breaker at '{}' attack cmds not going through".format(ckt_breaker_key, failed_attack_cnt))
            if ckt_breaker_key == 'LAST': return "BREAK-EXECUTION"
        return None

    def fill_attack_form_and_attack(self, villa, rally_url):
        res = self.check_for_ckt_breakers(self.failed_attack_cmds)
        if res:
            print("Breaking execution as number of attack cmds failing breached the LAST Limit. Possibly bot detection ran. Re-trigger!")
            return res, None

        units = villa.get_units()
        did_attack_happen = True
        override_failed_attack_cmds = False
        try:
            print("Available units: " + str(self.available_units))
            # computing availability of troops for attack
            if not self.switch_to_axe:
                if self.available_units[4] < units[4]:
                    self.switch_to_axe = True

            if self.switch_to_axe and units[0] == 0 and units[1] == 0:  # assuming that axe and lcav will always be mutually exclusive
                print("Force-switching to axe as lcav seems to be over!")
                units[2] += 20
                units[4] = 0

            if self.available_units[2] < units[2] and self.available_units[4] > units[4]:
                print("Switching from axe to lcav as axes have ran out. Current Axes: {}. lcav: {}".format(self.available_units[2], self.available_units[4]))
                units[2] = 0
                units[4] = 7

            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'spe')).send_keys(units[0])
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'swo')).send_keys(units[1])
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'axe')).send_keys(units[2])
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'spy')).send_keys(units[3])
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'lca')).send_keys(units[4])
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'hca')).send_keys(units[5])  # not-checked, might bug up
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'ram')).send_keys(units[6])
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'cat')).send_keys(units[7])  # not-checked, might bug up

            self.driver.find_element_by_class_name(self.extract_elements_from_site('class', 'input.field')).send_keys(villa.get_coordinates())
            # time.sleep(.150)
            self.driver.find_element_by_class_name(self.extract_elements_from_site('class', 'input.field')).send_keys(Keys.ENTER)
            time.sleep(.5)
            self.driver.find_element_by_id(self.extract_elements_from_site('id', 'btn.attack')).click()

            time.sleep(.125)
            # check whether it has gotten owned by some player
            place_attack = True
            if 'barb' in villa.get_display_name().lower():  # have designated it to be a barb, and a player has nobled it
                xpath = '//*[@id="command-data-form"]/div[1]/table/tbody/tr[3]/td[1]'
                search_str_found = False
                try:
                    field = self.driver.find_element_by_xpath(xpath).text
                    if 'Player' in field: search_str_found = True
                except Exception as unable_locate_err:
                    xpath = '//*[@id="content_value"]/div[1]/div'
                    field = self.driver.find_element_by_xpath(xpath).text
                    if 'do not exceed 120%' in field:
                        search_str_found = True
                        print("120% err msg.")

                if search_str_found:
                    print('*** Cannot place attack as this village was previously a barb but not got nobled! Remove from config ASAP! ***')
                    did_attack_happen = False
                    place_attack = False
                    override_failed_attack_cmds = True

            if place_attack:
                self.driver.find_element_by_id(self.extract_elements_from_site('id', 'btn.attack.confirm')).click()
                # reducing available units count here, post successful op
                self.available_units = list(map(operator.sub, self.available_units, units))
                # print("Successfully reduced available units to: ")
                # pprint(self.available_units)

            # THE ATTACK HAS BEEN APPROVED
        except Exception as e2:
            print("Exception occurred in this villa's traversal : " + str(e2))
            did_attack_happen = False
            if not override_failed_attack_cmds: self.failed_attack_cmds += 1

        trash = None
        if not did_attack_happen and override_failed_attack_cmds:
            trash = villa
            self.load_page(rally_url)
        return did_attack_happen, trash

    def logout(self):
        list = self.driver.find_elements_by_link_text(self.extract_elements_from_site('link.text', 'logout'))
        list[0].click()
        print("Logging out")

    def extract_elements_from_site(self, type, key):
        return self.helper.extract_base_info('elements')[type][key]
