from typing import Union, List, Dict
from .node_properties import new_node_property, BaseNodeProperty


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
                            handle=None,
                            ref=None):
        if nodename == handle == ref and ref is None:
            raise NodeSignatureError('No signature provided')
        if nodename is not None and ref is not None:
            raise NodeSignatureError('Ambiguous signature: &{}, {}'.format(ref, nodename))
        if nodename is not None:
            if nodename.strip() == '':
                raise NodeSignatureError('Blank-string signature detected')
        if ref is not None:
            if ref.strip() == '':
                raise NodeSignatureError('Blank-string signature detected')
        if nodename is None and handle is not None:
            raise NodeSignatureError('Handle {} not associated with nodename')

    def __str__(self):
        raise NotImplementedError('BaseNode cannot be printed')


class Node(BaseNode):
    handle: Union[str, None]
    ref: Union[str, None]
    _properties: List[BaseNodeProperty]
    parent: BaseNode
    reg: Union[int, None]
    dtc: Dict[str, str]

    def __init__(self,
                 parent=None,
                 nodename=None,
                 handle=None,
                 ref=None,
                 reg=None):
        self._validate_signature(nodename, handle, ref)
        if parent is not None and not isinstance(parent, Node):
            raise TypeError('Bad parent: {}'.format(type(parent)))
        self.nodename = nodename
        self.handle = handle
        self.ref = ref
        self._properties = [new_node_property('status', 'okay')]
        self.reg = reg
        if reg is not None:
            self._properties.append(new_node_property('reg', reg))
        self.parent = parent
        if parent is not None:
            parent.children.append(self)
        self.children = []
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
    def properties(self):
        return self._properties

    @property
    def signature(self):
        sig  = ''
        if self.ref is not None:
            sig += '&' + self.ref
        else:
            if self.handle is not None:
                sig += self.handle + ': '
            sig += self.nodename
            if self.reg is not None:
                sig += '@' + hex(self.reg)[2:]
        return sig

    def set_property(self, name, value=True):
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
        nodestr = self.signature + ' {\n'
        for p in self.properties:
            nodestr += p.print(1) + '\n'
        nodestr += '};'
        return nodestr

    def print(self, indent=0):
        nodestr = (self.tab * indent) + self.signature + ' {\n'
        indent += 1
        for p in self.properties:
            nodestr += p.print(indent) + '\n'
        for c in self.children:
            nodestr += c.print(indent) + '\n'
        indent -= 1
        nodestr += (self.tab * indent) + '};'
        return nodestr
