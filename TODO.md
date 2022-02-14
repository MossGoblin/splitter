*   PROBLEMS:
        [x] peripherals fail on 2_basic.graph for 3 splits - results in 5 anchors
        [x] peripherals fail on 3_basic.graph for 4 splits - results in 5 anchors - FIXED
        [x] peripherals fail on 5_basic.graph for 5 splits - results in 6 anchors - FIXED
        [x] negotiations not performing well on 3_basic.graph - e or c could be grouped with d
        [x] nergotiations failing for 6_basic - Z ends up in incorrect split
        [x] exception when processing 6_basic for 5 splits - Intermittent bug, receiver S not a neighbour of Z (recheck nbrs)
        [x] negotiations can lead to split discontinuity - example 7_basic for 4 and 3
        [x] negotiation fails on graph 9, split count 5
            * something wrong with picking split pairs for negotiation
              * duplicate split_pairs in split_pairs list
        [ ] File "d:\Codee\package_splitter\splitter\graph.py", line 796, in check_if_node_removal_breaks
                        start_node = nbrs[0]
                        IndexError: list index out of range
            *       Seems like it is an extreme case of a single node, separated from the split ??
        [ ] ?? Splits mean deviation may be calculated inacurately - pyhon disagrees with excel
*   TODO:
        *   DONE - needs optimization; discontinuity check limits the effect of negotiation
        *   DONE - iterate anchors for best solution
    