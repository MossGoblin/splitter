from typing import Dict, List
import workbench as wb
import math
import queue

class Node():
    label = ''
    value = 0
    links = []
    signature = []

    def __init__(self, label: int, value: int, signature: List, links: List):
        if value == None or links == None:
            return
        self.init(label, value, signature, links)

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

    def set_signature(self, signature: List):
        self.signature = signature

    def init(self, label: int, value: int, signature: List, links: List):
        self.set_label(label)
        self.set_value(value)
        self.set_links(links)
        self.set_signature(signature)
        if not self.validate():
            raise Exception(
                f'Node {self.label}({self.value}) is trying to link to itself.')

    def validate(self):
        # validate for self-reference
        for link in self.links:
            if link == self.label:
                return False
        return True


class Graph():
    nodes = []  # a list of all 0 level nodes
    node_map = {}  # an enchanced map of nodes, separated by level
    map_total = 0  # the total weight of all the level 0 nodes
    distance_map = {}  # an enchanced map of nodes, separated by level

    def __init__(self):
        pass

    def __str__(self):
        graph_str = ''
        for node in self.nodes:
            graph_str = graph_str + str(node) + '\n'
        return graph_str

    def add_node(self, node, level):
        if level == 0:
            self.nodes.append(node)
        pass

    def calculate_deviation(self, split_number) -> Dict:
        pass

    def calculate_total(self):
        pass

    def process_graph(self, split_number: int):
        '''
        == PROCESS ==
        Find all distances within the map
        Select (split) number of nodes that are as far away from each other as possible (definition to be scrutinized -> highest min distance)
        Spread sub-networks from each of the nodes simultaneously until all nodes are within any one of the subnetworks
        Negotiate bordering nodes to adjust subnetwork weights

                == (OBSOLETE) ==
                start iterating from count 0
                count = 0:
                check if there are (split-1) nodes of level = count that:
                    have no common index in their label
                    AND
                    have values with a total deviation no greater than the split_deviation for split_number
                if NOT:
                    increase count by 1
                    Add another level of nodes
                ADD LEVEL
                iterate all nodes in node_map with the highest level
                    for each node calculate all couples between that node and their linked level 0 nodes and add the couples to the node_map:
                        for A and B being each two connected nodes
                        label = sort([A, B])
                        value = A.value + B.value
                        links = A.links + B.links -> remove A and B from the new list AND remove all duplicates
                        level = count (the first is 1)
        '''
        pass

    def find_distances(self):
        exploration_queue = []
        for node in self.nodes:
            exploration_queue.append(node)
            self.distance_map[node.label] = {}
            for nbr in node.links:
                self.distance_map[node.label][nbr] = 1
        # HERE
        pass