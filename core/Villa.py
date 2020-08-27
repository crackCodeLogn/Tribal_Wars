"""
@author Vivek
@since 26/01/20
"""
import math


class FarmVilla:
    x = 0
    y = 0
    points = 0
    ignore = False
    units = []  # seq: sp sw axe spy lcav hcav ram cat - 8 - NO ARCHERS

    def __init__(self, x, y, units=None, name=None, points=None, **kwargs):
        self.x = int(x)
        self.y = int(y)
        self.units = units
        self.name = name
        self.points = points
        self.ignore = kwargs.get('ignore', False)  # will not be present in each village json
        self.ignore_json = 'true' if self.ignore else 'false'
        self.meta = kwargs.get('meta', '')  # will not be present in each village json

        self.coordinates = self._extract_coords()
        self.display_name = self._generate_display_name()

    def _extract_coords(self):
        return "{}|{}".format(self.x, self.y)

    def get_distance_from_another_villa(self, other_villa):
        delta_x = other_villa.get_x() - self.get_x()
        delta_y = other_villa.get_y() - self.get_y()
        val = math.sqrt(delta_x ** 2 + delta_y ** 2)
        return round(val)

    def _generate_display_name(self):
        return "{}. {} - {} pts :: {} {}".format(self.get_coordinates(), self.name, self.points, self.units, self.meta)

    def get_axes(self):
        return self.units[2] if self.units else -1

    def get_lcav(self):
        return self.units[4] if self.units else -1

    def set_axes(self, axes):
        self.__check_units()
        self.units[2] = axes

    def set_scouts(self, scouts):
        self.__check_units()
        self.units[3] = scouts

    def set_lcav(self, lcav):
        self.__check_units()
        self.units[4] = lcav

    def __check_units(self):
        if not self.units: self.units = [0 for i in range(1, 9)]

    def get_coordinates(self):
        return self.coordinates

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_units(self):
        return self.units

    def is_ignored(self):
        return self.ignore

    def get_points(self):
        return self.points

    def get_display_name(self):
        return self.display_name

    def get_meta(self):
        return self.meta

    def __eq__(self, other):
        if other is None and other == self: return False
        if isinstance(other, FarmVilla): return other.get_coordinates() == self.get_coordinates()
        return False

    def __hash__(self):
        return hash(self.get_coordinates())

    def __repr__(self):
        return self.display_name
