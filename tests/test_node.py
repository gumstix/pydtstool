###################################################
#                    PyDeviceTree                 #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################
import unittest

from dtsgen.node import Node, NodeSignatureError
from dtsgen.node_properties import *
from tests import DtTestCase


# noinspection PyUnusedLocal
class TestNode(DtTestCase):
    dummy_node = Node(nodename='dummy')

    def all_node_properties(self, node):
        for p in node.properties:
            self.assertIsInstance(p, BaseNodeProperty)

    def test_simple_generate_nodename(self):
        n = Node(nodename='test')
        self.assertIsInstance(n, Node)
        self.assertEqual(n.nodename, 'test')
        self.assertIsNone(n.handle)
        self.assertIsNone(n.ref)
        self.assertIsNone(n.parent)
        self.assertIsInstance(n.properties, list)
        self.all_node_properties(n)

    def test_simple_generate_nodename_handle(self):
        n = Node(nodename='test', handle='test')
        self.assertIsInstance(n, Node)
        self.assertEqual(n.nodename, 'test')
        self.assertEqual(n.handle, 'test')
        self.assertIsNone(n.ref)
        self.assertIsNone(n.parent)
        self.assertIsInstance(n.properties, list)
        self.all_node_properties(n)

    def test_simple_generate_ref(self):
        n = Node(ref='test')
        self.assertIsInstance(n, Node)
        self.assertEqual(n.ref, 'test')
        self.assertIsNone(n.handle)
        self.assertIsNone(n.nodename)
        self.assertIsNone(n.parent)
        self.assertIsInstance(n.properties, list)
        self.all_node_properties(n)

    def test_simple_generate_ref_parent(self):
        n = Node(self.dummy_node, ref='test')
        self.assertEqual(n.parent, self.dummy_node)
        self.all_node_properties(n)

    # noinspection PyUnusedLocal
    def test_generate_fails_signature(self):
        with self.assertRaises(NodeSignatureError):
            n = Node()
        with self.assertRaises(NodeSignatureError):
            n = Node(nodename='test', ref='test')
        with self.assertRaises(NodeSignatureError):
            n = Node(handle='test')

    def test_generate_fails_parent(self):
        with self.assertRaises(TypeError):
            n = Node('', 'test')

    def test_int_property(self):
        n = Node(nodename='test')
        n.set_property('integer', 1)
        self.assertIn('integer', n.property_index.keys())
        self.assertEqual(n.property_index['integer'].property_value, 1)
        n.set_property('integer', 2)
        instances = 0
        for key in n.property_index.keys():
            if key == 'integer':
                instances += 1
        self.assertEqual(instances, 1)
        self.assertEqual(n.property_index['integer'].property_value, 2)
        self.assertEqual(str(n.property_index['integer']), 'integer = <0x2>;')
        self.all_node_properties(n)

    def test_int_list_property(self):
        n = Node(nodename='test')
        n.set_property('int_list', [1, 2, 3])
        self.assertIsInstance(n.property_index['int_list'], IntListNodeProperty)
        self.assertEqual(n.property_index['int_list'].property_value, [1, 2, 3])
        n.set_property('int_append', 1)
        self.assertIsInstance(n.property_index['int_append'], IntNodeProperty)
        n.extend_property_list('int_append', [2, 3])
        self.assertIsInstance(n.property_index['int_append'], IntListNodeProperty)

    def test_str_property(self):
        n = Node(nodename='test')
        n.set_property('str', 'test')
        self.assertIn('str', n.property_index.keys())
        self.assertEqual(n.property_index['str'].property_value, 'test')
        n.set_property('str', '2')
        instances = 0
        for key in n.property_index.keys():
            if key == 'str':
                instances += 1
        self.assertEqual(instances, 1)
        self.assertEqual(n.property_index['str'].property_value, '2')
        self.assertEqual(str(n.property_index['str']), 'str = "2";')
        self.all_node_properties(n)

    def test_str_list_property(self):
        n = Node(nodename='test')
        values = ['test1', 'test2', 'test3']
        n.set_property('str', values)
        self.assertIsInstance(n.property_index['str'], StrListNodeProperty)
        for i in range(0, len(values)):
            self.assertEqual(values[i], n.property_index['str'].property_value[i])
        n.set_property('str_append', 'test4')
        self.assertIsInstance(n.property_index['str_append'], StrNodeProperty)
        n.extend_property_list('str_append', ['test5'])
        self.assertIsInstance(n.property_index['str_append'], StrListNodeProperty)

