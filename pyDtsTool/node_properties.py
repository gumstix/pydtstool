###################################################
#                    pyDtsTool                    #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################

from typing import Union, List, Dict, Any, AnyStr, Tuple, Iterable
import abc


def tuple_to_string(tup: Tuple) -> str:
    """Standardized assembly of tuple strings for DTS files

    :param tup: typing.Tuple
    :return: str
    """
    string = ' '.join(tup)
    return string


class NodeProperty(metaclass=abc.ABCMeta):
    property_name: str
    soft_tabs: bool= True
    tab_size: int= 4

    def __init__(self, name: str):
        """Node property base class constructor
        
        :param name: str
        """
        self.property_name = name
        self.value = None

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError('Base property not printable')

    @abc.abstractmethod
    def type_match(self, value):
        raise NotImplementedError('Base property has no type')

    @abc.abstractmethod
    def _get(self):
        raise NotImplementedError('No getter for Base property')

    @property
    def classname(self):
        return self.__class__.__name__

    @property
    def tab(self) -> str:
        if self.soft_tabs:
            return ' ' * self.tab_size
        else:
            return '\t'

    @abc.abstractmethod
    def print(self, indent: int):
        raise NotImplementedError

    @abc.abstractmethod
    def first(self):
        raise NotImplementedError


class BoolNodeProperty(NodeProperty):
    def __str__(self) -> str:
        return self.property_name + ';'

    def print(self, indent: int=0) -> str:
        return (self.tab * indent) + self.property_name + ';'

    def _get(self):
        return self.property_name, True

    def type_match(self, value: Any) -> bool:
        if isinstance(value, bool):
            return True
        return False

    @property
    def property_value(self) -> bool:
        return True

    def first(self) -> bool:
        return self.property_value


class PairNodePorperty(NodeProperty, metaclass=abc.ABCMeta):
    property_value: Any

    def __init__(self, name: str, value: Any):
        super(PairNodePorperty, self).__init__(name)
        self.property_value = value

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError('Non-type property')

    def _get(self):
        return self.property_name, self.property_value

    def print(self, indent: int):
        return (self.tab * indent) + str(self)

    def type_match(self, value) -> bool:
        return isinstance(value, type(self.property_value))

    def first(self)-> Any:
        return self.property_value


class StrNodeProperty(PairNodePorperty):
    property_value: AnyStr

    def __str__(self):
        return '{} = "{}";'.format(self.property_name,
                                   self.property_value)


class IntNodeProperty(PairNodePorperty):
    property_value: int

    def __str__(self):
        return '{} = <{}>;'.format(self.property_name, hex(self.property_value))


class TupleNodeProperty(PairNodePorperty):
    property_value: Tuple

    def __init__(self, name, value):
        super(TupleNodeProperty, self).__init__(name, value)
        self.property_value = value

    def __str__(self):
        return '{} = <{}>;'.format(self.property_name, tuple_to_string(self.property_value))

    def first(self):
        return next(p for p in self.property_value)


class ListNodeProperty(NodeProperty):
    property_value: List[Any]

    def __init__(self, name, value):
        super(ListNodeProperty, self).__init__(name)
        self.property_value = value
        self.len = len(value)

    def __str__(self):
        raise NotImplementedError('Untyped list property')

    def _get(self):
        return self.property_name, self.property_value

    def print(self, indent=0):
        return (self.tab * indent) + self.__str__()

    def type_match(self, value):
        if isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], type(self.property_value[0])):
                return True
        return False

    def first(self):
        return self.property_value[0]


class TupleListNodeProperty(ListNodeProperty):
    property_value: List[Tuple]

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
    property_value: Iterable[int]

    def __str__(self):
        return '{} = <{}>;'.format(self.property_name, ' '.join(self.property_value))

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
    property_value: List[AnyStr]

    def __str__(self):
        return '{} = "{}";'.format(self.property_name, '", "'.join(self.property_value))

    def print(self, indent=0):
        ret_str = (self.tab * indent) + '{} =\n'.format(self.property_name)
        indent += 1
        for v in self.property_value[:-1]:
            ret_str += (self.tab * indent) + '"{}",\n'.format(v)
        ret_str += (self.tab * indent) + '"{}";'.format(self.property_value[-1])
        return ret_str


def new_node_property(name: str, value: Any=None, default_type: type=bool) -> NodeProperty:
    """Node property factory:  Determines NodeProperty subclass based on assigned value."""
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
