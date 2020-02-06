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
        self.x = x
        self.y = y
        self.units = units
        self.name = name
        self.points = points
        self.ignore = kwargs.get('ignore', False)  # will not be present in each village json

        self.coordinates = self._extract_coords()
        self.display_name = self._generate_display_name()

    def _extract_coords(self):
        return "{}|{}".format(self.x, self.y)

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

    def get_display_name(self):
        return self.display_name

    def get_distance_from_another_villa(self, other_villa):
        delta_x = other_villa.get_x() - self.get_x()
        delta_y = other_villa.get_y() - self.get_y()
        val = math.sqrt(delta_x ** 2 + delta_y ** 2)
        return round(val)

    def _generate_display_name(self):
        return "{}. {} - {} pts :: {}".format(self.get_coordinates(), self.name, self.points, self.units)

    def __eq__(self, other):
        if other is None and other == self: return False
        if isinstance(other, FarmVilla): return other.get_coordinates() == self.get_coordinates()
        return False

    def __hash__(self):
        return hash(self.get_coordinates())

    def __repr__(self):
        return self.display_name
