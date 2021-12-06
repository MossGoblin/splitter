from string import ascii_letters, ascii_lowercase, ascii_uppercase
from typing import List

def get_label(label_list: List):
    for label in ascii_uppercase:
        if label not in label_list:
            label_list.append(label)
            break
    
    return label, label_list