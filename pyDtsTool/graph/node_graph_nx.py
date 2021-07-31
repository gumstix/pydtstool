from pyvis.network import Network
import networkx as nx
from networkx.drawing.nx_agraph import write_dot
from pyDtsTool import DeviceTree, Node
from os import popen

class DtGraph(object):
    def __init__(self, dt: DeviceTree):
        self.dt = dt
        self.graph = nx.DiGraph()
        self.count = 0

    def add_node(self, parent: str, child: Node):
        name = '[{}] '.format(self.count) + child.pathname
        self.count += 1
        self.graph.add_node(name,
                            title=child.path,
                            node_properties=('\n'.join(p.print(1) for p in child.properties)))
        self.graph.add_edge(parent, name)
        for c in child.children:
            self.add_node(name, c)

    def generate(self):
        root = self.dt.nodes_by_name.get('/', None)
        if root != None:
            root_id = '[{}] /'.format(self.count)
            self.graph.add_node(root_id, title='/',
                                node_properties=('\n'.join(p.print(1) for p in root.properties)))
            self.count += 1
            for child in root.children:
                self.add_node(root_id, child)
        for ref, node in self.dt.nodes_by_ref.items():
            ref_id =  '[{}] &{}'.format(self.count, ref)
            self.graph.add_node(ref_id, title='&'+ref,
                                node_properties=('\n'.join(p.print(1) for p in node.properties)))
            for child in node.children:
                self.add_node(ref_id, child)
        write_dot(self.graph, self.dt.filename + '.dot')