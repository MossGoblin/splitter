from typing import Dict, List
import workbench as wb
import math
import queue

class Node():
    label = None
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
        return f'{self.signature} ({self.value}) -> [{links}]'

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

    def get_node(self, label):
        for node in self.nodes:
            if node.label == label:
                return node
        return None
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
        checked_nodes = []
        exploration_queue.append((self.nodes[0], None))
        checked_nodes.append(self.nodes[0])
        while len(exploration_queue) > 0:
            # pop a node
            current_node, parent = exploration_queue.pop()
            # place all links in the Q
            # mark all links as checked
            # add links to exploration queue
            for link in current_node.links:
                linked_node = self.get_node(link)
                if linked_node not in checked_nodes:
                    checked_nodes.append(linked_node)
                    exploration_queue.append((linked_node, current_node))
            # process current_node
            self.process_node_distances(current_node, parent)
        pass

    def process_node_distances(self, node, parent):
        print(f'processing distances for {node.signature}')
        # init node in distance_map
        if node not in self.distance_map:
            self.distance_map[node] = {}
        # note down own link distances
        for link in node.links:
            self.distance_map[node][link] = 1
        # iterate through all other nodes already in the distance map
        for recorded_node in self.nodes:
            # do not update recorded_node if has no parent (i.e dno update if this is the first node)
            if not parent:
                continue
            # update only nodes that are already in the distance map
            if recorded_node not in self.distance_map:
                continue
            # do not update recorded_node if it is parent
            if recorded_node is parent:
                continue
            # do not update recorded node if it is node
            if recorded_node is not node:
                # check new straight distance - through the new node
                #   = if there is no link between the recorded_node and node:
                #      = add the new link as the distance between the recorded_node and the parent + 1
                if not node.label in self.distance_map[recorded_node]:
                    print(f'update {recorded_node}')
                    self.distance_map[recorded_node][node.label] = self.distance_map[recorded_node][parent.label] + 1
                    # TODO breaks above, additional checks required for self.distance_map[recorded_node][parent.label]
                    print(f'updated distance from {recorded_node.signature} to {node.signature} to {self.distance_map[recorded_node][node.label]}')

        print(f'== == ==')
        pass