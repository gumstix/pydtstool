###################################################
#                    PyDeviceTree                 #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################
# !/bin/env python3
import os

the_copyright = ['###################################################\n',
                 '#                    PyDeviceTree                 #\n',
                 '#           Copyright 2021, Altium, Inc.          #\n',
                 '#  Author: Keith Lee                              #\n',
                 '#  E-Mail: keith.lee@altium.com                   #\n',
                 '###################################################\n']


def recursive_copyright(file):
    if os.path.isfile(file):
        if os.path.splitext(file)[-1] == '.py':
            with open(file, 'r') as fp:
                temp = fp.readlines()
            if temp[:6] != the_copyright:
                if temp[:2] != the_copyright[:2]:
                    temp = the_copyright + temp
                else:
                    temp = the_copyright + temp[6:]
                with open(file, 'w') as fp:
                    fp.writelines(temp)
    elif os.path.isdir(file):
        for f in os.listdir(file):
            recursive_copyright(os.path.join(file, f))


for f in os.listdir(os.curdir):
    recursive_copyright(f)
