from device_tree import DeviceTree
from importer.importer import DtImporter
file = '/home/keith/git/dts-geppetto/devicetree-jetson_tx2.dts'

def main():
    dti = DtImporter(file)
    dti.parse()
    with open('output.dts', 'w+') as fp:
        fp.write('\n'.join(dti._data))
    for line in dti._data:
        if '//' in line or '/*' in line or '*/' in line:
            print('comment in line {}: {}'.format(dti._data.index(line), line))
    dti.build()
    dti.export('./exported.dts')
    return

if __name__ == '__main__':
    main()