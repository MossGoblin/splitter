Definition
===
*Input*: ONE - A rectangle, comprised of other rectangles. The format of the input is not essentialy important. TWO - a number of desired regions.

*Task*: Create an algorithm that takes a rectangle composed of multiple rectangles (input ONE) and splits it into N (input TWO) portions, with areas as close to each other as possible.

*Conditions*: Try to avoid bruteforcing the problem through recursion. The task has no intended real-life benefit, the goal is to find an interesting solution


Development
===
**Plan of attack**:
*   Weapon of choice
    *   Create a network out of the input - each rectangle is a node, with value equal to the rectangle area. The edges of the network reflect the adjacency of rectangles.
    *   Let's call the resulting divisions of the graph 'splits'. 
*   Outline of a brute force approach - Select a node. Add adjacent nodes (breadth first iteration) until a total value of (total area / N) is reached (as close as possible). Repeat the process within the remaining unselected portion of the network N-2 more times. Calculate the average deviation of the splits and compare to the ideal average deviation ((total value % N) / N). If there is a split with larger deviation, roll back and try again with different starting nodes for each split.
*   Selected method:
    *   Try to create the splits simoultaneously, instead of one by one.
    *   What would that look like - N splits start with one node each. Then each split appropriates one of it's adjoining free (not claimed already by any split) nodes. Repeat until all nodes are claimed.
    *   Whenever a node is evaluated whether it it could be adjoined to a split, if the node is not free, this limits the options for the network that needs to claim a new node. Ideally this should happen only at the end, when all free nodes are already claimed.
    *   Therefore it is better to avoid splits reaching each other for as long as possible.
    *   To achieve this, let's select starting nodes that are as far from each other as possible [see Anchors].
    *   Once we have a list of N nodes that are as far from each other as possible, we init splits with them and we can start adding free nodes to the splits [see Creep].
    *   Once all free nodes have been claimed, we can check for the balance of the splits. We know the ideal deviation of the splits. For example, if we have a network with total value of 25 (a starting rectangle of 5×5) and we want to split it into 4 regions, the real number target area of each split would be 6.25. That would give an ideal deviation of 0.25. Splits with values 6, 6, 6, 7 would satisfy the requirements, as the average deviation will be equal to 0.25.
    *   If the average deviation is too large, this means that there is at least one split with way too small value and at least one with way too large value.
    *   Here somes the negotiation. We can check each pair of neighbouring splits and see if changing ownership of any of the nodes that are on the border of the pair would improve the average deviation [see Negotiation]. We do this a few times until we stop improving the average deviation.
    *   And that should be enough.

**Anchors**
*   In order to ensure the growing splits will not come in contact with each other as long as possible, we need starting nodes (anchors) that are as far from each other as possible.