from typing import Dict, List, Union, Any
from .node import Node
from importer import sig_tuple

default_header = ['/*************************************/',
                  '/* PyDeviceTree by Gumstix           */',
                  '/* Copyright (c) 2020 Gumstix, Inc   */',
                  '/*************************************/',
                  '']


class DeviceTree(object):
    filename:   str
    dts_version: int
    gcc_include: List[str]
    gcc_define: Dict[str, Union[bool, str, int]]
    _all_nodes: Dict[int, Node]

    def __init__(self):
        self.filename = None
        self._all_nodes = {0: Node(nodename='/')}
        self.dts_version = 1
        self.gcc_include = []
        self.gcc_define = {}

    def __str__(self):
        text = '\n'.join(default_header)
        text += '\n/dts-v{}/;\n\n'.format(self.dts_version)
        for inc in self.gcc_include:
            text += '#include {}\n'.format(inc)
        text += '\n'
        for name, val in self.gcc_define.items():
            text += '#define {}'.format(name)
            if type(val) not in (bool, type(None)):
                text += ' {}'.format(val)
            text += '\n'

        root = self.nodes_by_name.get('/', None)
        if root is not None:
            text += root.print(1) + '\n'
        for _, node in self.nodes_by_ref.items():
            text += node.print(0) + '\n'
        return text


    @classmethod
    def new_devicetree(cls,
                       filename: str):
        new_dt = cls()
        if not isinstance(filename, str):
            raise TypeError('{} is not compatible with DeviceTree.filename'.format(type(filename)))
        new_dt.filename = filename
        return new_dt

    @property
    def nodes_by_name(self) -> Dict[str, Node]:
        nodes = {}
        for _, n in self._all_nodes.items():
            if n.nodename is not None:
                name = n.nodename
                if n.reg is not None:
                    name += '@' + str(n.reg)
            nodes[name] = n
        return nodes

    @property
    def nodes_by_ref(self) -> Dict[str, Node]:
        nodes = {n.ref: n for _, n in self._all_nodes.items() if n.ref is not None}
        return nodes

    def get_node_from_tuple(self, tup: sig_tuple) -> Union[Node, None]:
        # candidates = None
        node = None
        if tup.nodename is not None:
            candidates = [n for k, n in self.nodes_by_name.items() if k.startswith(tup.nodename)]
            if candidates is not None and len(candidates) > 0:
                node = next((n for n in candidates if n.reg == tup.reg), None)

        elif tup.ref is not None:
            node = self.nodes_by_ref.get(tup.ref, None)
        return node

    def new_node(self,
                 parent=None,
                 nodename=None,
                 handle=None,
                 ref=None,
                 reg=None):

        new_node = Node(parent, nodename, handle, ref, reg)
        entry_number = self.add_node(new_node)
        return entry_number, new_node

    def add_node(self,
                 node):
        entry_number = max(self._all_nodes.keys()) + 1
        self._all_nodes[entry_number] = node
        return entry_number


