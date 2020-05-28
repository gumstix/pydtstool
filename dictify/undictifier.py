import yaml
import os
from device_tree import DeviceTree, Node
from common import make_sig_tuple, sig_tuple


class UnDictifier(object):
    def __init__(self, dt: DeviceTree, dt_dict: dict):
        self.data = dt_dict
        self.dt = dt

    @classmethod
    def from_yaml(cls, filename: str):
        if not os.path.isfile(filename):
            raise FileNotFoundError('No such yaml file')
        with open(filename, 'r') as fp:
            data = yaml.load(fp)
        dt_file = os.path.splitext(os.path.split(filename)[-1])[0] + '.dts'
        dt = DeviceTree.new_devicetree(dt_file)
        return UnDictifier(dt, data)

    def populate(self):
        self.dt.dts_version = self.data.get('dts_version', 1)
        self.dt.gcc_include = self.data.get('gcc_include', [])
        if not isinstance(self.dt.gcc_include, list):
            self.gcc_include = [self.gcc_include]
        self.dt.gcc_define = self.data.get('gcc_define', {})
        self.dt.filename = self.data.get('filename', 'generated.dts')
        nodes = self.data.get('nodes', {})
        for i, node_data in nodes.items():
            if 'signature' in node_data.keys():
                sig = make_sig_tuple(node_data['signature'])
            else:
                sig = sig_tuple(node_data.get('nodename', None),
                                node_data.get('handle', None),
                                node_data.get('ref', None),
                                node_data.get('reg', None))
            dtnode = self.dt.get_node_from_tuple(sig)
            if dtnode is None:
                _, dtnode = self.dt.new_node(None, *sig)
            self.undictify_node(dtnode, node_data)

    def undictify_node(self, dtnode: Node, node_data: dict):
        dtnode.dtc['include'] = node_data.get('dtc_include', [])
        dtnode.dtc['delete-property'] = node_data.get('dtc_delete_property', [])
        dtnode.dtc['delete-node'] = node_data.get('dtc_delete_node', [])
        for key, val in dtnode.dtc.items():
            if not isinstance(val, list) and val is not None:
               dtnode.dtc[key] = [val]
        dtnode.set_property('status', node_data.get('status', 'okay'))
        for prop_name, prop_val in node_data.get('properties', {}).items():
            dtnode.set_property(prop_name, prop_val)
        for _, child in node_data.get('children', {}).items():
            if 'signature' in child.keys():
                sig = make_sig_tuple(child['signature'])
            else:
                sig = sig_tuple(child.get('nodename', None),
                                child.get('handle', None),
                                child.get('ref', None),
                                child.get('reg', None))
            _, dtchild = self.dt.new_node(dtnode, *sig)
            self.undictify_node(dtchild, child)
