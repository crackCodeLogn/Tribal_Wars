"""
@author Vivek
@since 03/02/20
"""


class Stats:

    def __init__(self, distance, tta_minz):
        """tta - time to attack"""
        self.distance = distance
        self.tta_minz = tta_minz
        self.tta_hrs = tta_minz / 60

    def get_tta_minz(self):
        return self.tta_minz

    def get_tta_hrs(self):
        return self.tta_hrs

    def __repr__(self):
        return "{} fields, {} minutes ~ {} hours".format(self.distance, self.tta_minz, format(self.tta_hrs, '.2f'))
