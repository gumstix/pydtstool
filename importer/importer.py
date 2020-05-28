import os
import typing

from device_tree.device_tree import DeviceTree
from .parsing import (merge_dict,
                      gcc_match,
                      node_match,
                      line_match,
                      remove_comments,
                      collect_subnodes,
                      parse_property)


class DtImporter(object):
    filename: str
    _data: typing.List[str]
    dt_version: int

    def __init__(self, filename):
        self.nodestrs = {}
        self.filename = filename
        self.dt_version = 1
        self.dt = DeviceTree.new_devicetree(filename)
        if not os.path.isfile(self.filename):
            raise FileNotFoundError(self.filename)
        else:
            with open(self.filename, 'r') as fp:
                self._data = fp.readlines()
            for i, line in enumerate(self._data):
                self._data[i] = line.rstrip('\n')

    def extract_gcc(self):
        for line in self._data:
            groups = gcc_match.search(line)
            if groups is None:
                continue
            if groups.group('inc') is not None:
                self.dt.gcc_include.append(groups.group('val'))
            elif groups.group('def') is not None:
                defn = groups.group('val').split()
                self.dt.gcc_define[defn[0]] = ' '.join(defn[1:])

    def extract_nodes(self):
        data = self._data.copy()
        i = 0
        datalen = len(data)
        while datalen and i < datalen:
            line = data[i]
            m = node_match.search(line)
            if m is not None:
                md = {name: value for name, value in m.groupdict().items() if value is not None}
                if 'sig' in md.keys():
                    if 'extra' in md.keys() and md['extra'].strip() != '':
                        data[i] = md['extra']
                    else:
                        i += 1
                    if md['sig'] not in self.nodestrs.keys():
                        self.nodestrs[md['sig']] = {}
                    data, nodestrs = collect_subnodes(data[i:])
                    self.nodestrs[md['sig']] = merge_dict(self.nodestrs[md['sig']], nodestrs)
                    datalen = len(data)
                    i = 0
                    continue
            else:
                i += 1

    def parse(self, comments: bool = False):
        if not comments:
            data = remove_comments(self._data)
            if data != self._data:
                raise ValueError('data != self.data')
        self.extract_gcc()
        self.extract_nodes()

    def build_node(self, node, lines):
        ag_line = ''
        for line in lines['self']:
            ag_line += line.strip()
            if line.endswith(';'):
                ag_line = ag_line[:-1]
                groups = line_match.search(ag_line)
                if groups is not None:
                    gd = groups.groupdict()
                    if gd.get('eq', None) is not None:
                        prop_name = gd['head']
                        prop_val = parse_property(gd['tail'])
                        node.set_property(prop_name, prop_val)
                    elif gd.get('bool', None) is not None:
                        node.set_property(gd['bool'])
                    elif gd.get('dtc', None) is not None:
                        node.dtc[gd['dtc']].append(gd['tail'])
                ag_line = ''
        for sig, sub_lines in lines['subnodes'].items():
            sigtup = make_sig_tuple(sig)
            child = None
            for c in node.children:
                if c.nodename == sigtup.nodename:
                    if sigtup.reg is not None and sigtup.reg == c.reg:
                        child = c
            if child is None:
                _, child = self.dt.new_node(node, *sigtup)
            self.build_node(child, sub_lines)

    def build(self):
        for sig, nodelines in self.nodestrs.items():
            sigtup = make_sig_tuple(sig)
            node = self.dt.get_node_from_tuple(sigtup)
            if node is None:
                _, node = self.dt.new_node(None, *sigtup)
            self.build_node(node, nodelines)

    def export(self, filename):
        with open(filename, 'w+') as fp:
            fp.write(str(self.dt))
