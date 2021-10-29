#!/usr/bin/python3

###################################################
#                    pyDtsTool                    #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################

import argparse
from sys import argv
import os
from pyDtsTool import DtImporter, Comparator
from pyDtsTool.graph.node_graph_nx import DtGraph
from pyDtsTool.dictify import Dictifier, UnDictifier

def check(r):
    if r.lower() in ['q', 'quit', 'exit']:
        print('Exiting...')
        exit(0)

def interactive():
    namespace = []
    print('           PyDtsTool command-line interface:\n'
          '=======================================================\n'
          '<type (q)uit or exit at any time to leave>\n')
    r = input('  Compare two DTS files(y/N)? ')
    check(r)
    if r != '' and r.lower().startswith('y'):
        namespace.append('-c')
        r = ''
        while r == '':
            r = input('    Enter first DTS file: ')
            check(r)
            if not os.path.isfile(r):
                print('Error Invalid filename.')
                r = ''
        namespace.append(r)
        while r == '':
            r = input('    Enter second DTS file: ')
            check(r)
            if not os.path.isfile(r):
                print('Error Invalid filename.')
                r = ''
        namespace.append(r)
        r = input('    Enter output YAML file (default: stdout): ')
        check(r)
        if r is not '':
            if not (r.endswith('.yaml') or r.endswith('.yml')):
                r += '.yaml'
            namespace.append(r)
        return namespace
    r = input('  Import DTS(Y/n)? ')
    imp = False
    check(r)
    if r.lower() == '' or r.lower().startswith('y'):
        namespace.append('-i')
        r = ''
        while r == '':
            r = input('    Enter file to import: ')
            check(r)
            if not os.path.isfile(r):
                print('Error: Invalid filename.')
                r = ''
        namespace.append(r)
        imp = True
    if r is not '':
        r = input('  Export DTS(y,N)? ')
        check(r)
        if r.lower() != '' and r.lower()[0] == 'y':
            namespace.append('-x')
            r = ''
            while r == '':
                r = input('    Enter new filename: ')
                check(r)
            if not r.endswith('.dts'):
                r += '.dts'
            namespace.append(r)
    if not imp:
        r = input('  Undictify YAMLized device tree(Y/n)? ')
        check(r)
        if r == '' or r.lower().startswith('y'):
            namespace.append('-u')
            r = ''
            while r == '':
                r = input('    Enter YAML file name: ')
                check(r)
                if not os.path.isfile(r):
                    print('Invalid file name.')
                    r = ''
            namespace.append(r)
    if '-i' in namespace or '-u' in namespace:
        r = input('  Dictify Device tree data(y/N)? ')
        check(r)
        if r != '' and r.lower().startswith('y'):
            namespace.append('-d')
            r = ''
            while r == '':
                r = input('    Enter output filename: ')
                check(r)
            if not (r.endswith('.yaml') or r.endswith('.yml')):
                r += '.yaml'
            namespace.append(r)
        r = input('  Merge linked DT nodes(Y/n)? ')
        check(r)
        if r == '' or r.lower().startswith('y'):
            namespace.append('-m')
    print('Running:  ' + ' '.join([__file__] + namespace))
    return namespace


def main():
    parser = argparse.ArgumentParser('pydts_cli.py', description='Command line device tree tool')
    parser.add_argument('--import_dts', '-i',
                        help='import DTS file')
    parser.add_argument('--export_dts', '-x',
                        help='export to DTS file',
                        action='store_const',
                        const='./output.dts')
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
    if len(argv) == 1:
        new_argv = interactive()
        args = parser.parse_args(new_argv)
    else:
        args = parser.parse_args()
    outfile = None
    if len(args.kargs) > 0:
        outfile = args.kargs[0]
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
    if args.export_dts is not None:
        outfile = args.export_dts
        with open(outfile, 'w+') as fp:
            fp.write(str(dt))

    return


if __name__ == '__main__':
    main()