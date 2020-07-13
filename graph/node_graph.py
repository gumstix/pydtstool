import graphviz
from device_tree import DeviceTree
import os


class DtGraph(object):
    def __init__(self, device_tree: DeviceTree):
        self.dt = device_tree
        self.graph = graphviz.Digraph(self.dt.filename, filename=os.path.splitext(self.dt.filename)[0] + '.gv')
        self.graph.attr(rankdir='LR')

