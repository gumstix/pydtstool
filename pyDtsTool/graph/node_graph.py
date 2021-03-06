###################################################
#                    pyDtsTool                    #
#           Copyright 2021, Altium, Inc.          #
#  Author: Keith Lee                              #
#  E-Mail: keith.lee@altium.com                   #
###################################################
import graphviz

from pyDtsTool import DeviceTree, TupleNodeProperty, TupleListNodeProperty
import os


class DtGraph(object):
    def __init__(self, device_tree: DeviceTree):
        self.dt = device_tree
        self.graph = graphviz.Digraph(self.dt.filename, filename=os.path.splitext(self.dt.filename)[0] + '.gv')
        self.graph.attr(rankdir='LR')
        self._next_index = 0

    def index(self):
            while True:
                self._next_index += 1
                yield self._next_index

    def add_node(self, parent, child):
        # if child.ref is not None:
        #     self.graph.node(child.ref, child.nodename)
        #     name = child.ref
        name = '[{}] {}'.format(next(self.index()), child.pathname)
        self.graph.node(name, name)
        self.graph.edge(parent, name)
        # for prop in [p for p in child.properties if type(p) in [TupleNodeProperty, TupleListNodeProperty]]:
        #     val = next((v for v in prop.property_value if isinstance(v, str) and v.startswith('&')), None)
        #     if val is not None:
        #         self.graph.edge(name, val[1:], style='dashed')
        for c in child.children:
            self.add_node(child.nodename, c)

    def generate(self):
        root = self.dt.nodes_by_name.get('/', None)
        if root != None:
            self.graph.node('[{}]/'.format(next(self.index())), '/')

            for node in self.dt.nodes_by_name['/'].children:
                self.add_node('[/', node)
        for ref, node in self.dt.nodes_by_ref.items():
            self.graph.node(ref, ref)
            # for prop in [p for p in node.properties if type(p) in [TupleNodeProperty, TupleListNodeProperty]]:
            #     val = next((v for v in prop.property_value if v.startswith('&')), None)
            #     if val is not None:
            #         self.graph.edge(ref, val[1:], style='dashed')
            for n in node.children:
                self.add_node(ref, n)
        self.graph.format = 'svg'
        self.graph.save()
        self.graph.render()



