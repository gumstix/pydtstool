###################################################
#                    pyDtsTool                    #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################

import re
import typing

from ..common import sig_tuple

gcc_match = re.compile(r'(?=\s*)((?P<inc>#include[ \t]*)([\"<])|'
                       r'(?P<def>#define))'
                       r'(\s*(?P<val>[^\v\"]*))')

node_match = re.compile(r'(((?P<sig>(?=\s)?[&\/]?[\w\-_: \t@,]*)[^&]{)|'
                        r'(?P<end>};))'
                        r'(?P<extra>[^\v]*)?')

comment_match = re.compile(r'^([ \t]*(?=\S))?'
                           r'(?P<linker>#[^id][0-9]*\s*\")|'
                           r'((?P<head>((?<!//))?(?(4)|.*(?=//|/\*)))'
                           r'((?P<comment>//)|'
                           r'(?P<block>/\*)))?'
                           r'((?P<mid>.*(?=\*/))'
                           r'(?P<blockend>\*/))?'
                           r'(?P<tail>[^\v]*)')

line_match = re.compile(r'^((/(?P<dtc>(?<=/)[\w\-]*)/|'
                        r'(?P<head>[,\w_\-]*)\s*)'
                        r'(?P<eq>=))'
                        r'(?P<tail>.*)|'
                        r'(^(?P<bool>\S*(?=;)))')

prop_match = re.compile(r'((\"(?P<str>[^\"\v]*)\")|(<(?P<tup>[^>]*)>)|(?P<macro>__\w*__))(?P<comma>,)?')


def remove_comments(data) -> typing.List[str]:

    block_comment = False
    for i, line in enumerate(data):
        groups = comment_match.search(line)
        if groups is None:
            valid = block_comment
        elif groups.group('linker') is not None:
            data[i] = ''
            continue
        else:
            valid = next((True for n, m in groups.groupdict().items() if n in ['comment', 'block', 'blockend'] and
                          m is not None), block_comment)
        if valid:
            if groups is not None:
                indent = groups.group(1)
                if indent is None:
                    indent = ''
                groups = {name: string for name, string in groups.groupdict().items() if string is not None}
            else:
                indent = ''
                groups = {}
            if 'block' in groups.keys():
                if 'blockend' in groups.keys() and 'mid' in groups.keys():
                    del groups['mid']
                elif 'tail' in groups.keys():
                    del groups['tail']
                    block_comment = True
            elif block_comment:
                if 'head' in groups.keys():
                    del groups['head']
                if 'blockend' in groups.keys():
                    block_comment = False
                elif 'tail' in groups.keys():
                    del groups['tail']
            if 'comment' in groups.keys() and 'tail' in groups.keys():
                del groups['tail']
            refit = indent
            refit += groups.get('head', '')
            refit += groups.get('mid', '')
            refit += groups.get('tail', '')
            data[i] = refit
    i = 0
    datalen = len(data)
    while i < datalen:
        if data[i].strip() == '':
            del data[i]
            i = 0
            datalen = len(data)
        else:
            i += 1
    return data


def collect_subnodes(data: typing.List[str]):
    node_lines = []
    subnode_lines = {}
    i = 0
    datalen = len(data)
    while len(data) > 0 and i < datalen:
        line = data[i].strip()
        m = node_match.search(line)
        if m is not None:
            md = {name: value for name, value in m.groupdict().items() if value is not None}
            if 'sig' in md.keys():
                if md.get('extra', '').strip() is not '':
                    data[i] = md['extra']
                else:
                    i += 1
                try:
                    data, new_subnode = collect_subnodes(data[i:])
                    subnode_lines[md['sig']] = merge_dict(subnode_lines.get(md['sig'], {}), new_subnode)
                except TypeError as e:
                    print(e)
                    raise e
                datalen = len(data)
                i = 0
            if 'end' in md.keys():
                return data[i + 1:], {'self': node_lines, 'subnodes': subnode_lines}
        else:
            node_lines.append(line)
            i += 1
    return [], {'self': node_lines, 'subnodes': subnode_lines}


def parse_property(prop_val: str):
    temp_val = prop_val.strip()
    temp_list = []
    gd = {'comma': ''}
    while gd['comma'] is not None:
        groups = prop_match.search(temp_val)
        if groups is not None:
            temp_list.append(groups.group(1))
            gd = groups.groupdict()
            if gd['comma'] is not None:
                temp_val = temp_val[len(groups.group(1)):].lstrip(' ,')
        else:
            # noinspection PyTypeChecker
            gd['comma'] = None
    if len(temp_list) > 1:
        ret_val = []
        for item in temp_list:
            groups = prop_match.search(item)
            if groups is not None:
                gd = groups.groupdict()
                if gd.get('tup', None) is not None:
                    ret_val.append(tuple(gd['tup'].split()))
                elif gd.get('str', None) is not None:
                    ret_val.append(gd['str'])
                else:
                    ret_val.append(gd.get('macro', None))
    else:
        if gd.get('tup', None) is not None:
            ret_val = tuple(gd['tup'].split())
        elif gd.get('str', None) is not None:
            ret_val = gd['str']
        else:
            ret_val = gd.get('macro', None)
    return ret_val


def merge_dict(d1, d2):
    merged = {}
    for key in d1.keys():
        if key in d2.keys():
            if isinstance(d1[key], dict):
                merged[key] = merge_dict(d1[key], d2[key])
            elif isinstance(d1[key], list):
                merged[key] = d1[key] + d2[key]
            elif isinstance(d1[key], str):
                merged[key] = '{} | {}'.format(d1[key], d2[key])
            else:
                merged[key] = d2[key]
        else:
            merged[key] = d1[key]
    for key in d2.keys():
        if key not in d1.keys():
            merged[key] = d2[key]
    return merged
