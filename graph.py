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
        # validate for unique values
        if len(self.links) > len(set(self.links)):
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

    def validate(self):
        valid = True
        for node in self.nodes:
            links_check = []
            label = node.label
            for another_node in self.nodes:
                if label in another_node.links:
                    links_check.append(another_node.label)
            if sorted(links_check) != sorted(node.links):
                print(f'node {node.signature} needs to be rechecked')
                valid = False
        if valid:
            print('The graph is valid')


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
        self.print_distance_map()

    def print_distance_map(self):
        print('== Distance Map ==')
        print('===')
        for node in self.distance_map:
            print(f'{node.signature}({node.label}):')
            for link, distance in self.distance_map[node].items():
                print(f'    {link} : {distance}')
            print('---')
        print('===')

    def process_node_distances(self, node, parent):
        print(f'== Processing distances for {node.signature}')
        '''
        == NEW PROCEDURE ==
        BackProp - check if the new node provides shorter paths to his links
            *   if the prev has a link to the node link and it is larger than 2, set it to 2
            *   if the prev has a link to the node link and it is 2 or less, leave it
            *   if the prev does not have a link to the node link, create it as 2
        Declare - write the new node in distance map:
            *   record new node links as distances
        Inherit - get all links from prev that are not present in node - add them as + 1
        ''' 
        # BACKPROPAGATION
        print(f'* BACKPROPAGATION checking for new distances to {node.signature}`s links')
        for prev_node in self.distance_map:
            print(f'  -   checking if {prev_node.signature} has got a new path to new links')
            for link in node.links:
                # skip backlinks
                if link == prev_node.label:
                    continue
                # the previous node does not know about the new link - set it to the distance to parent + 1
                if prev_node is parent:
                    if link not in self.distance_map[prev_node]:
                        print(f'    --  {prev_node.signature} got NEW link - {link} at distance 2')
                        self.distance_map[prev_node][link] = 2
                    elif self.distance_map[prev_node][link] > 2:
                        print(f'    --  {prev_node.signature} UPDATED link - {link} at distance 2')
                        self.distance_map[prev_node][link] = 2
                else:
                    if link not in self.distance_map[prev_node]:
                    # if the previos node has distance to the new link longer than the distance through the new node
                        print(f'    --  {prev_node.signature} got NEW link - {link} at distance {self.distance_map[prev_node][node.label] + 1}')
                        self.distance_map[prev_node][link] = self.distance_map[prev_node][node.label] + 1
                    elif self.distance_map[prev_node][link] > self.distance_map[prev_node][node.label] + 1:
                        print(f'    --  {prev_node.signature} got UPDATED link - {link} at distance {self.distance_map[prev_node][node.label] + 1}')
                        self.distance_map[prev_node][link] = self.distance_map[prev_node][node.label] + 1

        # DECLARATION
        print(f'- DECLARATION for {node.signature}')
        if node in self.distance_map:
            raise Exception (f'Node {node.signature} is already in distance map')
        self.distance_map[node] = {}
        for link in node.links:
            print(f'    -   Node {node.signature} declared new link to {link} at distance 1')
            self.distance_map[node][link] = 1

        # INHERITENCE
        if not parent:
            print('No parent to inherit links from')
            print(' \n')
            return
        print(f'INHERITENCE new links for {node.signature} from parent {parent.signature}')
        for parent_link in parent.links:
            if parent_link == node.label:
                continue
            if parent_link not in self.distance_map[node]:
                print(f'    --  Node {node.signature} inherited link to {parent_link} as distance {self.distance_map[parent][parent_link] + 1}')
                self.distance_map[node][parent_link] = self.distance_map[parent][parent_link] + 1
        print(' \n')
        pass


    def process_node_distances_(self, node, parent):
        print(f'Processing distances for {node.signature}')
        '''
        == NEW PROCEDURE ==
        Declare - write the new node in distance map:
            *   record new node links as distances
        BackProp - edit the links of all previously recorded nodes
            *   if the prev has a link to the node link and it is larger than 2, set it to 2
            *   if the prev has a link to the node link and it is 2 or less, leave it
            *   if the prev does not have a link to the node link, create it as 2
        Inherit - get all links from parent that are not present in node - add them as + 1
        ''' 
        # DECLARE
        # init node in distance_map
        print(f'* declaring node {node.label}')
        if node not in self.distance_map:
            self.distance_map[node] = {}
        # note down own link distances
        for link in node.links:
            self.distance_map[node][link] = 1
        # check if previous nodes know about the new node
        for recorded_node in self.distance_map:
            if recorded_node is node:
                continue
            if recorded_node is parent:
                continue
            if node.label not in self.distance_map[recorded_node]:
                self.distance_map[recorded_node][node.label] = self.distance_map[recorded_node][parent.label] + 1
            else:
                if parent.label not in self.distance_map[recorded_node]:
                    continue
                if self.distance_map[recorded_node][node.label] > self.distance_map[recorded_node][parent.label] + 1:
                    self.distance_map[recorded_node][node.label] = self.distance_map[recorded_node][parent.label] + 1

        print(f'* back propagation from node {node.label}')
        # BACK PROPAGATE
        for node_link in node.links:
            for recorded_node in self.distance_map:
                print(f'    * checking node {recorded_node.label} for distance to {node_link}')
                if recorded_node is node:
                    continue
                if node_link == recorded_node.label:
                    continue
                if node_link not in self.distance_map[recorded_node]:
                    self.distance_map[recorded_node][node_link] = 2
                    print(f'    - link {recorded_node.label} - {node_link} SET to 2')
                elif self.distance_map[recorded_node][node_link] > 2:
                    print(f'    - link {recorded_node.label} - {node_link} REDUCED to 2')
                    self.distance_map[recorded_node][node_link] = 2
        
        # INHERIT
        print(f'* inheritence from node {node.label}')
        if parent:
            for parent_link in self.distance_map[parent]:
                if parent_link == node.label:
                    continue
                if parent_link not in self.distance_map[node]:
                    print(f'    - link {node.label} - {parent_link} INHERITED as {self.distance_map[parent][parent_link] + 1}')
                    self.distance_map[node][parent_link] = self.distance_map[parent][parent_link] + 1
        
        print(f'== == ==')