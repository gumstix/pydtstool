from typing import Dict
from .node import NodeSignatureError, Node


class DeviceTree(object):
    filename:   str
    _all_nodes: Dict[int, Node]

    def __init__(self):
        self.filename = None
        self._all_nodes = {0: Node(nodename='/')}

    @classmethod
    def new_devicetree(cls,
                       filename: str):
        new_dt = cls()
        if not isinstance(filename, str):
            raise TypeError('{} is not compatible with DeviceTree.filename'.format(type(filename)))
        new_dt.filename = filename
        return new_dt

    def new_node(self,
                 parent=None,
                 nodename=None,
                 handle=None,
                 ref=None):

        new_node = Node(parent, nodename, handle, ref)
        entry_number = self.add_node(new_node)
        return entry_number, new_node

    def add_node(self,
                 node):
        entry_number = max(self._all_nodes.keys()) + 1
        self._all_nodes[entry_number] = node
        return entry_number
