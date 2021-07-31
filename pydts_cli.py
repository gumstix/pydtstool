#!/usr/bin/python3.7

import argparse
from pyDtsTool import DtImporter, Comparator
from pyDtsTool.graph.node_graph_nx import DtGraph
from pyDtsTool.dictify import Dictifier, UnDictifier

def main():
    parser = argparse.ArgumentParser('pydts_cli.py', description='Command line device tree tool')
    parser.add_argument('--import_dts', '-i',
                        nargs=1,
                        help='import DTS file')
    parser.add_argument('--export_dts', '-x',
                        nargs='?',
                        help='export to DTS file',
                        default=None)
    parser.add_argument('--undictify', '-u',
                        nargs=1,
                        help='UnDictify DTS data')
    parser.add_argument('--dictify', '-d',
                        help='Dictify DTS abstraction',
                        nargs='?',
                        default=None)
    parser.add_argument('--graph', '-g',
                        action='store_true',
                        help='Generate Digraph of device tree')
    parser.add_argument('--merge', '-m',
                        action='store_true',
                        help='Join reference and origin nodes')
    parser.add_argument('--compare', '-c',
                        nargs=2,
                        help='Compare 2 DTS files')
    parser.add_argument('kargs', nargs='*')

    args = parser.parse_args()
    outfile = None
    if len(args.kargs) > 0:
        outfile = args.kargs[0]
        print(outfile)
    if args.compare is not None:
        idt1 = DtImporter(args.compare[0])
        idt2 = DtImporter(args.compare[1])
        idt1.parse()
        idt2.parse()
        idt1.build()
        idt2.build()
        idt1.dt.merge()
        idt2.dt.merge()
        comp = Comparator(idt1.dt, idt2.dt)
        comp.get_diff()
        comp.print_output(outfile)
        return 0
    if args.import_dts is not None:
        idt = DtImporter(args.import_dts)
        idt.parse()
        dt = idt.build()
    elif args.undictify is not None:
        idt = UnDictifier.from_yaml(args.undictify)
        idt.populate()
        dt = idt.dt
    else:
        parser.print_help()
    if args.merge:
        dt.merge()
    if args.dictify is not None:
        odt = Dictifier(dt)
        odt.generate()
        odt.to_yaml(args.dictify)
    if args.graph:
        gdt = DtGraph(dt)
        gdt.generate()
    if args.export_dts is not None or len(args.kargs) > 0:
        outfile = set(args.kargs).get(0, args.export_dts)
        with open(outfile, 'w+') as fp:
            fp.write(str(dt))

    return


if __name__ == '__main__':
    main()