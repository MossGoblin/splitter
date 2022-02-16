from pydoc import replace
from string import ascii_letters, ascii_lowercase, ascii_uppercase
from typing import Dict, List
import json
import copy
import sympy
from sympy.ntheory.generate import prime


class WorkBench():
    label_list = {}
    label_list_level = 0

    def __init__(self, base_folder = None) -> None:
        self.base_folder = base_folder
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
            node_list_filename = f'splitter/{self.base_folder}node_list.json'
            node_list_filename = f'{self.base_folder}node_list.json'
        with open(node_list_filename, 'r') as file:
            node_dict = json.load(file)
        return node_dict



    def read_nodes_from_graph_file(self, graph_filename: str = None, save_json: bool = False) -> Dict:
        def generate_similar_nbrs(array, row_dot, element_dot, index):
                nbrs = []
                nbr_indeces = [(-1, 0), (0, 1), (1, 0), (0, -1)]
                for nbr_row, nbr_element in nbr_indeces:
                    row_index = row_dot + nbr_row
                    element_index = element_dot + nbr_element
                    if row_index > -1 and row_index < len(array) and element_index > -1 and element_index < len(array[row_dot]):
                        if array[row_index][element_index] == index:
                            element = (array[row_index][element_index], row_index, element_index)
                            nbrs.append(element)
                return nbrs

        def get_neighbours(graph_array, row_dot, element_dot):
            nbrs = []
            nbr_indeces = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            for nbr_row, nbr_element in nbr_indeces:
                row_index = row_dot + nbr_row
                element_index = element_dot + nbr_element
                if row_index > -1 and row_index < len(graph_array) and element_index > -1 and element_index < len(graph_array[row_dot]):
                    nbrs.append(graph_array[row_index][element_index])
            return list(set(nbrs))

        def position_exists(array, row_index, element_index):
            if row_index > -1 and row_index < len(array) and element_index > -1 and element_index < len(array[row_index]):
                return True
            return False

        graph_dict = {}
        graph_array = []
        if not graph_filename:
            graph_filename = f'{self.base_folder}basic.graph'
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
        
        node_array = []
        s_gen = SignatureGenerator()
        s_iter = iter(s_gen)

        for row_index, row in enumerate(graph_array):
            node_array.append([])
            for element_index, element in enumerate(row):
                # get all nbrs with the same node index
                nbrs = generate_similar_nbrs(graph_array, row_index, element_index, element)
                replacement_found = False
                for nbr in nbrs:
                    # if the nbr has already been assigned a replacement - use it
                    if position_exists(node_array, nbr[1], nbr[2]):
                        replacement = node_array[nbr[1]][nbr[2]]
                        replacement_found = True
                        break
                if not replacement_found:
                    replacement = next(s_iter)
                node_array[row_index].append(replacement)

        for row_index, row in enumerate(node_array):
            for element_index, element in enumerate(row):
                if element not in graph_dict:
                    graph_dict[element] = {}
                    graph_dict[element]["links"] = []
                nbrs = get_neighbours(node_array, row_index, element_index)
                for nbr in nbrs:
                    if nbr == element:
                        continue
                    if nbr not in graph_dict[element]["links"]:
                        graph_dict[element]["links"].append(nbr)
        for node in graph_dict:
            node_count = 0
            for row in node_array:
                node_count = node_count + row.count(node)
            graph_dict[node]["value"] = node_count

        if save_json:
            filename = f'{self.base_folder}json_data/graph_{len(node_array)}_{len(node_array[0])}.json'
            with open(filename, 'w') as json_output:
                json.dump(graph_dict, json_output)

        return node_array, graph_dict

class SignatureGenerator():
    def __init__(self, case = 0):
        if case > 1:
            raise AttributeError('Order can be only 0 for lowercase and 1 for uppercase')
        self.offset = 65 if case == 1 else 97

    def __iter__(self):
        self.index = 0
        self.sig = 'a'
        self.order = 0
        return self

    def __next__(self):
        if self.index < 676:
            clean_prefix = int(self.index/26)
            clean_suffix = self.index % 26
            
            postfix_index = self.offset + clean_suffix
            postfix = chr(postfix_index)
            if clean_prefix > 0:
                prefix_index = self.offset + clean_prefix - 1
                prefix = chr(prefix_index)
                self.sig = f'{prefix}{postfix}'
            else:
                self.sig = f'{postfix}'
        else:
            raise StopIteration

        self.index = self.index + 1
        return self.sig
    
