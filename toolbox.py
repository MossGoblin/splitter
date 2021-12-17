from string import ascii_letters, ascii_lowercase, ascii_uppercase
from typing import Dict, List
import json

def get_label(label_list: List):
    for label in ascii_uppercase:
        if label not in label_list:
            label_list.append(label)
            break
    
    return label, label_list

def read_node_list(node_list_filename: str) -> Dict:
    if not node_list_filename:
        node_list_filename = 'splitter/node_list.json'
    with open(node_list_filename, 'r') as file:
        node_dict = json.load(file)
    return node_dict