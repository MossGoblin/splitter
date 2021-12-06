import toolbox
from graph import Node, Graph
import workbench as wb

def main():
    gr = Graph()
    for count in range(15):
        new_node = Node(count, [count + 1, count + 2])
        gr.add_node(new_node)
    
    print(gr)
    pass


if __name__ == '__main__':
    main()