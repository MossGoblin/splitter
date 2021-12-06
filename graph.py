from typing import List
import toolbox as tb
import workbench as wb


class Node():
    label = ''
    value = 0
    links = []

    def __init__(self, value: int = None, links: List = None, label: str = None):
        if value == None or links == None:
            return
        self.init(value, links, label)

    def __str__(self):
        string_links = [str(int) for int in self.links]
        links = ', '.join(string_links)
        return f'{self.label}: {self.value} [{links}]'

    def set_value(self, value):
        self.value = value

    def set_links(self, links: List):
        self.links = links

    def set_label(self, label: str):
        self.label = label

    def init(self, value: int, links: List, label: str = None):
        if not label:
            label, wb.LABEL_LIST = tb.get_label(wb.LABEL_LIST)
        self.set_label(label)
        self.set_value(value)
        self.set_links(links)
        if not self.validate():
            raise Exception(
                f'A node can not link to itself. Node: {self.label}({self.value})')

    def validate(self):
        # validate for self-reference
        for link in self.links:
            if link == self.value:
                return False
        return True


class Graph():
    nodes = []
    node_map = {}

    def __init__(self):
        pass

    def __str__(self):
        graph_str = ''
        for node in self.nodes:
            graph_str = graph_str + str(node) + '\n'
        return graph_str

    def add_node(self, node):
        self.nodes.append(node)
        self.node_map[node.value] = {}
        self.node_map[node.value]['label'] = node.label
        self.node_map[node.value]['full_links'] = node.links
        self.node_map[node.value]['filtered_links'] = node.links

    def add_nodes(self, nodes: List):
        self.nodes.extend(nodes)

    def validate(self):
        # check if all node links lead to other nodes
        node_list = []
        for node in self.nodes:
            node_list.append(node)

        for node in self.nodes:
            for link in node.links:
                if link not in node_list:
                    return False
        return True