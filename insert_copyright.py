#!/bin/env python3
import os

the_copyright = ['###################################################\n',
                '#                    PyDeviceTree                 #\n',
                '#           Copyright 2020, Gumstix, Inc.         #\n',
                '#  Author: Keith Lee                              #\n',
                '#  E-Mail: keith.lee@gumstix.com                  #\n',
                '###################################################\n']

def recursive_copyright(file):
    if os.path.isfile(file):
        if os.path.splitext(file)[-1] == '.py':
            with open(file, 'r') as f:
                temp = f.readlines()
                temp = the_copyright + temp
            with open(file, 'w') as f:
                f.writelines(temp)
    elif os.path.isdir(file):
        for f in os.listdir(file):
            if f is not __file__:
                recursive_copyright(os.path.join(file, f))
            else:
                pass

for f in os.listdir(os.curdir):
    recursive_copyright(f)
