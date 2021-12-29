from graph import Node, Graph
from workbench import WorkBench

def main():
    gr = create_graph_from_graph_file()
    gr.validate()
    print(gr)
    gr.find_distances()
    new_node = Node("j", 4, ["g", "h", "i"])
    # gr.add_node_to_distance_map(new_node)
    print(gr.print_distance_map())
    gr.get_peripheral_nodes(3)

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
    node_dict = wb.read_nodes_from_graph_file(node_list_fliename, save_json=True)
    gr = Graph()
    for node_label, node_attributes in node_dict.items():
        label = node_label
        value = node_attributes['value']
        links = node_attributes['links']
        node = Node(label=label, value=value, links=links)
        gr.add_node(node, 0)
    return gr

if __name__ == '__main__':
    main()