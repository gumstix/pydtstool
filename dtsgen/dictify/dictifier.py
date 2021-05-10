###################################################
#                    PyDeviceTree                 #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################
import os
import yaml
from dtsgen import DeviceTree, Node
from dtsgen.node_properties import *


class Dictifier(object):
    def __init__(self, dt: DeviceTree):
        self.dt = dt
        self.data = {}
        self.yaml_name = os.path.splitext(os.path.split(dt.filename)[-1])[0] + '.yaml'

    def generate(self):
        data = self.data
        data['filename'] = self.dt.filename
        data['gcc_include'] = self.dt.gcc_include
        data['gcc_define'] = self.dt.gcc_define
        data['dts_version'] = self.dt.dts_version
        data['nodes'] = {}
        root_node = self.dt.nodes_by_name.get('/', None)
        if root_node is not None:
            data['nodes'][0] = self.dictify_node(root_node)
        for _, node in self.dt.nodes_by_ref.items():
            data['nodes'][len(data['nodes'])] = self.dictify_node(node)
        self.data.update(data)

    def dictify_node(self, dtnode: Node):
        data = {t: n for t, n in dtnode.names.items() if n is not None}
        if len(dtnode.dtc['include']) > 0:
            data['dtc_include'] = dtnode.dtc['include']
        if len(dtnode.dtc['delete-node']) > 0:
            data['dtc_delete_node'] = dtnode.dtc['delete-node']
        if len(dtnode.dtc['delete-property']) > 0:
            data['dtc_delete_property'] = dtnode.dtc['delete-property']
        data['properties'] = dict(dtnode.property_map)
        if len(dtnode.children) > 0:
            data['children'] = {}
            for i, child in enumerate(dtnode.children):
                data['children'][i] = self.dictify_node(child)
        return data

    def to_yaml(self, filename=None):
        if filename is None:
            if self.yaml_name in [None, '.yaml']:
                self.yaml_name = 'exported.yaml'
        else:
            self.yaml_name = filename
        with open(self.yaml_name, 'w+') as fp:
            yaml.dump(self.data, fp, default_flow_style=False)
