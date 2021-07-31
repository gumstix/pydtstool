###################################################
#                    pyDtsTool                 #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################
from typing import Dict, List, Union
from collections import defaultdict

from pyDtsTool.common import sig_tuple
from .node import Node

default_header = ['/*********************************************/',
                  '/* pyDtsTool by Altium                    */',
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
        nodes = {n.ref: n for _, n in self._all_nodes.items() if n.ref is not None}
        return nodes

    def _node_indexes_by_path(self) -> Dict[str, List[int]]:
        nodes = defaultdict(list)
        for i, n in self._all_nodes.items():
            if n.path != None:
                nodes[n.path].append(i)
        return dict(nodes)

    def _node_indexes_by_ref(self) -> Dict[str, List[int]]:
        nodes = defaultdict(list)
        for i, n in self._all_nodes.items():
            if n.ref != None:
                nodes[n.ref].append(i)
        return dict(nodes)

    def _node_indexes_by_handle(self) -> Dict[str, List[int]]:
        nodes = defaultdict(list)
        for i, n in self._all_nodes.items():
            if len(n.handles) > 0:
                for h in n.handles:
                    nodes[h].append(i)
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
                 handles=[],
                 ref=None,
                 reg=None):
        if isinstance(handles, str):
            handles = handles.split(': ')
        new_node = Node(parent, nodename, handles, ref, reg)
        entry_number = self.add_node(new_node)
        return entry_number, new_node

    def add_node(self,
                 node):
        entry_number = max(self._all_nodes.keys()) + 1
        self._all_nodes[entry_number] = node
        return entry_number

    def merge_refs(self):
        ref_indexes = self._node_indexes_by_ref()
        handle_indexes = self._node_indexes_by_handle()
        for r, indexes in ref_indexes.items():
            if r in handle_indexes.keys():
                assert len(handle_indexes[r]) == 1
                parent = self._all_nodes[handle_indexes[r][0]]
                for i in indexes:
                    if i in self._all_nodes.keys() and self._all_nodes[i] != None:
                        child = self._all_nodes.pop(i)
                        child.ref = None
                        parent.join(child)
        return

    def merge_paths(self):
        path_indexes = {p: l for p, l in self._node_indexes_by_path().items() if len(l) > 1}
        for path, indexes in path_indexes.items():
            parent = self._all_nodes[indexes[0]]
            for i in indexes[1:]:
                child = self._all_nodes.pop(i)
                parent.join(child)
        return

    def node_paths(self) -> list:
        return list(set(self._node_indexes_by_path().keys()))

    def merge(self):
        self.merge_refs()
        self.merge_paths()
