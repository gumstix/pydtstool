import os
from device_tree import DeviceTree, Node
from device_tree.node_properties import *

class Dictifier(object):
    def __init__(self, dt: DeviceTree):
        self.dt = dt
        self.data = {}
        self.yaml_name = dt.filename

    def export(self):
        data = self.data
        data['filename'] = self.dt.filename
        data['gcc_include'] = self.dt.gcc_include
        data['']

