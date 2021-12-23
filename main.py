from graph import Node, Graph
from workbench import WorkBench

def main():
    gr = create_graph_from_file()
    gr.validate()
    print(gr)
    gr.find_distances()

def create_graph_from_file(node_list_fliename: str = None) -> Graph:
    wb = WorkBench()
    node_dict = wb.read_node_list(node_list_fliename)
    gr = Graph()
    for node_label, node_attributes in node_dict.items():
        label = int(node_label)
        signature = wb.get_label()
        value = node_attributes['value']
        links = node_attributes['links']
        node = Node(label=label, value=value, signature=signature, links=links)
        gr.add_node(node, 0)
    return gr

if __name__ == '__main__':
    main()