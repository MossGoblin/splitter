from datetime import datetime
from graph import Node, Graph
from workbench import WorkBench
import logging


BASE_FOLDER = 'data/'
SPLIT_MAXIMUM = 9
SPLIT_COUNT = 3
''' 
CRITICAL    50
ERROR       40
WARNING     30
INFO        20
DEBUG       10
NOTSET      0
'''
log_level = logging.DEBUG

def main():
    logging.info('START')
    start_time = datetime.utcnow()
    gr = create_graph_from_graph_file(split_count = SPLIT_COUNT)
    gr.process()
    run_time = datetime.utcnow() - start_time
    logging.info(f'TOTAL TIME: {run_time} s')


def create_graph_from_json_file(node_list_fliename: str = None) -> Graph:
    wb = WorkBench()
    node_dict = wb.read_node_list(node_list_fliename)
    gr = Graph()
    for node_label, node_attributes in node_dict.items():
        label = node_label
        value = node_attributes['value']
        links = node_attributes['links']
        node = Node(label=label, value=value, links=links)
        gr.add_node(node, 0)
    return gr


def create_graph_from_graph_file(node_list_fliename: str = None, split_count: int = None) -> Graph:
    if split_count == 1 or split_count == 0:
        raise ValueError('Split count must be larger than 2 (missing split count defaults to 2)')
    if split_count > SPLIT_MAXIMUM:
        raise ValueError(f'Split maximum can not exceed {SPLIT_MAXIMUM}')
    if not split_count:
        split_count = 2
    logging.info('Reading network from .graph file')
    wb = WorkBench(base_folder=BASE_FOLDER)
    node_array, node_dict = wb.read_nodes_from_graph_file(node_list_fliename, save_json=True)
    gr = Graph(split_count, base_folder=BASE_FOLDER)
    for node_label, node_attributes in node_dict.items():
        label = node_label
        value = node_attributes['value']
        links = node_attributes['links']
        node = Node(label=label, value=value, links=links)
        gr.add_node(node, 0)
    gr.node_array = node_array
    gr.validate(rectangular=True)
    return gr


if __name__ == '__main__':
    logging.basicConfig(filename=f'{BASE_FOLDER}processing.log', format='[%(levelname)-5s] %(message)s', filemode='w', encoding='utf-8', level=log_level)
    main()