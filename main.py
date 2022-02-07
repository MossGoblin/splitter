from graph import Node, Graph
from workbench import WorkBench
import logging

SPLIT_COUNT = 3
'''
CRITICAL    50
ERROR       40
WARNING     30
INFO        20
DEBUG       10
NOTSET      0
'''
log_level = 10

def main():
    logging.info('START')
    logging.info('Reading network from .graph file')
    gr = create_graph_from_graph_file()
    gr.validate(rectangular=True)
    logging.info('Creating distance map')
    gr.find_distances()
    gr.get_peripheral_nodes(SPLIT_COUNT)
    logging.info('Starting split network creep')
    gr.creep_splits()
    gr.negotiate_borders()
    gr.print_splits()
    logging.info('Composing split array')
    gr.compose_split_graph()



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

def create_graph_from_graph_file(node_list_fliename: str = None) -> Graph:
    wb = WorkBench()
    node_array, node_dict = wb.read_nodes_from_graph_file(node_list_fliename, save_json=True)
    gr = Graph()
    for node_label, node_attributes in node_dict.items():
        label = node_label
        value = node_attributes['value']
        links = node_attributes['links']
        node = Node(label=label, value=value, links=links)
        gr.add_node(node, 0)
    gr.node_array = node_array
    return gr

if __name__ == '__main__':
    logging.basicConfig(filename='processing.log', format='[%(levelname)-5s] %(message)s', filemode='w', encoding='utf-8', level=log_level)
    main()