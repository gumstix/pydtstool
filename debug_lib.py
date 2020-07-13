#!/usr/bin/env python3

import argparse
import yaml
from importer import DtImporter
from dictify import Dictifier, UnDictifier

from device_tree import DeviceTree

in_file = '/home/keith/git/dts-geppetto/devicetree-jetson_nano.dts'
out_file = './exported.dts'
yaml_in_file = './example.yaml'
yaml_out_file = './exported.yaml'


def main():
    """Allows user to run library functions for debugging purposes"""
    parser = argparse.ArgumentParser('debug_lib.py')
    parser.add_argument('--import_dts', '-i', nargs='?', help='import DTS file', const=in_file, default=None)
    parser.add_argument('--export_dts', '-x', nargs='?', help='export to DTS file', const=out_file, default=None)
    parser.add_argument('--undictify', '-u', nargs='?', help='UnDictify DTS data', const=yaml_in_file, default=None)
    parser.add_argument('--dictify', '-d', nargs='?', help='Dictify DTS abstraction', const=yaml_out_file, default=None)
    args = parser.parse_args()
    dt = None
    if args.import_dts is not None:
        dti = DtImporter(args.import_dts)
        dti.parse()
        dti.build()
        dt = dti.dt
    if args.undictify is not None:
        undict = UnDictifier.from_yaml(args.undictify)
        undict.populate()
        dt = undict.dt
    if args.dictify is not None and dt is not None:
        d = Dictifier(dt)
        d.generate()
        d.to_yaml(args.dictify)
    if dt is not None:
        print(dt)
        if args.export_dts is not None:
            with open(args.export_dts, 'w+') as fp:
                fp.write(str(dt))
    return


if __name__ == '__main__':
    main()
