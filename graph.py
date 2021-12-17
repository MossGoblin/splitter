from typing import Dict, List
import toolbox as tb
import workbench as wb
import math


class Node():
    label = ''
    value = 0
    links = []

    def __init__(self, label: int, value: int, links: List):
        if value == None or links == None:
            return
        self.init(label, value, links)

    def __str__(self):
        string_links = [str(int) for int in self.links]
        links = ', '.join(string_links)
        return f'{self.label} ({self.value}) -> [{links}]'

    def set_value(self, value):
        self.value = value

    def set_links(self, links: List):
        self.links = links

    def set_label(self, label: int):
        self.label = label

    def init(self, label: int, value: int, links: List):
        self.set_label(label)
        self.set_value(value)
        self.set_links(links)
        if not self.validate():
            raise Exception(
                f'A node can not link to itself. Node: {self.label}({self.value})')

    def validate(self):
        # validate for self-reference
        for link in self.links:
            if link == self.label:
                return False
        return True


class Graph():
    nodes = []
    node_map = {}
    map_total = 0
    split_deviations = {}

    def __init__(self):
        pass

    def __str__(self):
        graph_str = ''
        for node in self.nodes:
            graph_str = graph_str + str(node) + '\n'
        return graph_str

    def add_node(self, node):
        self.nodes.append(node)
        self.node_map[node.label] = {}
        self.node_map[node.label]['value'] = node.value
        self.node_map[node.label]['links'] = node.links
        self.node_map[node.label]['level'] = 0

    def add_nodes(self, nodes: List):
        self.nodes.extend(nodes)
        self.validate()

    def validate(self) -> bool:
        # check if there are no dead links - leading to unexisting nodes
        node_links_list = []
        for node in self.nodes:
            node_links_list.extend(node.links)

        for node in self.nodes:
            if node.value not in node_links_list:
                return False
        self.calculate_total()
        return True

    def calculate_deviation(self, split_number) -> Dict:
        if split_number in self.split_deviations:
            return self.split_deviations[split_number]
        else:
            split_floor = math.floor(self.map_total / split_number)
            split_deviation = self.map_total % split_number
            self.split_deviations[split_number] = {}
            self.split_deviations[split_number]['floor'] = split_floor
            self.split_deviations[split_number]['deviation'] = split_deviation
            return split_deviation

    def calculate_total(self):
        for node in self.nodes:
            self.map_total = self.map_total + node.value

    def process_graph(self, split_number: int):
        '''
        == PROCESS ==
        start iterating from count 0
        count = 0:
        iterate all nodes in node_map with level 0
            for each node calculate all couples between that node and their linked level 0 nodes and add the couples to the node_map:
                for A and B being each two connected nodes
                label = sort([A, B])
                value = A.value + B.value
                links = A.links + B.links -> remove A and B from the new list AND remove all duplicates
                level = count (the first is 1)
        check if there are (split-1) number of values that:
            have no common index in their label
            AND
            have a total deviation no greater than the split_deviation for split_number
        if NOT:
            increase count by 1
            repeat procedure by combining all nodes with level (count-1) with their linked nodes (of level 0)
        '''

        pass
