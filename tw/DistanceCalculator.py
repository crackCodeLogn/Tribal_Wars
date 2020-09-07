"""
@author Vivek
@since 01/02/20

Takes in the entire list of villages and generates stats of distance and attack time
"""
from core.Villa import FarmVilla as Villa
from core.VillaStats import Stats
from util.Helper import read_generic_config


class DistanceCalc:

    def __init__(self, current_world_config, farm_list, units_speed):
        self.current_world_config = current_world_config
        self.farm_list = farm_list
        self.units_speed = units_speed
        self.central = self.generate_central_village_info()

    def generate_central_village_info(self):
        x = read_generic_config(self.current_world_config, 'villa')['x']
        y = read_generic_config(self.current_world_config, 'villa')['y']
        name = read_generic_config(self.current_world_config, 'villa')['name']
        points = read_generic_config(self.current_world_config, 'villa')['points']
        return Villa(x, y, None, name, points)

    def _compute_slowest_unit(self, units_for_dest_villa):
        slowest = 0
        for i in range(0, len(units_for_dest_villa)):
            if units_for_dest_villa[i] != 0 and self.units_speed[i] > slowest:
                slowest = self.units_speed[i]
        return slowest

    def perform_calculation(self):
        """Returns a dict of villa v/s stats"""
        stats = {}
        for villa in self.farm_list:
            distance = self.central.get_distance_from_another_villa(villa)
            slowest_unit_time = self._compute_slowest_unit(villa.get_units())
            stats[villa] = Stats(distance, distance * slowest_unit_time)
        return stats

    def update_to_lcav_only(self, stats):
        redeployment = False
        for villa in self.farm_list:
            if stats[villa].get_tta_hrs() > 5.5:
                villa.set_axes(0)
                villa.set_lcav(11)
                redeployment = True
        return redeployment

    def display_stats(self, stats):
        for villa in stats:
            print("{} => {} {}".format(villa, stats[villa], "-- switchToLcav" if stats[villa].tta_hrs > 4 else ""))
