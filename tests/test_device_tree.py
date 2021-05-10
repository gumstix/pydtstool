###################################################
#                    PyDeviceTree                 #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################
import unittest

from dtsgen import DeviceTree
from tests import DtTestCase

filename = 'new.dts'


class TestDeviceTree(DtTestCase):
    def test_generate(self):
        dt = DeviceTree()
        self.assertIsInstance(dt, DeviceTree)
        self.assertIsNone(dt.filename)

    def test_new_device_tree(self):
        dt = DeviceTree.new_devicetree(filename)
        self.assertIsInstance(dt, DeviceTree)
        self.assertEqual(dt.filename, filename)

    def test_new_device_tree_fails(self):
        bad_values = [None, '', 1, [], {}]
        try:
            dt = DeviceTree.new_devicetree()
            self.fail('Generated without filename')
        except Exception as e:
            self.assertIsInstance(e, TypeError)
        for value in bad_values:
            try:
                dt = DeviceTree.new_devicetree(value)
            except Exception as e:
                self.assertIsInstance(e, TypeError)
                continue
