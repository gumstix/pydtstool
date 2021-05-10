###################################################
#                    PyDeviceTree                 #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################
from typing import Dict, List, Union
from collections import defaultdict

from dtsgen.common import sig_tuple
from .node import Node

default_header = ['/*********************************************/',
                  '/* PyDeviceTree by Altium                    */',
                  '/* Copyright (c) 2020 Altium, Inc            */',
                  '/* Contact: Keith Lee <keith.lee@altium.com> */',
                  '/*********************************************/',
                  '']


class DeviceTree(object):
    def __init__(self):
            self.filename: str = None
            self.dts_version: int = 1
            self.gcc_include: List[str] = []
            self.gcc_define: Dict[str, Union[bool, str, int]] = {}
            self.dtc_special: Dict[str, str] = {}
            self._all_nodes: Dict[int, Node] = {0: Node(nodename='/')}

    def __str__(self):
        text = '\n'.join(default_header)
        text += '\n/dts-v{}/;\n\n'.format(self.dts_version)
        for k, v in self.dtc_special.items():
            if not k.startswith('dts-v'):
                if not v.endswith(';'):
                    v += ';'
                text += '/{}/ {}\n\n'.format(k, v)
        for inc in self.gcc_include:
            if inc.startswith('<'):
                text += '#include {}\n'.format(inc)
            else:
                text += '#include "{}"\n'.format(inc)
        text += '\n'
        for name, val in self.gcc_define.items():
            text += '#define {}'.format(name)
            if type(val) not in (bool, type(None)):
                text += ' {}'.format(val)
            text += '\n'
        text += '\n'
        root = self.nodes_by_name.get('/', None)
        if root is not None:
            text += root.print() + '\n'
        for _, node in self.nodes_by_ref.items():
            text += '\n' + node.print() + '\n'
        return text

    def copy(self):
        new_dt = self.__class__()
        new_dt.filename = self.filename
        new_dt.dts_version = self.dts_version
        new_dt.gcc_include = self.gcc_include.copy()
        new_dt.gcc_define = self.gcc_define.copy()
        new_dt._all_nodes = self._all_nodes.copy()
        return new_dt

    @classmethod
    def new_devicetree(cls,
                       filename: str):
        """
        Verify filename and return new device tree object
        :param filename: str
        :return: DeviceTree
        """
        new_dt = cls()
        if not isinstance(filename, str):
            raise TypeError('{} is not compatible with DeviceTree.filename'.format(type(filename)))
        new_dt.filename = filename
        return new_dt

    @property
    def nodes_by_name(self) -> Dict[str, Node]:
        """
        Dictify all nodes that have root name and register
        :return: Dict[str, Node]
        """
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
        """
        Dictify all nodes that are reference nodes
        :return:
        """
        nodes = {n.ref: n for _, n in self._all_nodes.items() if n.ref is not None}
        return nodes

    def _node_indexes_by_refhandle(self) -> Dict[str, List[int]]:
        nodes = defaultdict(list)
        for i, n in self._all_nodes.items():
            if n.handle is not None:
                nodes[n.handle].append(i)
            if n.ref is not None:
                nodes[n.ref].append(i)
        return dict(nodes)

    def get_node_from_tuple(self, tup: sig_tuple) -> Union[Node, None]:
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

    def merge_by_handle(self):
        to_merge = {tag: indexes for tag, indexes in self._node_indexes_by_refhandle().items() if len(indexes) > 1}
        for tag, indexes in to_merge.items():
            top_index = next(i for i in indexes if self._all_nodes[i].handle is not None)
            top_node = self._all_nodes[top_index]
            for i in sorted(indexes):
                if i is not top_index:
                    top_node.join(self._all_nodes[i])
                    self._all_nodes[i] = None
        self._all_nodes = {k: v for k, v in self._all_nodes.items() if v is not None}
        return



