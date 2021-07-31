from pyDtsTool import DeviceTree, Node

vert = '\u2502'
tee = '\u251c'
end = '\u2514'
horiz = '\u2500'


def add_child_to_tree(child: Node, depth: int, pre=' '):
    output = child.nodename
    if child.reg != None:
        output += '@' + child.nodename
    for i, c in enumerate(child.children):
        output += '\n' + pre
        if i == len(child.children)-1:
            output += '\t' + end
            output += add_child_to_tree(c, depth + 1, pre+'\t ')
        else:
            output += '\t' + tee
            output += add_child_to_tree(c, depth + 1, pre+'\t'+vert)
    return output


def treegraph(dt: DeviceTree):
    root = dt.nodes_by_name['/']
    output = '/\n'
    depth = 0
    for i, child in enumerate(root.children):
        if i == len(root.children)-1:
            output += end
            output += add_child_to_tree(child, depth)
        else:
            output += tee
            output += add_child_to_tree(child, depth, vert)
        output += '\n'
    return output
