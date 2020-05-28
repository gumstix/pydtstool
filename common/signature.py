from collections import namedtuple
import re

sig_match = re.compile(r'(?P<ref>(?<=&)[\w_]*)|'
                       r'(((?P<handle>[\w_]*(?=:))?(:\s*)?'
                       r'(?P<nodename>(?<!@)[\w_\-/]+)).?'
                       r'(?P<reg>(?<=@)\S*)?)')

sig_tuple = (namedtuple('sig_tuple', ['nodename', 'handle', 'ref', 'reg']))


def make_sig_tuple(signature):
    groups = sig_match.search(signature)
    if groups is None:
        raise ValueError('Signature "{}" not valid'.format(signature))
    sig_dict = groups.groupdict()
    sig = sig_tuple(sig_dict.get('nodename', None),
                    sig_dict.get('handle', None),
                    sig_dict.get('ref', None),
                    sig_dict.get('reg', None))
    return sig
