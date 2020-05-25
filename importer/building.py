from device_tree import Node


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
