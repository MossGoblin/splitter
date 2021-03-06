import itertools
from typing import List

import json
import copy
import logging
import math
from string import ascii_letters
from colored import bg


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
    node_array = []  # an array, read from the input
    split_array = []  # an array, displaying the splits
    node_map = {}  # an enchanced map of nodes, separated by level
    map_total = 0  # the total weight of all the level 0 nodes
    distance_map = {}  # an enchanced map of nodes, separated by level
    split_count = 0  # the total number of target splits
    anchor_set_list = []  # a list of all anchor groups
    anchors = []  # a list of anchors selected from peripherals_list
    splits = {}  # a dictionary of all split networks, build around anchors
    split_totals = {} # a list of the total values of each split
    symbol_map = {} # a map of split indeces to digits to be used in the csv output

    def __init__(self, split_count: int, base_folder=None):
        self.split_count = split_count
        self.base_folder = base_folder

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
        # calculate target values
        self.split_average = self.total_value / self.split_count
        self.mean_deviation = self.split_average % 1
        logging.info(f'.. Graph total: {self.total_value}')
        logging.info(f'.. Graph mean deviation: {self.mean_deviation}')

    def find_distances(self) -> None:
        '''
        Calculate the minimal distances between each pair of nodes
        and store them in self.distance_map
        '''
        logging.info('Creating distance map')
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
        '''
        Add new node to self.distance_map
        '''
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
        '''
        Adjust the distances from the new node to the already processed nodes
        '''
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
        '''
        Check the list of already recorded distances and adjust them if the inclusion of a new node changes any of them
        '''
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
        '''
        Generate distance pairs from self.distance_map
        '''
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
        '''
        Check if a node has nbrs in the map so far
        '''
        if len(self.distance_map) == 0:
            return True
        # Check for Continuous Map Growth
        for graph_node in self.distance_map:
            if graph_node.label in node.links:
                return True
        return False

    def print_distance_map(self):
        '''
        Logging
        '''
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

    def get_peripheral_nodes(self):
        '''
        Find [node_number] nodes that are as far away from each other as possible
        definition of "as far away from each other as possible":
            the minimum distance between any two of the selected nodes is as large as possible
        '''
        logging.info('Acquiring anchor sets')
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

        '''
        Process:
            *   Select the peripherals
            *   Try to find the requisite number in the highest distance category
            *   If there is no suitable combination, add the lower category and search in the highest two
            *   If needed, repeat by adding another one and so on
        
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
                f'SIFTING for {self.split_count} anchors at cut off {cut_off}')
            peripherals_list, found = self.sift_for_peripherals(
                distribution_flatmap, self.split_count)
            if found:
                logging.info(f'.. {len(peripherals_list)} Anchor sets found:')
                for peripherals in peripherals_list:
                    logging.info(f'{peripherals}')
                self.anchor_set_list = peripherals_list
                self.anchors = peripherals_list[0]
                return self.anchors
            else:
                logging.debug('No anchor sets found')

    def search_reduced_distribution_for_peripherals(self, distribution, group, count, checked_pairs):
        '''
        Find if there is a suitable group of nodes in a given cut-off of self.distance_map
        '''
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
        1. remove nodes with less than target-1 links
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
                        evaluated_nodes[node] = get_link_average(
                            node, distribution, reduced_group)
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
        self.split_totals = {}
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
            for split, split_data in splits.items():
                logging.debug(f'[{split[0]}]: {split_data}')
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
                        logging.debug('   -   already claimed')
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
        logging.info(f'. Creep completed in {tick} ticks')

    def negotiate_borders(self):
        logging.info('. Start negotiations')
        self.run_negoriation()
        logging.info('.. Negotiations complete')

    def valid_border_map(self, border_map):
        '''
        Check if every split in the border map appears in the records of the splits it has in it's own record
        '''
        for anchor, anchor_data in border_map.items():
            for nbr in anchor_data.keys():
                if not anchor in border_map[nbr].keys():
                    return False
        return True

    def create_border_map(self):
        '''
        Create a map of border nodes
        All nodes have been assigned by the creep
        For each pair of bordering splits there are two sets of border nodes:
        - nodes that are part of split one and ones that are part of split two
        The border map has a part for each split and has it's border nodes for each bordering split
        '''
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
        if not self.valid_border_map(border_map):
            logging.error('Border map is invalid')
            raise Exception('Border map is invalid')
        self.border_map = border_map
        for split_anchor, border_data in self.border_map.items():
            logging.debug(f'Border nodes for {split_anchor}: {border_data}')

    def print_splits(self):
        '''
        Logging
        '''
        for split, split_data in self.splits.items():
            logging.info(
                f'{split} ({self.get_split_total(split_data)}) :: {split_data}')

    def run_negoriation(self):
        '''
        Iterate through all pairs of bordering splits
        Check if moving any of the border nodes from one of the splits to the other will improve the average deviation of the splits
        If so, move the split, recalculate the border map and repeat
        Stop when it is determined that no border node change will improve the averate deviation
        '''
        def get_updatable_nodes(recipient_split_index, donor_split_index, difference):
            # find node in the boardmap of the splits that have a value as close to the abs of difference
            # moving a node would change the difference by 2*node
            candidate_node = None
            # trying to find an update that will get this value as close to 0 as possible
            difference_to_clear = math.floor(abs(difference) / 2)
            best_intermediate_update = difference_to_clear
            try:
                for node_label in self.border_map[donor_split_index][recipient_split_index]:
                    # check if the node value is lower than the difference that we are trying to reduce
                    node_value = self.get_node(node_label).value
                    if node_value > difference_to_clear:
                        continue
                    # check if using this node will be improvement over the previously chosen node
                    possible_difference = difference_to_clear - node_value
                    if possible_difference < best_intermediate_update:
                        best_intermediate_update = possible_difference
                        if self.check_if_node_removal_breaks(donor_split_index, node_label):
                            candidate_node = node_label
            except Exception as e:
                logging.error(e)
                raise e
            return candidate_node

        adjustments_completed = False
        border_map_creation_logged = False
        while not adjustments_completed:
            if not border_map_creation_logged:
                logging.info('. Creating border map')
                border_map_creation_logged = True
            self.create_border_map()
            split_pairs = []
            # build a list of split anchor pairs to be iterated through
            for split_one, split_two in itertools.combinations(self.splits.keys(), 2):
                if not split_one in self.border_map[split_two]:
                    continue
                split_pairs.append([split_one, split_two])
            logging.debug(split_pairs)

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
                # check the balance between the splits
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
                    f'-    {donor_split} to provide to {receiver_split} to cover diff {abs(difference)}')
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
                    adjustments_completed = False
                    break
                else:
                    logging.debug(f'    -   No suitable adjustments')

        totals = {}
        for anchor in self.anchors:
            totals[anchor] = 0
            for node in self.splits[anchor]:
                totals[anchor] = totals[anchor] + self.get_node(node).value
                self.split_totals[anchor] = totals[anchor]

        for anchor in self.anchors:
            logging.info(
                f'{self.splits[anchor][0]} > {totals[anchor]} > {self.splits[anchor]}')

    def get_split_total(self, split):
        '''
        The sum of all node values in a split
        '''
        split_total = 0
        for node in split:
            split_total = split_total + self.get_node(node).value
        return split_total

    def get_graph_total(self):
        '''
        The sum of all node values in the network
        '''
        total = 0
        for node in self.nodes:
            total = total + node.value
        return total

    def get_nbr_splits(self, anchor, node):
        '''
        Return the indices of all splits that a node is bordering
        '''
        def get_split(node):
            for split, split_data in self.splits.items():
                if node in split_data:
                    return split

        nbr_splits = []
        node_nbrs = self.get_node(node).links
        for nbr in node_nbrs:
            parent_split = get_split(nbr)
            nbr_splits.append(parent_split)
        nbr_splits = list(set(nbr_splits))
        if anchor in nbr_splits:
            nbr_splits.remove(anchor)
        return nbr_splits

    def compose_split_graph(self):
        '''
        Compose an array where the node labels are replaced with the indeces of the splits the nodes are part of
        '''
        def get_split(node):
            for split, split_nodes in self.splits.items():
                if node in split_nodes:
                    return split

        logging.info('Composing split array')
        self.split_array = copy.deepcopy(self.node_array)
        for row_index, row in enumerate(self.node_array):
            for node_index, node in enumerate(row):
                self.split_array[row_index][node_index] = get_split(node)
        logging.info(f'.. Split array prepared')
        split_array_string = '\n'
        with open(f'{self.base_folder}result.graph', 'w') as result_file:
            for row in self.split_array:
                for node in row:
                    result_file.write(f'{node}'.ljust(2))
                    split_array_string = split_array_string + \
                        f'{node}'.ljust(2)
                result_file.write('\n')
                split_array_string = split_array_string + '\n'
        logging.info(split_array_string)
        self.build_csv_output_file()

    def build_csv_output_file(self):
        if self.split_count > 9:
            logging.error(
                'Can not export a .csv file : the split count is too large.')
        symbol_list = list([x for x in range(1, 10)])
        if self.split_count > 10 and self.split_count < 61:
            symbol_list.extend(list([x for x in ascii_letters]))
        # map nodes to symbols
        counter = 0
        for row in self.split_array:
            for node in row:
                if node in self.symbol_map:
                    continue
                self.symbol_map[node] = None
                self.symbol_map[node] = symbol_list[counter]
                counter = counter + 1
        with open(f'{self.base_folder}result.csv', 'w') as result_csv:
            for row in self.split_array:
                for node in row:
                    result_csv.write(str(self.symbol_map[node]) + ',')
                result_csv.write('\n')

    def check_if_node_removal_breaks(self, split_index, removable):
        '''
        Check if removing a node from a split will break the split in two (or more) parts
        '''
        # Check if removing a node from a split will break it into two graphs
        # Get the split, corresponding to the split index
        for split_anchor, split_data in self.splits.items():
            if split_anchor == split_index:
                split = split_data
                break
        # Get the nbrs of the candidate node within the split
        nbrs = []
        node = self.get_node(removable)
        for nbr in node.links:
            if not nbr in split:
                continue
            nbrs.append(nbr)
        # Remove the candidate node from the split
        reduced_split = copy.deepcopy(split)
        reduced_split.remove(removable)
        # Create a copy of the graph, containing ONLY links connecting nodes from the split
        reduced_split_node_list = []
        for node_label in reduced_split:
            node = self.get_node(node_label)
            reduced_split_node_list.append(node)
        # Crate connections network for the reduced split graph, starting with one of the nbrs
        # Get all the split nodes, connected to one of the nbrs
        if len(nbrs) == 0:
            error_mesage = f'Node {removable} is somehow separated from its split'
            logging.error(error_mesage)
            raise Exception(error_mesage)
        start_node = nbrs[0]
        connected_nodes = self.get_split_connected_nodes(
            start_node, reduced_split_node_list)
        # If all nbrs are in the connections network, then the reduced split graph is not broken
        for nbr in nbrs:
            if not self.get_node(nbr) in connected_nodes:
                return False
        return True

    def get_split_connected_nodes(self, start_node, split_node_list):
        '''
        Get all the nodes within a split that are connected to a given node in the same split
        '''
        # fail check
        if self.get_node(start_node) not in split_node_list:
            raise Exception(
                f'Split graph brakage fail: node {start_node} is not in the split')

        connected_nodes = []
        processed_nodes = []
        process_queue = []
        connected_nodes.append(self.get_node(start_node))
        processed_nodes.append(start_node)
        process_queue.append(split_node_list[0])
        while len(process_queue) > 0:
            next_node = process_queue.pop()
            for nbr in next_node.links:
                if not self.get_node(nbr) in split_node_list:
                    continue
                if nbr in processed_nodes:
                    continue
                processed_nodes.append(nbr)
                connected_nodes.append(self.get_node(nbr))
        return connected_nodes

    def find_best_split(self):
        '''
        Iterate through all sets of anchors and cache the results
        Compare results and output the best, based on the average deviation of the splits
        '''
        logging.info('Iterating anchor sets')
        self.result_cache = {}
        best_result_mean = self.total_value
        best_result_anchor_set = None
        for anchor_set in self.anchor_set_list:
            logging.info(f'Processing anchors {anchor_set}')
            anchor_set_label = ''.join(anchor_set)
            self.result_cache[anchor_set_label] = {}
            self.anchors = anchor_set
            result = {}
            result['anchors'] = anchor_set
            # creep
            self.splits = {}
            self.creep_splits(anchor_set)
            self.negotiate_borders()
            result['splits'] = self.splits
            result['split values'] = self.split_totals
            mean_splits_deviation = 0
            total_splits_deviation = 0
            for split_total, split_total_value in self.split_totals.items():
                total_splits_deviation = total_splits_deviation + \
                    abs(split_total_value - self.split_average)
            mean_splits_deviation = total_splits_deviation / self.split_count
            result['mean deviation'] = mean_splits_deviation
            anchor_set_result_string = f'.. Splits mean deviation {mean_splits_deviation}'
            if mean_splits_deviation < best_result_mean:
                anchor_set_result_string = anchor_set_result_string + f' -> provisionally best'
                best_result_mean = mean_splits_deviation
                best_result_anchor_set = anchor_set
            logging.info(anchor_set_result_string)
            self.result_cache[anchor_set_label] = result

        logging.info(f'Best anchor set: {best_result_anchor_set}')
        logging.info(f'Best splits mean deviation : {best_result_mean}')
        self.splits = self.result_cache[''.join(
            best_result_anchor_set)]['splits']
        self.print_splits()
        self.compose_split_graph()
        self.colour_output()

    def process(self):
        self.find_distances()
        self.get_peripheral_nodes()
        self.find_best_split()

    def colour_output(self):
        row_str = ''
        for row_index, row in enumerate(self.node_array):
            for element_index, element in enumerate(row):
                split_code = self.split_array[row_index][element_index]
                color_code = self.symbol_map[split_code]
                row_str = row_str + f"{bg(color_code)}" + f"{element}".ljust(2)
            row_str = row_str + bg(0)
            row_str = row_str + '\n'
        print(row_str)