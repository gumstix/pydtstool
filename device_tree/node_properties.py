import typing


def tuple_to_string(tup: typing.Tuple):
    string = ' '
    for t in tup:
        string += '{} '.format(t)
    return string


class BaseNodeProperty(object):
    property_name: str
    soft_tabs = True
    tab_size = 4

    def __init__(self, name):
        self.property_name = name

    def __str__(self):
        raise NotImplementedError('Base node not printable')

    def type_match(self, value):
        raise NotImplementedError('Base node has no type')

    @property
    def tab(self):
        if self.soft_tabs:
            return ' ' * self.tab_size
        else:
            return '\t'


class BoolNodeProperty(BaseNodeProperty):
    def __str__(self):
        return self.property_name + ';'

    def print(self, indent=0):
        return (self.tab * indent) + self.property_name + ';'

    def type_match(self, value):
        if isinstance(value, bool):
            return True
        return False


class PairNodePorperty(BaseNodeProperty):
    property_value: typing.Any

    def __init__(self, name, value):
        super(PairNodePorperty, self).__init__(name)
        self.property_value = value

    def __str__(self):
        raise NotImplementedError('Non-type property')

    def print(self, indent: int):
        return (self.tab * indent) + str(self)

    def type_match(self, value) -> bool:
        return isinstance(value, type(self.property_value))


class StrNodeProperty(PairNodePorperty):
    property_value: typing.AnyStr

    def __str__(self):
        return '{} = "{}";'.format(self.property_name,
                                   self.property_value)


class IntNodeProperty(PairNodePorperty):
    property_value: int

    def __str__(self):
        return '{} = <{}>;'.format(self.property_name, hex(self.property_value))


class TupleNodeProperty(PairNodePorperty):
    property_value: typing.Tuple

    def __init__(self, name, value):
        super(TupleNodeProperty, self).__init__(name)
        self.property_value = value

    def __str__(self):
        return '{} = <{}>;'.format(self.property_name, tuple_to_string(self.property_value))


class ListNodeProperty(BaseNodeProperty):
    property_value: typing.List[typing.Any]

    def __init__(self, name, value):
        super(ListNodeProperty, self).__init__(name)
        self.property_value = value
        self.len = len(value)

    def __str__(self):
        raise NotImplementedError('Untyped list property')

    def print(self, indent=0):
        return self.__str__()

    def type_match(self, value):
        if isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], type(self.property_value[0])):
                return True
        return False


class TupleListNodeProperty(ListNodeProperty):
    property_value: typing.List[typing.Tuple]

    def __str__(self):
        tuple_strs = [tuple_to_string(t) for t in self.property_value]
        return '{} = <{}>;'.format(self.property_name, '>, <'.join(tuple_strs))

    def print(self, indent=0):
        ret_str = (self.tab * indent) + '{} =\n'.format(self.property_name)
        indent += 1
        for val in self.property_value[:-1]:
            ret_str += (self.tab * indent) + '<{}>,\n'.format(tuple_to_string(val))
        ret_str += (self.tab * indent) + '<{}>;'.format(tuple_to_string(self.property_value[-1]))
        return ret_str


class IntListNodeProperty(ListNodeProperty):
    property_value: typing.List[int]

    def __str__(self):
        return '{} = < {} >;'.format(self.property_name, ' '.join(self.property_value))

    def print(self, indent=0):
        return (self.tab * indent) + self.__str__()

    def print_alt(self, indent=0):
        ret_str = (self.tab * indent) + '{} =\n'.format(self.property_name)
        indent += 1
        for v in self.property_value[:-1]:
            ret_str += (self.tab * indent) + '<{}>,\n'.format(v)
        ret_str += (self.tab * indent) + '<{}>;'.format(self.property_value[-1])
        return ret_str


class StrListNodeProperty(ListNodeProperty):
    property_value: typing.List[typing.AnyStr]

    def __str__(self):
        return '{} = "{}";'.format(self.property_name, '", "'.join(self.property_value))

    def print(self, indent=0):
        ret_str = (self.tab * indent) + '{} =\n'.format(self.property_name)
        indent += 1
        for v in self.property_value[:-1]:
            ret_str += (self.tab * indent) + '"{}",\n'.format(v)
        ret_str += (self.tab * indent) + '"{}";'.format(self.property_value[-1])


def new_node_property(name, value=None, default_type=bool) -> BaseNodeProperty:
    if value is not None:
        valtype = str(type(value))
    else:
        valtype = str(default_type)
    if valtype == str(bool):
        return BoolNodeProperty(name)
    if valtype == str(int):
        return IntNodeProperty(name, value)
    if valtype == str(str):
        return StrNodeProperty(name, value)
    if valtype == str(tuple):
        return TupleNodeProperty(name, value)
    if valtype == str(list):
        if len(value) == 0:
            raise ValueError('Zero-length list property')
        subtype = str(type(value[0]))
        if subtype == str(int):
            return IntListNodeProperty(name, value)
        if subtype == str(str):
            return StrListNodeProperty(name, value)
        if subtype == str(tuple):
            return TupleListNodeProperty(name, value)
    raise TypeError('Invalid node property type')
