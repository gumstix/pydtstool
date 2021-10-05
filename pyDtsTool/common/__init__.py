###################################################
#                    pyDtsTool                 #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################
from .signature import make_sig_tuple, sig_tuple

def tuple_representer(dumper, data):
    output = '<'
    output += ' '.join(list(data))
    output += '>'
    return dumper.represent_str(output)
