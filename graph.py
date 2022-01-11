from typing import Dict, List

from sympy.core.function import diff
import workbench as wb
import json
import copy
import logging
import math

# logging.basicConfig(filename='processing.log', encoding='utf-8', level=logging.debug)


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
    split_count = 0  # the total number of target splits
    peripherals_list = []  # a list of all anchor groups
    anchors = []  # a list of anchors selected from peripherals_list
    splits = []  # a list of all split networks, build around anchors
    split_totals = {}  # a list of the total values of each split

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

    def validate(self, rectangular=True):
        if rectangular:
            valid = True
            for node in self.nodes:
                links_check = []
                label = node.label
                for another_node in self.nodes:
                    if label in another_node.links:
                        links_check.append(another_node.label)
                if sorted(links_check) != sorted(node.links):
                    logging.error(f'node {node.sig} needs to be rechecked')
                    valid = False
            if valid:
                logging.debug('The graph is valid')
        self.total_value = self.get_graph_total()

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
        self.print_distance_map()

    def add_node_to_distance_map(self, node):
        # Check if the node can be added - needs to be adjacent to at least on other node in the map
        if not self.verify_cmg(node):
            raise Exception(
                f'Adding node {node.sig} failed - no nbrs to existing map nodes')
        logging.debug(f'Adding node {node.sig} to distance graph')
        # DECLARE - add the node to the graph
        logging.debug(f'*   Declaring {node.sig}')
        self.distance_map[node] = {}
        # distance to self is always 0
        self.distance_map[node][node.label] = 0
        # add node nbrs to map
        logging.debug(f'*   Adding nbrs of {node.sig}')
        for nbr in node.links:
            logging.debug(f'    -   Nbr {nbr} added')
            self.distance_map[node][nbr] = 1
            if self.get_node(nbr) in self.distance_map and node.label not in self.distance_map[self.get_node(nbr)]:
                self.distance_map[self.get_node(nbr)][node.label] = 1
        # process links to all other nodes
        self.adjust_distances_to_node(node)
        self.adjust_old_distances_through_node(node)

    def adjust_distances_to_node(self, node):
        logging.debug(f'*   Adding nbrs of {node.sig}')
        if len(self.distance_map) == 1:
            logging.debug(f'    *   No distances to adjust for {node.sig}')
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
            logging.debug(
                f'    *   Distance between {node.sig} and {distant_node.sig} recorded as {min_distance}')
            self.distance_map[node][distant_node.label] = min_distance
            self.distance_map[distant_node][node.label] = min_distance

    def adjust_old_distances_through_node(self, node):
        logging.debug(
            f'    *   Checking distances between old nodes through {node.sig}')
        # Iterate pais of nodes (other than node)
        for node_one, node_two in self.distance_map_pairs(node):
            if node_one.label in self.distance_map[node_two] and self.distance_map[node_two][node_one.label] == 1:
                continue
            if self.distance_map[node_one][node_two.label] > self.distance_map[node_one][node.label] + self.distance_map[node_two][node.label]:
                self.distance_map[node_one][node_two.label] = self.distance_map[node_one][node.label] + \
                    self.distance_map[node_two][node.label]
                self.distance_map[node_two][node_one.label] = self.distance_map[node_one][node.label] + \
                    self.distance_map[node_two][node.label]
                logging.debug(
                    f'      *   Distance between {node_one.sig} and {node_two.sig} adjusted to {self.distance_map[node_one][node_two.label]}')

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
        logging.debug('\n== Distance Map ==')
        for node in self.distance_map:
            logging.debug(f'{node.sig}:')
            logging.debug(
                f'    {node.label} : {self.distance_map[node][node.label]}')
            for link, distance in self.distance_map[node].items():
                if link == node.label:
                    continue
                logging.debug(f'    {link} : {distance}')
            logging.debug('')
        # logging.debug('\n')

    def get_peripheral_nodes(self, node_number):
        '''
        find [node_number] nodes that are as far away from each other as possible
        definition of "as far away from each other as possible":
            the minimum distance between any two of the selected nodes is as large as possible
        '''
        self.split_count = node_number
        distance_distribution = {}
        # get a list of all possible distances
        for node, distant_node in self.distance_map.items():
            for distant_node_distance in distant_node:
                distance = self.distance_map[node][distant_node_distance]
                if distance not in distance_distribution:
                    distance_distribution[distance] = []
                    distance_distribution[distance].append(
                        sorted([node.label, distant_node_distance]))
                elif sorted([node.label, distant_node_distance]) not in distance_distribution[distance]:
                    distance_distribution[distance].append(
                        sorted([node.label, distant_node_distance]))
        logging.info(f'.. Distance distrubution built')
        logging.debug(json.dumps(distance_distribution))

        # select the peripherals
        # try to find the requisite number in the highest distance category
        # if there is no suitable combination, add the lower category and search in the highest two
        # if needed, repeat by adding another one and so on
        '''
        Conditions for peripherals in the current distribution:
        In the peripheral group there are
            *   exactly node_number unique nodes
            *   exactly node_number * (node_number - 1) couples
        '''
        found = False
        cut_off = 0
        while not found:
            cut_off = cut_off + 1
            peripherals_list = []
            reduced_distribution = self.get_reduced_distribution(
                distance_distribution, cut_off)
            distribution_flatmap = self.flatten_reduced_distribution(
                reduced_distribution)

            logging.debug(
                f'SIFTING for {node_number} peripherals at cut off {cut_off}')
            peripherals_list, found = self.sift_for_peripherals(
                distribution_flatmap, node_number)
            if found:
                logging.info(f'.. Periferals found')
                for peripherals in peripherals_list:
                    logging.debug(f'{peripherals}')
                self.peripherals_list = peripherals_list
                # TODO select the best group of peripherals
                self.anchors = peripherals_list[0]
                return self.anchors
            else:
                logging.debug('No prefipherals found')

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

        # add new pair - unique combination
        for distance, pair in distribution:
            if pair in group:
                continue
            state = copy.deepcopy(group)
            state.append(pair)
            if state in checked_pairs:
                continue
            group = copy.deepcopy(state)
            checked_pairs.append(state)
            # add all nodes from group to node_counter
            node_counter = []
            for pair in group:
                node_counter.extend(pair)
                node_counter = list(set(node_counter))
            # calculate check conditions
            nodes_match, nodes_overshot = node_number_condition(
                node_counter, count)
            pairs_match, pairs_overshot = pair_number_condition(group, count)
            # check for completion
            if nodes_match and not nodes_overshot and pairs_match and not pairs_overshot:
                return group, True

            # not complete
            else:
                # if over
                if nodes_overshot or pairs_overshot:
                    group.pop()
                    return self.search_reduced_distribution_for_peripherals(distribution, group, count, checked_pairs)
                # if under
                else:
                    return self.search_reduced_distribution_for_peripherals(distribution, group, count, checked_pairs)
        # no more pairs in the distance class
        if len(group) > 0:
            group.pop()
            return self.search_reduced_distribution_for_peripherals(distribution, group, count, checked_pairs)

        # distribution exhausted
        return group, False

    def flatten_reduced_distribution(self, distribution):
        flatmap = []
        for distance, pairs in distribution.items():
            for pair in pairs:
                pair = sorted(pair, key=lambda element: element[0])
                flatmap.append((distance, pair))
        flatmap = sorted(flatmap, key=lambda tup: tup[0], reverse=True)
        return flatmap

    def get_reduced_distribution(self, distance_distribution, cut_off):
        reduced_distribution = {}
        sorted_distribution_keys = sorted(
            distance_distribution.keys(), reverse=True)
        selected_key_categories = []
        for key in sorted_distribution_keys:
            selected_key_categories.append(key)
            if len(selected_key_categories) > cut_off:
                break
            reduced_distribution[key] = distance_distribution[key]
        return reduced_distribution

    def sift_for_peripherals(self, distribution, target):
        '''
        REQUIREMENTS for the group of peripherals:
        1. the groups has [target] number of nodes
        2. all the links between the nodes in the group are within the distribution
        PROCEDURE
        1.  remomve nodes with less than target-1 links
        2. for each remaining node - iterate linked nodes
        2.1 for each linked node - check if it has links to each other linked node
        2.2 if not - remove one of the two - the one with shorter average link distance within the distribution
        3. if enough linked nodes remain (target-1) - return the node and it's linked nodes as group
        '''

        def flatten_distribution(distribution):
            flat_distribution = []
            for pair_data in distribution:
                flat_distribution.append(sorted(pair_data[1]))
            return flat_distribution

        def get_link_average(node, distribution, node_group):
            running_total = 0
            counter = 0
            for pair_data in distribution:
                # we are only interested in pair of nodes from the node group
                if pair_data[1][0] in node_group and pair_data[1][1] in node_group:
                    # we are only interested in pairs that contain node
                    if node in pair_data[1]:
                        counter = counter + 1
                        running_total = running_total + pair_data[0]
            return (running_total / counter) if counter > 0 else 0

        def reduce_group(node_links, distribution, flat_distribution, target):
            group = copy.deepcopy(node_links)
            for node in node_links:
                for second_node in group:
                    if node == second_node:
                        continue
                    if node not in group:
                        continue
                    if not sorted([node, second_node]) in flat_distribution:
                        node_avg = get_link_average(node, distribution, group)
                        second_node_avg = get_link_average(
                            second_node, distribution, group)
                        # Remove the mode with shorter average links
                        node_to_remove = second_node if second_node_avg < node_avg else node
                        group.remove(node_to_remove)
                        break

            # the group has to end up having exactly target-1 nodes
            number_of_nodes_to_remove = len(group) - (target - 1)
            reduced_group = copy.deepcopy(group)

            if number_of_nodes_to_remove > 0:
                for counter in range(number_of_nodes_to_remove):
                    evaluated_nodes = {}
                    for node in reduced_group:
                        evaluated_nodes[node] = get_link_average(node, distribution, reduced_group)
                    node_to_remove = sorted(evaluated_nodes)[0]
                    reduced_group.remove(node_to_remove)


            return reduced_group

        peripherals_list = []
        node_collection = {}
        for distance, nodes in distribution:
            if nodes[0] not in node_collection:
                node_collection[nodes[0]] = []
            if nodes[1] not in node_collection:
                node_collection[nodes[1]] = []
            node_collection[nodes[0]].append(nodes[1])
            node_collection[nodes[1]].append(nodes[0])

        sieved_nodes = {}
        for node, node_data in node_collection.items():
            if len(node_collection[node]) >= target - 1:
                sieved_nodes[node] = []
                sieved_nodes[node] = node_data
        if len(sieved_nodes) < target:
            return [], False

        flat_distribution = flatten_distribution(distribution)
        for node, node_links in sieved_nodes.items():
            candidate_group = []
            candidate_group = reduce_group(
                node_links, distribution, flat_distribution, target)
            candidate_group.append(node)

            if len(candidate_group) >= target:
                if sorted(candidate_group) not in peripherals_list:
                    peripherals_list.append(sorted(candidate_group))

        if len(peripherals_list) == 0:
            return [], False
        return peripherals_list, True

    def creep_splits(self, anchors=None):
        '''
        Initiates one split network per anchor
        Starts acquiring adjacent nodes to each anchor, taking into account the size of the adjacent nodes - larger are added slower
        '''
        if not anchors:
            anchors = self.anchors

        # build split networks and creep map
        splits = {}  # all split networks
        creep_map = {}  # holder for the creep counters
        creep_prospects = {}  # map of the prospects of each split network
        claimed_nodes = []  # a list of all claimed nodes
        for anchor in anchors:
            splits[anchor] = []
            splits[anchor].append(anchor)
            anchor_size = self.get_node(anchor).value
            creep_map[anchor] = anchor_size * -1 + 1
            creep_prospects[anchor] = []
            for link in self.get_node(anchor).links:
                creep_prospects[anchor].append(link)
            claimed_nodes.append(anchor)

        tick = 0
        while len(claimed_nodes) < len(self.nodes):
            # add one tick to each creep
            tick = tick + 1
            logging.debug(f'Tick [ {tick} ]')
            for anchor in anchors:
                logging.debug(f'Split {anchor} at {creep_map[anchor]}')

            # Iterate anchors based on accumulated network value - the smallest network at the moment gets to be checked for new additions first
            # prepare list of collected accumulated values
            split_values = {}
            for split in splits:
                split_values[split] = 0
                for node in split:
                    split_values[split] = split_values[split] + \
                        self.get_node(node).value

            # prepare ordered list for iterating
            ordered_splits = sorted(
                split_values.items(), key=lambda network: network[1])

            for anchor_data in ordered_splits:
                anchor = anchor_data[0]
                prospects_updated = False
                creep_map[anchor] = creep_map[anchor] + 1
                # check in each creep prospect if there is a node to be acquired
                # make an editable copy of the creep prospects to work with
                current_prospects = copy.deepcopy(creep_prospects[anchor])
                for prospect in creep_prospects[anchor]:
                    logging.debug(f'-   {anchor} checks {prospect}')
                    if prospect in claimed_nodes:
                        logging.debug(' -   already claimed')
                        continue
                    if creep_map[anchor] >= self.get_node(prospect).value:
                        logging.debug(f'{anchor} ADDS {prospect}')
                        # add the prospect to the split
                        splits[anchor].append(prospect)
                        # add the prospect to the list of all claimed nodes
                        claimed_nodes.append(prospect)
                        # remove the prospect from the list of prospects for this split
                        current_prospects.remove(prospect)
                        # add to the list of split prospects the nbrs of the previous addition
                        for link in self.get_node(prospect).links:
                            if link not in claimed_nodes:
                                if link in current_prospects:
                                    continue
                                current_prospects.append(link)
                                logging.debug(
                                    f'-   adding {link} to the prospects of {anchor}')
                        # reset creep value of the split
                        creep_map[anchor] = 1
                        prospects_updated = True
                # set the creep prospects to the edited current_prospects
                if prospects_updated:
                    creep_prospects[anchor] = []
                    for new_prospect in current_prospects:
                        creep_prospects[anchor].append(new_prospect)

        self.splits = splits

        totals = {}
        for anchor in anchors:
            totals[anchor] = 0
            for node in splits[anchor]:
                totals[anchor] = totals[anchor] + self.get_node(node).value
                self.split_totals[anchor] = totals[anchor]

        for anchor in anchors:
            logging.debug(
                f'{splits[anchor][0]} > {totals[anchor]} > {splits[anchor]}')

    def negotiate_borders(self):
        self.create_border_map()
        for split_anchor, border_data in self.border_map.items():
            logging.debug(f'Border nodes for {split_anchor}: {border_data}')

        # calculate target values
        self.split_average = self.total_value / self.split_count
        self.average_deviation = (self.total_value % self.split_count) / 3

        logging.info('Start negotiations')
        self.run_negoriation()

    def create_border_map(self):
        logging.info('Creating border map')
        # create a map of border nodes
        # all nodes have been assigned by the creep
        # for each pair of splits there are two sets of border nodes:
        # - nodes that are part of split one and ones that are part of split two
        # the border map has a part for each split and has it's border nodes for each borsering split
        border_map = {}
        for anchor in self.anchors:
            border_map[anchor] = {}
            # find all nodes in this split that border on nodes in the other splits
            for own_node in self.splits[anchor]:
                nbr_splits = self.get_nbr_splits(anchor, own_node)
                if len(nbr_splits) > 0:
                    for nbr_split in nbr_splits:
                        if not nbr_split in border_map[anchor]:
                            border_map[anchor][nbr_split] = []
                        border_map[anchor][nbr_split].append(own_node)
        self.border_map = border_map

    def print_splits(self):
        for split, split_data in self.splits.items():
            logging.info(
                f'{split} ({self.get_split_total(split_data)}) :: {split_data}')

    def run_negoriation(self):
        def get_updatable_nodes(receiver_split, donor_split, difference):
            # find node in the boardmap of the splits that have a value as close to the abs of difference
            # moving a node would change the difference by 2*node
            candidate_node = None
            # trying to find an update that will get this value as close to 0 as possible
            difference_to_clear = math.floor(abs(difference) / 2)
            best_intermediate_update = difference_to_clear
            for node_label in self.border_map[donor_split][receiver_split]:
                # check if the node value is lower than the difference that we are trying to reduce
                node_value = self.get_node(node_label).value
                if node_value > difference_to_clear:
                    continue
                # check if using this node will be improvement over the previously chosen node
                possible_difference = difference_to_clear - node_value
                if possible_difference < best_intermediate_update:
                    best_intermediate_update = possible_difference
                    candidate_node = node_label

            return candidate_node

        split_pairs = []
        # build a list of split anchor pairs to be iterated through
        for split_one, split_one_data in self.splits.items():
            for split_two, split_two_data in self.splits.items():
                if split_one == split_two:
                    continue
                if split_one not in self.border_map[split_two]:
                    continue
                split_pairs.append(sorted([split_one, split_two]))

        adjustments_completed = False
        while not adjustments_completed:
            logging.debug('= new negotiations round')
            adjustments_completed = True
            adjusted_pairs = []
            for split_pair in split_pairs:
                split_one = split_pair[0]
                split_two = split_pair[1]
                split_one_data = self.splits[split_one]
                split_two_data = self.splits[split_two]
                if sorted([split_one, split_two]) in adjusted_pairs:
                    continue
                # check the balance between both splits
                split_one_total = self.get_split_total(split_one_data)
                split_two_total = self.get_split_total(split_two_data)
                difference = split_one_total - split_two_total
                if abs(difference) < 2:
                    # the smallest difference that can be adjusted is 2 (with an update of a node with value 1)
                    continue
                if difference < 0:
                    donor_split = split_two
                    receiver_split = split_one
                else:
                    donor_split = split_one
                    receiver_split = split_two
                logging.debug(
                    f'-    {receiver_split} to receive from {donor_split} to cover diff {abs(difference)}')
                updatable = get_updatable_nodes(
                    receiver_split, donor_split, difference)
                if updatable:
                    logging.debug(
                        f'    -   {updatable} moved from {donor_split} to {receiver_split}')
                    adjusted_pairs.append(
                        sorted([donor_split, receiver_split]))
                    # update splits
                    self.splits[receiver_split].append(updatable)
                    self.splits[donor_split].remove(updatable)
                    # update border map
                    self.create_border_map()
                    adjustments_completed = False
                else:
                    logging.debug(f'    -   No suitable adjustments')

    def get_split_total(self, split):
        split_total = 0
        for node in split:
            split_total = split_total + self.get_node(node).value
        return split_total

    def get_graph_total(self):
        total = 0
        for node in self.nodes:
            total = total + node.value
        return total

    def get_nbr_splits(self, anchor, node):
        def get_split(node):
            for split, split_data in self.splits.items():
                if node in split_data:
                    return split[0]

        nbr_splits = []
        node_nbrs = self.get_node(node).links
        for nbr in node_nbrs:
            parent_split = get_split(nbr)
            nbr_splits.append(parent_split)
        nbr_splits = list(set(nbr_splits))
        if anchor in nbr_splits:
            nbr_splits.remove(anchor)
        return nbr_splits
