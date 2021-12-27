from string import ascii_letters, ascii_lowercase, ascii_uppercase
from typing import Dict, List
import json
import copy

CONSOLE_DUMP = False


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


def report(message):
    if CONSOLE_DUMP:
        print(message)
