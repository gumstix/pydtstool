###################################################
#                    pyDtsTool                    #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################
from typing import Union, List, Dict, Any

from .node_properties import *


class NodeSignatureError(Exception):
    def __init__(self, msg: str):
        super(NodeSignatureError, self).__init__()
        self.message = msg

    def __str__(self):
        return 'Node Signature Error: {}'.format(self.message)


class BaseNode(object):
    children: List
    nodename: Union[str, None]
    soft_tabs = True
    tab_size = 4

    @property
    def tab(self):
        if self.soft_tabs:
            return ' ' * self.tab_size
        else:
            return '\t'

    @staticmethod
    def _validate_signature(nodename=None,
                            handles=[],
                            ref=None):
        if nodename == ref and ref is None and len(handles) == 0:
            raise NodeSignatureError('No signature provided')
        if nodename is not None and ref is not None:
            raise NodeSignatureError('Ambiguous signature: &{}, {}'.format(ref, nodename))
        if nodename is not None:
            if nodename.strip() == '':
                raise NodeSignatureError('Blank-string signature detected')
        if ref is not None:
            if ref.strip() == '':
                raise NodeSignatureError('Blank-string signature detected')
        if nodename is None and len(handles) > 0:
            raise NodeSignatureError('Handle {} not associated with nodename'.format(handles))

    def __str__(self):
        raise NotImplementedError('BaseNode cannot be printed')


class Node(BaseNode):
    def __init__(self,
                 parent=None,
                 nodename=None,
                 handles=[],
                 ref=None,
                 reg=None):
        self.handles = []
        self.ref = None
        self._properties = []
        self.parent = None
        self.reg = None
        self.dtc = {}
        self.children = []
        if handles != None:
            if not isinstance(handles, list):
                handles = [handles]
        else:
            handles = []
        self._validate_signature(nodename, handles, ref)
        if parent is not None and not isinstance(parent, Node):
            raise TypeError('Bad parent: {}'.format(type(parent)))
        self.nodename = nodename
        self.ref = ref
        self.handles = handles
        try:
            self.reg = int(reg, 16)
        except TypeError:
            self.reg = reg
        except ValueError:
            self.reg = reg
        if self.reg is not None:
            self._properties.append(new_node_property('reg', self.reg))
        self.parent = parent
        if parent is not None:
            parent.children.append(self)
        self.dtc = {'include': [], 'delete-node': [], 'delete-property': []}

    def set_parent(self, parent):
        if self.parent is not None:
            self.parent.children.remove(self)
        self.parent = parent
        parent.children.append(self)

    @property
    def property_index(self):
        return {p.property_name: p for p in self._properties}

    @property
    def property_map(self):
        for p in self._properties:
            yield p._get()

    @property
    def properties(self):
        return self._properties

    @property
    def signature(self):
        sig = ''
        if self.ref is not None:
            sig += '&' + self.ref
        else:
            if len(self.handles) > 0:
                sig += ': '.join(self.handles) + ': '
            sig += self.nodename
            if isinstance(self.reg, int):
                sig += '@' + hex(self.reg)[2:]
            elif self.reg is not None:
                sig += '@' + str(self.reg)
        return sig

    @property
    def names(self):
        sig = {'nodename': self.nodename,
               'handles': self.handles,
               'ref': self.ref,
               'reg': self.reg}
        return sig

    @property
    def pathname(self):
        path = self.nodename
        if self.reg is not None:
            if isinstance(self.reg, int):
                path += '@' + hex(self.reg)[2:]
            else:
                path += '@' + str(self.reg)
        return path


    @property
    def path(self):
        n = self
        path = ''
        while n is not None:
            if n.pathname == None:
                pathname = n.signature
            else:
                pathname = n.pathname
            path = pathname + '/' + path
            n = n.parent
        path = path.replace(' ', '')
        return path

    def set_property(self, name, value=None):
        if name not in self.property_index.keys():
            self._properties.append(new_node_property(name, value))
        else:
            p = self.property_index[name]
            if isinstance(value, bool):
                if value is False:
                    self._properties.remove(p)
                return
            if p.type_match(value):
                p.property_value = value
            else:
                self._properties.remove(p)
                self._properties.append(new_node_property(name, value))

    def unset_property(self, name):
        p = self.property_index.get(name, None)
        if p is not None:
            self._properties.remove(p)

    def extend_property_list(self, name: str, value_list: list):
        if name not in self.property_index.keys():
            self._properties.append(new_node_property(name, value_list))
        elif self.property_index[name].type_match(value_list):
            self.property_index[name].property_value.extend(value_list)
        elif self.property_index[name].type_match(value_list[0]):
            value_list.append(self.property_index[name].property_value)
            self.set_property(name, value_list)
        else:
            raise ValueError('data type does not match variable')

    def __str__(self):
        return self.print()

    def print(self, indent=0):
        nodestr = '\n'
        for i in self.dtc['include']:
            nodestr += (self.tab * indent) + '/include/ "{}"\n'.format(i)
            if self.dtc['include'].index(i) == len(self.dtc['include']) - 1:
                nodestr += '\n'
        nodestr += (self.tab * indent) + self.signature + ' {\n'
        indent += 1
        for key, value in self.dtc.items():
            if key != 'include' and len(value) > 0:
                for v in value:
                    nodestr += (self.tab * indent) + '/{}/ {};\n'.format(key, v)
        for p in self.properties:
            nodestr += p.print(indent) + '\n'
        for c in self.children:
            nodestr += c.print(indent) + '\n'
        indent -= 1
        nodestr += (self.tab * indent) + '};'
        return nodestr

    def join(self, next_node):
        if len(next_node.handles) > 0:
            for h in next_node.handles:
                if h not in self.handles:
                    self.handles.append(h)
        for prop in next_node.properties:
            self.set_property(prop.property_name, prop.property_value)
        for child in next_node.children:
            if child not in self.children:
                self.children.append(child)
                child.parent = self
        next_node.children = []
