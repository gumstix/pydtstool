import argparse
import yaml
from importer import DtImporter
from dictify import UnDictifier

from device_tree import DeviceTree

in_file = '/home/keith/git/dts-geppetto/devicetree-jetson_tx2.dts'
out_file = './exported.dts'
yaml_in_file = './example.yaml'
yaml_out_file = './exported.yaml'

def main():
    parser = argparse.ArgumentParser('debug_lib.py')
    parser.add_argument('--import_dts', '-i', nargs='?', help='import DTS file', const=in_file, default=None)
    parser.add_argument('--export_dts', '-x', nargs='?', help='export to DTS file', const=out_file, default=None)
    parser.add_argument('--dictify', '-u', nargs='?', help='UnDictify DTS data', const=yaml_in_file, default=None)
    parser.add_argument('--dictify', '-d', nargs='?', help='Dictify DTS abstraction', const=yaml_out_file, default=None)
    args = parser.parse_args()

    if args.import_dts is not None:
        dti = DtImporter(args.import_dts)
        dti.parse()
        dti.build()
        dt = dti.dt
    if args.undictify is not None:
        with open(args.undictify, 'r') as fp:
            data = yaml.load(fp)
        undict = UnDictifier(DeviceTree(), data)
        undict.populate()
        dt = undict.dt
    return


if __name__ == '__main__':
    main()
