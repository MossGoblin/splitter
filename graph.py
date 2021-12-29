from typing import Dict, List
import workbench as wb
import json
import copy

class Node():
    label = ''
    value = 0
    links = []
    # sig = '[' + label + ']'

    def __init__(self, label: int, value: int, links: List):
        if value == None or links == None:
            return
        self.init(label, value, links)

    def __str__(self):
        string_links = [str(int) for int in self.links]
        links = ', '.join(string_links)
        return f'{self.sig} ({self.value}) -> [{links}]'

    def set_value(self, value):
        self.value = value

    def set_links(self, links: List):
        self.links = links

    def set_label(self, label: int):
        self.label = label
        self.sig = '[' + label + ']'

    def init(self, label: int, value: int, links: List):
        self.set_label(label)
        self.set_value(value)
        self.set_links(links)
        if not self.validate():
            raise Exception(
                f'Node {self.sig}({self.value}) is trying to link to itself.')

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
                wb.report(f'node {node.sig} needs to be rechecked')
                valid = False
        if valid:
            wb.report('The graph is valid')

    def find_distances(self):
        distance_queue = []
        processed_nodes = []
        distance_queue.append(self.nodes[0])
        processed_nodes.append(self.nodes[0].label)
        while len(distance_queue) > 0:
            node_to_add = distance_queue.pop()
            for nbr in node_to_add.links:
                if nbr not in processed_nodes:
                    distance_queue.append(self.get_node(nbr))
                    processed_nodes.append(nbr)
            self.add_node_to_distance_map(node_to_add)
        pass
        self.print_distance_map()

    def add_node_to_distance_map(self, node):
        # Check if the node can be added - needs to be adjacent to at least on other node in the map
        if not self.verify_cmg(node):
            raise Exception(
                f'Adding node {node.sig} failed - no nbrs to existing map nodes')
        wb.report(f'Adding node {node.sig} to distance graph')
        # DECLARE - add the node to the graph
        wb.report(f'*   Declaring {node.sig}')
        self.distance_map[node] = {}
        # distance to self is always 0
        self.distance_map[node][node.label] = 0
        # add node nbrs to map
        wb.report(f'*   Adding nbrs of {node.sig}')
        for nbr in node.links:
            wb.report(f'    -   Nbr {nbr} added')
            self.distance_map[node][nbr] = 1
            if self.get_node(nbr) in self.distance_map and node.label not in self.distance_map[self.get_node(nbr)]:
                self.distance_map[self.get_node(nbr)][node.label] = 1
        # process links to all other nodes
        self.adjust_distances_to_node(node)
        self.adjust_old_distances_through_node(node)
        wb.report('== == ==\n')
        pass

    def adjust_distances_to_node(self, node):
        wb.report(f'*   Adding nbrs of {node.sig}')
        if len(self.distance_map) == 1:
            wb.report(f'    *   No distances to adjust for {node.sig}')
            return
        # find all parents of node
        parents = []
        for nbr in node.links:
            if self.get_node(nbr) in self.distance_map:
                parents.append(self.get_node(nbr))
        if len(parents) == 0:
            raise Exception(
                f'Something went wrong. Could not find a parent for {node.sig}')

        # the distance from the other nodes to node equals their distance to parent + 1
        for distant_node in self.distance_map:
            min_distance = len(self.distance_map)
            if distant_node.label in self.distance_map[node]:
                continue
            for parent in parents:
                distance = self.distance_map[distant_node][parent.label] + 1
                if distance < min_distance:
                    min_distance = distance
            wb.report(f'    *   Distance between {node.sig} and {distant_node.sig} recorded as {min_distance}')
            self.distance_map[node][distant_node.label] = min_distance
            self.distance_map[distant_node][node.label] = min_distance

    def adjust_old_distances_through_node(self, node):
        wb.report(f'    *   Checking distances between old nodes through {node.sig}')
        # Iterate pais of nodes (other than node)
        for node_one, node_two in self.distance_map_pairs(node):
            if node_one.label in self.distance_map[node_two] and self.distance_map[node_two][node_one.label] == 1:
                continue
            if self.distance_map[node_one][node_two.label] > self.distance_map[node_one][node.label] + self.distance_map[node_two][node.label]:
                self.distance_map[node_one][node_two.label] = self.distance_map[node_one][node.label] + \
                    self.distance_map[node_two][node.label]
                self.distance_map[node_two][node_one.label] = self.distance_map[node_one][node.label] + \
                    self.distance_map[node_two][node.label]
                wb.report(f'      *   Distance between {node_one.sig} and {node_two.sig} adjusted to {self.distance_map[node_one][node_two.label]}')
        pass

    def distance_map_pairs(self, excluded_nodes):
        # used to avoid duplicates
        checked_pairs = []
        if isinstance(excluded_nodes, Node):
            excluded_nodes = [excluded_nodes]
        for node_one in self.distance_map:
            if node_one in excluded_nodes:
                continue
            for node_two in self.distance_map:
                if node_two in excluded_nodes:
                    continue
                if node_one is node_two:
                    continue
                pair_labels = sorted([node_one.label, node_two.label])
                if pair_labels in checked_pairs:
                    continue
                checked_pairs.append(sorted([node_one.label, node_two.label]))
                yield (node_one, node_two)

    def verify_cmg(self, node):
        if len(self.distance_map) == 0:
            return True
        # Check for Continuous Map Growth
        for graph_node in self.distance_map:
            if graph_node.label in node.links:
                return True
        return False

    def print_distance_map(self):
        wb.report('== Distance Map ==')
        wb.report('===')
        for node in self.distance_map:
            wb.report(f'{node.sig}:')
            wb.report(f'    {node.label} : {self.distance_map[node][node.label]}')
            for link, distance in self.distance_map[node].items():
                if link == node.label:
                    continue
                wb.report(f'    {link} : {distance}')
            wb.report('')
        wb.report('===')

    def get_peripheral_nodes(self, node_number):
        '''
        find [node_number] nodes that are as far away from each other as possible
        definition of "as far away from each other as possible":
            the minimum distance between any two of the selected nodes is as large as possible
        '''
        distance_distribution = {}
        # get a list of all possible distances
        for node, distant_node in self.distance_map.items():
            for distant_node_distance in distant_node:
                distance = self.distance_map[node][distant_node_distance]
                if distance not in distance_distribution:
                    distance_distribution[distance] = []
                    distance_distribution[distance].append(sorted([node.label, distant_node_distance]))
                elif sorted([node.label, distant_node_distance]) not in distance_distribution[distance]:
                    distance_distribution[distance].append(sorted([node.label, distant_node_distance]))
        wb.report(f'Distance distrubution built')
        wb.report(json.dumps(distance_distribution))

        # select the peripherals
        # try to find the requisite number in the highest distance category
        # if there is no suitable combination, add the lower category and search in the highest two
        # if needed, repeat by adding another one and so on
        # TODO recursiion!
        '''
        Conditions for peripherals in the current distribution:
        In the peripheral group there are
            *   exactly node_number unique nodes
            *   exactly node_number * (node_number - 1) couples
        '''
        found = False
        # cut_off = 1 # DBG start from 1 in order to check both distance groups 2 and 3
        cut_off = 0
        while not found:
            cut_off = cut_off + 1
            peripheral_group = []
            reduced_distribution = self.get_reduced_distribution(distance_distribution, cut_off)

            # DBG only
            checked_pairs = []
            peripheral_group, found = self.search_reduced_distribution_for_peripherals(reduced_distribution, peripheral_group, node_number, checked_pairs)
        pass

    def search_reduced_distribution_for_peripherals(self, distribution, group, count, checked_pairs):

        def node_number_condition(node_counter, count):
            if len(node_counter) < count:
                # 1st bool - node number matching ?
                # 2nd bool - node count overshot ?
                return False, False
            elif len(node_counter) == count:
                # 1st bool - node number matching ?
                # 2nd bool - node count overshot ?
                return True, False
            # 1st bool - node number matching ?
            # 2nd bool - node count overshot ?
            return False, True

        def pair_number_condition(group, count):
            pair_number_target = count * (count - 1) / 2
            if len(group) < pair_number_target:
                # 1st bool - pair number matching ?
                # 2nd bool - pair count overshot ?
                return False, False
            elif len(group) == pair_number_target:
                # 1st bool - pair number matching ?
                # 2nd bool - pair count overshot ?
                return True, False
            # 1st bool - pair number matching ?
            # 2nd bool - pair count overshot ?
            return False, True



        # 1. add new pair from the distribution to the group
        new_group = copy.deepcopy(group)

        new_pair_added = False
        for distance, pairs in distribution.items():
            wb.report(f'. cheking distance {distance}')
            for pair in pairs:
                if pair not in new_group:
                    new_group.append(pair)
                    new_pair_added = True
                    checked_pairs.append(pair)
                    wb.report(f'. adding {pair}')
                    wb.report(f'. new group {new_group}')
                    break
            if not new_pair_added:
                # the group has been exhausted and peripherals can not be found
                wb.report(f'. pairs exhausted')
                return new_group, False

            
            # build a list of all elements of the group with count of occurences
            node_counter = []
            for pair in new_group:
                node_counter.extend(pair)
                node_counter = list(set(node_counter))

            # node_counter = []
            # for element in new_group:
            #     if element[0] not in node_counter:
            #         node_counter.append(element[0])
            #     if element[1] not in node_counter:
            #         node_counter.append(element[1])
            # check for completeness:

            node_count_matching, node_count_overshot = node_number_condition(node_counter, count)
            pair_matching, pair_count_overshot = pair_number_condition(new_group, count)

            # DBG VERIABLE
            can_continue = not node_count_overshot and not pair_count_overshot

            if node_count_matching and not node_count_overshot and pair_matching and not pair_count_overshot:
                # we have found a group with the exact number of nodes and pairs
                # COMPLETE
                wb.report(f'. group completed: {new_group}')
                return new_group, True


            # if not complete:
            # check if we can continue
            if node_count_overshot or pair_count_overshot:
                # the last iteration overshot the number of pairs OR nodes
                # return without the new pair pair and declare not finished
                wb.report(f'. target overshot: {new_group} -> {"nodes" if node_count_overshot else "pairs"}')
                wb.report(f'. reverting to : {group}')
                return group, False

            # if the pair count and the node count did not overshoot
            # continue digging in
            wb.report(f'. digging in with {new_group}')
            group, completed = self.search_reduced_distribution_for_peripherals(distribution, new_group, count, checked_pairs)
            if completed:
                wb.report(f'. group found: {group}')
                return group, completed
            # reset new_group
            new_group = copy.deepcopy(group)
        wb.report(f'. reverting to : {group}')
        return group, False


    def get_reduced_distribution(self, distance_distribution, cut_off):
        reduced_distribution = {}
        sorted_distribution_keys = sorted(distance_distribution.keys(), reverse=True)
        selected_key_categories = []
        for key in sorted_distribution_keys:
            selected_key_categories.append(key)
            if len(selected_key_categories) > cut_off:
                break
            reduced_distribution[key] = distance_distribution[key]
        return reduced_distribution