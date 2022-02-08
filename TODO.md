*   PROBLEMS:
        *   FIXED - peripherals fail on 2_basic.graph for 3 splits - results in 5 anchors
        *   FIXED - peripherals fail on 3_basic.graph for 4 splits - results in 5 anchors - FIXED
        *   FIXED - peripherals fail on 5_basic.graph for 5 splits - results in 6 anchors - FIXED
        *   FIXED - negotiations not performing well on 3_basic.graph - e or c could be grouped with d
        *   FIXED - nergotiations failing for 6_basic - Z ends up in incorrect split
        *   FIXED - exception when processing 6_basic for 5 splits - Intermittent bug, receiver S not a neighbour of Z (recheck nbrs)
        * FIXED - negotiations can lead to split discontinuity - example 7_basic for 4 and 3
        *   DISCONTINUITY FIXED
        *   **FAILS** on graph 9, split count 5

*   TODO:
        *   needs optimization; discontinuity check limits the effect of negotiation
        *   ITERATE anchors for best solution
    