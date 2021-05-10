from . import DeviceTree

class Comparator(object):
    def __init__(self, dt1: DeviceTree, dt2: DeviceTree):
        self.dt1 = dt1
        self.dt2 = dt2

