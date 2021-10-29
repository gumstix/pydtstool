###################################################
#                    pyDtsTool                    #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################

from . import DeviceTree, NodeProperty, Node
from pyDtsTool.common import sig_tuple, tuple_representer
import yaml


def _g_tuples_to_str(data: dict):
    for key, val in data.items():
        if isinstance(val, dict):
            data[key] = _g_tuples_to_str(val)
        elif isinstance(val, tuple):
            data[key] = ' '.join(val)
    return data


class Comparator(object):
    def __init__(self, dt1: DeviceTree, dt2: DeviceTree):
        """Object comparing two device tree sources, returning a YAML with details of what is different or missing"""
        self.dt1 = dt1
        self.dt2 = dt2
        self.diff = None

    def missing_nodes(self) -> tuple:
        """Searches for unpaired paths bidirectionally"""
        d1_paths = self.dt1.node_paths()
        d2_paths = self.dt2.node_paths()
        d1_missing = [p for p in d1_paths if p not in d2_paths]
        d2_missing = [p for p in d2_paths if p not in d1_paths]
        return d1_missing, d2_missing

    def _node_diff(self, node: Node, node2: Node) -> dict:
        diff = {}
        props1 = node.properties
        props2 = node2.properties
        for prop in props1:
            prop2 = next((p for p in props2 if p.property_name == prop.property_name), None)
            if prop2 is None:
                diff[prop.property_name] = {1: prop.property_value, 2: '*missing'}
            elif prop.property_value != prop2.property_value:
                diff[prop.property_name] = {1: prop.property_value, 2: prop2.property_value}
        for prop2 in props2:
            prop = next((p for p in props1 if p.property_name == prop2.property_name), None)
            if prop is None:
                diff[prop2.property_name] = {1: '*missing', 2: prop2.property_value}
        if len(node.children) > 0 or len(node2.children) > 0:
            diff['nodes'] = {}
            for n in node.children:
                n2 = next((c for c in node2.children if c.pathname == n.pathname), None)
                if n2 is None:
                    diff['nodes'][n.pathname] = {1: '*present', 2: '*missing'}
                else:
                    diff['nodes'][n.pathname] = self._node_diff(n, n2)
                    if diff['nodes'][n.pathname] == {}:
                        del diff['nodes'][n.pathname]
            for n in node2.children:
                n2 = next((c for c in node.children if c.pathname == n.pathname), None)
                if n2 is None:
                    diff['nodes'][n.pathname] = {1: '*missing', 2: '*present'}
            if diff['nodes'] == {}:
                del diff['nodes']
        return diff

    def get_diff(self):
        """Recursive comparison of two DeviceTree objects"""
        root_d1 = self.dt1.get_node_from_tuple(sig_tuple('/', None, None, None))
        root_d2 = self.dt2.get_node_from_tuple(sig_tuple('/', None, None, None))
        self.diff = {'filenames': {1: self.dt1.filename, 2: self.dt2.filename}, 'root': {}}
        props1 = root_d1.properties
        props2 = root_d2.properties
        for prop in props1:
            prop2 = next((p for p in props2 if p.property_name == prop.property_name), None)
            if prop2 is None:
                self.diff['root'][prop.property_name] = {1: prop.property_value, 2: '*missing'}
            elif prop.property_value != prop2.property_value:
                self.diff['root'][prop.property_name] = {1: prop.property_value, 2: prop2.property_value}
        for prop2 in props2:
            prop = next((p for p in props1 if p.property_name == prop2.property_name), None)
            if prop is None:
                self.diff['root'][prop2.property_name] = {1: '*missing', 2: prop2.property_value}
        self.diff['root']['nodes'] = {}
        for node in root_d1.children:
            node2 = next((n for n in root_d2.children if n.pathname == node.pathname),
                         None)
            if node2 is None:
                self.diff['root']['nodes'][node.pathname] = {1: '*present', 2: '*missing'}
            else:
                ndiff = self._node_diff(node, node2)
                if ndiff not in [{}, None]:
                    self.diff['root']['nodes'][node.pathname] = ndiff
        for node2 in root_d2.children:
            node = next((n for n in root_d1.children if n.pathname == node2.pathname), None)
            if node is None:
                self.diff['root']['nodes'][node2.pathname] = {1: '*missing', 2: '*present'}
        self.diff['ref_nodes'] = {}
        for ref, node in self.dt1.nodes_by_ref.items():
            node2 = self.dt2.nodes_by_ref.get(ref, None)
            if node2 is None:
                self.diff['ref_nodes'][ref] = {1: '*present', 2: '*missing'}
            else:
                ndiff = self._node_diff(node, node2)
                if ndiff not in [{}, None]:
                    self.diff['ref_nodes'][ref] = ndiff
        for ref in [r for r in self.dt2.nodes_by_ref.keys() if r not in self.dt1.nodes_by_ref.keys()]:
            self.diff['ref_nodes'][ref] = {1: '*missing', 2: '*present'}
        self._cleanup_diff()

    def _cleanup_diff(self):
        if 'nodes' in self.diff['root'].keys() and len(self.diff['root']['nodes']) == 0:
            del self.diff['root']['nodes']
        if len(self.diff['root'].keys()) == 0:
            del self.diff['root']
        if len(self.diff['ref_nodes'].keys()) == 0:
            del self.diff['ref_nodes']

    def _props_to_str(self):
        for key, val in self.diff.items():
            if isinstance(val, dict):
                self.diff[key] = _g_tuples_to_str(val)
            elif isinstance(val, NodeProperty):
                self.diff[key] = str(val)

    def print_output(self, filename: str=None):
        """YAML representation of DT differences"""
        yaml.add_representer(tuple, tuple_representer)
        if self.diff is None:
            self.get_diff()
        self._props_to_str()
        out = None
        if len(self.diff.keys()) > 1:
            if filename is not None:
                with open(filename, 'w+') as out:
                    yaml.dump(self.diff, out, yaml.Dumper)
            else:
                print(yaml.dump(self.diff))
        else:
            print('The following device trees are identical:\n'
                  '-----------------------------------------\n')
            print(yaml.dump(self.diff))
            

