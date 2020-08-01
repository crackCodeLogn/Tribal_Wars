"""
@author Vivek
@since 26/01/20

The central class which triggers the entire op
"""
import json
import time

from DistanceCalculator import DistanceCalc
from DriverCommandCenter import Driver
from Helper import Helper, read_config_world_level, read_generic_config, print_list
from TW_Interactor import TWI
from core.Villa import FarmVilla as Villa


class NewFarmingCommandCenter:

    def __init__(self, config, world, mode):
        self.helper = Helper(config)
        self.world = world
        self.mode = mode

        self.current_world_config = read_config_world_level(self.world)
        self.base_screen_url = self.helper.extract_base_screen_url(
            read_generic_config(self.current_world_config, 'villa')['world'],
            read_generic_config(self.current_world_config, 'villa')['id'])  # obtain targeted world details
        # https://en112.tribalwars.net/game.php?village=481&screen={screen}

        browser = read_generic_config(self.current_world_config, "driver")
        self.Driver = Driver(
            browser,
            self.helper.extract_base_info('driver')[browser]
        )  # obtain driver here
        self.driver = self.Driver.get_driver()

        self.interactor = TWI(self.driver, self.helper)
        self.world_homepage = self.helper.extract_base_info('homepage.world').format(self.world)

    def read_in_villas_to_be_farmed(self):
        raw_farm_villas_list = read_generic_config(self.current_world_config, 'farming')
        raw_farm_villas_list = [Villa(**villa) for villa in raw_farm_villas_list]
        raw_farm_villas_list = self.filter_villas_to_farm(raw_farm_villas_list)
        # Un-comment only whilst weeding up the duplicates, as set destroy order of villages from config
        # print('Pre-conv to set size: '+str(len(raw_farm_villas_list)))
        # raw_farm_villas_list = set(raw_farm_villas_list)
        print('Final number of villas being farmed: ' + str(len(raw_farm_villas_list)))
        return raw_farm_villas_list

    def filter_villas_to_farm(self, raw_farm_villas_list):
        return [villa for villa in raw_farm_villas_list if not villa.is_ignored()]

    def compute_units_required(self, farm_list):
        required_units = [sum(units) for units in zip(*[val.get_units() for val in farm_list])]  # the * helps in summing up the units' array
        print("The attack units required:-")
        print(required_units)  # later, replace this with pandas
        return required_units

    def extract_units_speed(self):
        return read_generic_config(self.current_world_config, 'speed')

    def perform_analysis_farming_run(self, required_units):
        """A potential bug is the part where there are units present from other units in the village where the farming is to be started.
        This will lead to mis-calc of own troops from the main screen where this is based.
        BUT side-stepping this for now, as i'll not be farming most probably if there is an attack on-going"""
        # self.interactor.load_page(self.base_screen_url.format(screen=self.helper.extract_screen('home'))) # Commenting post introduction of 'compute_villas_already_being_attacked'
        available_units = [0] * 8
        xpath = self.helper.extract_base_info("elements")['xpath']['current_troops']

        print("Initiating analysis of farming feasibility")
        for i in range(1, len(available_units) + 1):  # +1 to compensate for the above commented bug of 'All'
            available_unit = self.driver.find_element_by_xpath(xpath.format(i)).text
            try:
                print("available unit : " + available_unit)
                units = int(available_unit[:available_unit.index(" ")])

                if "Spear" in available_unit:
                    available_units[0] += units
                elif "Sword" in available_unit:
                    available_units[1] += units
                elif "Axe" in available_unit:
                    available_units[2] += units
                elif "Scout" in available_unit:
                    available_units[3] += units
                elif "Light" in available_unit:
                    available_units[4] += units
                elif "Heavy" in available_unit:  # not-checked, might bug up
                    available_units[5] += units
                elif "Ram" in available_unit:
                    available_units[6] += units
                elif "Cat" in available_unit:  # not-checked, might bug up
                    available_units[7] += units

            except Exception as e1:
                if available_unit != 'All':
                    print("Breakin off at i : " + str(i) + ", exception : " + str(e1))
                    break
                else:
                    print('Encountered All from the new screen type. Will be flying by.')

        is_attack_possible = True
        for i in range(0, len(available_units)):
            if available_units[i] < required_units[i]:
                is_attack_possible = False
                break
        return is_attack_possible, available_units

    def commence_farming_op(self, farm_list, is_full_attack_possible, available_units):
        rally_url = self.base_screen_url.format(screen=self.helper.extract_screen('rally'))
        self.interactor.load_page(rally_url)
        self.interactor.set_available_units(available_units)

        for i in range(1, len(farm_list) + 1):
            villa = farm_list[i - 1]
            print('{}. {}'.format(i, villa.get_display_name()))
            '''
            if not is_full_attack_possible:
                choice = input("Do you want to attack this village? (y/n)")
                if choice == 'n': continue
            '''

            result = self.interactor.fill_attack_form_and_attack(villa, rally_url)
            if result == "BREAK-EXECUTION":
                print("Final break... Breaking out of farming op now!")
                break
            if result:
                print("Attack placed for this village.")
            else:
                print("*** Couldn't place attack for this village! ***")

    def _parse_attack_cmd_for_coords(self, data):
        data = str(data)
        data = data[data.rindex('(') + 1:data.rindex(')')]
        split_pt = data.index('|')
        return int(data[:split_pt]), int(data[split_pt + 1:])

    def _parse_number_of_outgoing_attacks(self, data):
        return int(data[1:-1])  # (12) => 12

    def compute_villas_already_being_attacked(self):
        attack_in_progress_villas = []
        self.interactor.load_page(self.base_screen_url.format(screen=self.helper.extract_screen('home')))
        xpath_all_own_commands_count = '//*[@id="commands_outgoings"]/table/tbody/tr[1]/th[1]/span'
        try:
            attacks_already_count = self._parse_number_of_outgoing_attacks(self.driver.find_element_by_xpath(xpath_all_own_commands_count).text) + 2
            print("Number of already ongoing attacks : " + str(attacks_already_count - 2))

            xpath = '//*[@id="commands_outgoings"]/table/tbody/tr[{}]/td[1]/span/span/a/span[2]'  # 2 onwards
            prefix = 'Attack on '  # Attack on Bonus village (510|530) K55
            for i in range(2, attacks_already_count):
                text = self.driver.find_element_by_xpath(xpath.format(i)).text
                if text.startswith(prefix):
                    x, y = self._parse_attack_cmd_for_coords(text)
                    attack_in_progress_villas.append(Villa(x, y))
        except Exception as e:
            print('Seems like there are no ongoin attacks..')
        return attack_in_progress_villas

    def calc_units_required_and_distance_stats(self, farm_list, units_speed):
        total_units_req = self.compute_units_required(farm_list)

        calculator = DistanceCalc(self.current_world_config, farm_list, units_speed)
        stats = calculator.perform_calculation()
        calculator.display_stats(stats)

        return total_units_req, stats

    def sort_farm_list_least_distance_first(self, farm_list, stats):
        farm_list = sorted(farm_list, key=lambda villa: stats[villa.get_coordinates()].get_tta_minz())
        return farm_list

    def overwatch_farming(self):
        farm_list = self.read_in_villas_to_be_farmed()
        print_list(farm_list)
        units_speed = self.extract_units_speed()

        if self.mode == 'analysis-only':
            print("Analysis mode only. Will not proceed with spawning of selenium session")
            total_units_req = self.compute_units_required(farm_list)

            calculator = DistanceCalc(self.current_world_config, farm_list, units_speed)
            stats = calculator.perform_calculation()
            calculator.display_stats(stats)

            total_units_req, stats = self.calc_units_required_and_distance_stats(farm_list, units_speed)
            farm_list = self.sort_farm_list_least_distance_first(farm_list, stats)
            """
            for villa in farm_list:
                print(villa)
                print(stats[villa.get_coordinates()].get_tta_minz())
                print("****")
            """

            self.closing()
            return

        tw_url = self.helper.extract_base_info("url")
        self.interactor.load_page(tw_url)
        sso_path = self.helper.extract_sso("path")
        sso = json.loads(open(sso_path).read())
        self.interactor.login(
            sso.get("user"),
            sso.get("cred")
        )
        print("Button clicked, switching over to main game page in en{} world".format(self.world))
        self.interactor.load_page(self.world_homepage)

        self.interactor.create_new_tab_and_switch_to_it()
        print("Tab switched;\nVillages to be farmed : " + str(len(farm_list)))

        villas_already_being_attacked = self.compute_villas_already_being_attacked()
        if villas_already_being_attacked:
            print("Villas already being attacked:-")
            for villa in villas_already_being_attacked:
                print(villa.get_coordinates())  # this does not contain any other information from the webpage
                try:
                    farm_list.remove(villa)
                except Exception as e:
                    print("Seems like this village was not in the local_config attack list. Will skip by.")
        else:
            print("No ongoing attacks from this villa. Will go for compute and then attack.")

        total_units_req, stats = self.calc_units_required_and_distance_stats(farm_list, units_speed)
        farm_list = self.sort_farm_list_least_distance_first(farm_list, stats)
        # for villa in farm_list:
        #     print(villa)
        #     print(stats[villa.get_coordinates()].get_tta_minz())
        #     print("****")

        is_full_attack_possible, available_units = self.perform_analysis_farming_run(total_units_req)
        if is_full_attack_possible:
            print('Attacking all enlisted villages!')
        else:
            print('Cannot attack all villages enlisted. Not sufficient troops! Will order as many as I can after your approval on each.')
        self.commence_farming_op(farm_list, is_full_attack_possible, available_units)

        self.interactor.logout()
        self.closing()

    def closing(self):
        self.Driver.kill_driver()


if __name__ == '__main__':
    config = json.loads(open('../res/config.json').read())
    start_time = time.time()

    mode = 'attack'  # 'analysis-only', 'attack'
    # mode = 'analysis-only'  # 'analysis-only', 'attack'
    amaterasu = NewFarmingCommandCenter(config, 115, mode)  # pass world number in parameter
    amaterasu.overwatch_farming()

    end_time = time.time()
    print("\nTotal time taken : {} seconds ~ {} minutes".format(end_time - start_time, (end_time - start_time) / 60.0))
