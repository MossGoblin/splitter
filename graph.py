from typing import Dict, List
import workbench as wb
import json
import copy
import logging

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

    def validate(self):
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
        logging.debug('\n')

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
        logging.debug('\n')

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
                    distance_distribution[distance].append(
                        sorted([node.label, distant_node_distance]))
                elif sorted([node.label, distant_node_distance]) not in distance_distribution[distance]:
                    distance_distribution[distance].append(
                        sorted([node.label, distant_node_distance]))
        logging.info(f'Distance distrubution built')
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
        # cut_off = 1 # DBG start from 1 in order to check both distance groups 2 and 3
        cut_off = 0
        while not found:
            cut_off = cut_off + 1
            peripherals_list = []
            reduced_distribution = self.get_reduced_distribution(
                distance_distribution, cut_off)
            distribution_flatmap = self.flatten_reduced_distribution(
                reduced_distribution)

            logging.debug(f'SIFTING for {node_number} peripherals at cut off {cut_off}')
            peripherals_list, found = self.sift_for_peripherals(
                distribution_flatmap, node_number)
            if found:
                logging.info(f'Periferals found')
                for peripherals in peripherals_list:
                    logging.debug('{peripherals}')
                self.peripherals_list = peripherals_list
                return peripherals_list[0]
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
            # DBG var
            can_continue = nodes_match and not nodes_overshot and pairs_match and not pairs_overshot
            # DBG var
            overshot = nodes_overshot or pairs_overshot
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

        def reduce_group(node_links, distribution, flat_distribution):
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

            return group

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
                node_links, distribution, flat_distribution)
            candidate_group.append(node)

            if len(candidate_group) >= target:
                if sorted(candidate_group) not in peripherals_list:
                    peripherals_list.append(sorted(candidate_group))

        if len(peripherals_list) == 0:
            return [], False
        return peripherals_list, True

    def creep_splits(self, anchors):
        '''
        Initiates one split network per anchor
        Starts acquiring adjacent nodes to each anchor, taking into account the size of the adjacent nodes - larger are added slower
        '''

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
            tick = tick + 1
            logging.debug(f'\nTick [ {tick} ]')
            for anchor in anchors:
                logging.debug(f'Split {anchor} at {creep_map[anchor]}')
            # add one tick to each creep
            for anchor in anchors:
                prospects_updated = False
                creep_map[anchor] = creep_map[anchor] + 1
                # check in each creep prospect if there is a node to be acquired
                # make an aeditable copy of the creep prospects to work with
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
        for anchor in anchors:
            logging.debug(f'{splits[anchor][0]} > {splits[anchor]}')
