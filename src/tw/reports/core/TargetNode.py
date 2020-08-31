"""
@author Vivek
@since 31/08/20
"""
from src.core.Villa import FarmVilla


class TargetNode:

    def __init__(self, color_code, x, y, url):
        self.color_code = color_code
        self.villa = FarmVilla(x, y)
        self.url = url

        self.resources = 0
        self.wall = 0
        self.martyr_axes = 0
        self.martyr_lcav = 0

    def __eq__(self, other):
        if other is None and other == self: return False
        if isinstance(other, TargetNode): return other.__repr__() == self.__repr__()
        return False

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        return "{}. {}".format(self.color_code.name, self.villa)

    def set_res(self, resources):
        self.resources = resources

    def set_wall(self, wall_lvl):
        self.wall = wall_lvl

    def set_martyr_axes(self, axes):
        self.martyr_axes = axes

    def set_martyr_lcav(self, lcav):
        self.martyr_lcav = lcav

    def get_color(self):
        return self.color_code

    def get_villa(self):
        return self.villa

    def get_res(self):
        return self.resources

    def get_wall(self):
        return self.wall

    def get_martyr_axes(self):
        return self.martyr_axes

    def get_martyr_lcav(self):
        return self.martyr_lcav

    def get_url(self):
        return self.url
