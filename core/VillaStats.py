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

    def __repr__(self):
        return "{} fields, {} minutes ~ {} hours".format(self.distance, self.tta_minz, format(self.tta_hrs, '.2f'))
