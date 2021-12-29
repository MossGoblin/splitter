from string import ascii_letters, ascii_lowercase, ascii_uppercase
from typing import Dict, List
import json
import copy

CONSOLE_DUMP = True


class WorkBench():
    label_list = {}
    label_list_level = 0

    def __init__(self) -> None:
        for letter in ascii_lowercase:
            self.label_list[letter] = False

    def get_label(self):
        new_label = self.extract_label()
        if new_label == None:
            self.add_level_to_labels()
            new_label = self.extract_label()
        self.label_list[new_label] = True
        return new_label

    def extract_label(self):
        new_label = None
        for label, used in self.label_list.items():
            if not used:
                new_label = label
                break
        return new_label

    def add_level_to_labels(self):
        new_label_list = copy.deepcopy(self.label_list)
        self.label_list_level = self.label_list_level + 1
        for new_prefix in ascii_lowercase:
            for label in ascii_lowercase:
                new_label = new_prefix + label
                new_label_list[new_label] = False
        self.label_list = new_label_list

    def read_node_list(self, node_list_filename: str) -> Dict:
        if not node_list_filename:
            node_list_filename = 'splitter/node_list.json'
            node_list_filename = 'node_list.json'
        with open(node_list_filename, 'r') as file:
            node_dict = json.load(file)
        return node_dict

    def read_nodes_from_graph_file(self, graph_filename: str = None, save_json: bool = False) -> Dict:

        def get_neighbours(graph_array, row_dot, element_dot):
            nbrs = []
            nbr_indeces = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            for nbr_row, nbr_element in nbr_indeces:
                row_index = row_dot + nbr_row
                element_index = element_dot + nbr_element
                if row_index > -1 and row_index < len(graph_array[row_dot]) and element_index > -1 and element_index < len(graph_array):
                    nbrs.append(graph_array[row_index][element_index])
            return list(set(nbrs))

        graph_dict = {}
        graph_array = []
        if not graph_filename:
            graph_filename = 'basic.graph'
        with open(graph_filename, 'r') as file:
            lines = file.readlines()
            line_length = 0
            for line in lines:
                row = [char for char in line]
                if '\n' in row:
                    row.remove('\n')
                if line_length > 0:
                    if len(row) != line_length:
                        raise Exception(
                            'Graph file seems to have lines of different length')
                else:
                    line_length = len(row)
                graph_array.append(row)
        for row_index, row in enumerate(graph_array):
            for element_index, element in enumerate(row):
                if element not in graph_dict:
                    graph_dict[element] = {}
                    graph_dict[element]["links"] = []
                nbrs = get_neighbours(graph_array, row_index, element_index)
                for nbr in nbrs:
                    if nbr == element:
                        continue
                    if nbr not in graph_dict[element]["links"]:
                        graph_dict[element]["links"].append(nbr)
                print(nbrs)
        for node in graph_dict:
            node_count = 0
            for row in graph_array:
                node_count = node_count + row.count(node)
            graph_dict[node]["value"] = node_count

        if save_json:
            filename = f'graph_{len(graph_array)}_{len(graph_array[0])}.json'
            with open(filename, 'w') as json_output:
                json.dump(graph_dict, json_output)

        return graph_dict


def report(message):
    if CONSOLE_DUMP:
        print(message)
