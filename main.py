from graph import Node, Graph
from workbench import WorkBench

def main():
    # MOTHBALLED WHILE REWORKING NODE
    # gr = create_graph_from_file()
    # print(gr)
    # gr.validate()
    # split_deviation = gr.calculate_deviation(2)
    # print(f'split_deviation: {split_deviation}')
    # gr.process_graph(3)
    wb = WorkBench()
    for x in range(30):
        label = wb.get_label()
        print(label)
    pass


def create_graph_from_file(node_list_fliename: str = None) -> Graph:
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

if __name__ == '__main__':
    main()