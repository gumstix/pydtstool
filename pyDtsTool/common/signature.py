###################################################
#                    pyDtsTool                    #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################
from collections import namedtuple
import re

sig_match = re.compile(r'(?P<ref>(?<=&)[\w_]*)|'
                       r'(((?P<handle>([\w_0-9]*:\s)*)?'
                       r'(?P<nodename>(?<!@)[\w_\-/,]+)).?'
                       r'(?P<reg>(?<=@)\S*)?)')

sig_tuple = (namedtuple('sig_tuple', ['nodename', 'handles', 'ref', 'reg']))


def make_sig_tuple(signature):
    groups = sig_match.search(signature)
    if groups is None:
        raise ValueError('Signature "{}" not valid'.format(signature))
    sig_dict = groups.groupdict()
    handles = sig_dict.get('handle', None)

    if handles is not None:
        handles = handles.split(': ')[:-1]
    else:
        handles = []
    sig = sig_tuple(sig_dict.get('nodename', None),
                    handles,
                    sig_dict.get('ref', None),
                    sig_dict.get('reg', None))
    return sig
