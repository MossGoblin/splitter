Definition
===
*Input*: ONE - A rectangle, composed of other rectangles. The format of the input is not essentialy important. TWO - a number of desired regions.

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
    *   What would that look like - N splits start with one node each. Then each split appropriates one of it's adjoining unclaimed nodes. Repeat until all nodes are claimed.
    *   Whenever a node is evaluated whether it could be adjoined to a split, if the node has already been claimed by another split, this limits the options for the network that needs to claim a new node. Ideally this should happen only at the end, when all free nodes are already claimed.
    *   Therefore it is better to avoid splits reaching each other for as long as possible.
    *   To achieve this, let's select starting nodes that are as far from each other as possible [see Anchors].
    *   Once we have a list of N nodes that are as far from each other as possible, we init splits with them and we can start adding free nodes to the splits [see Creep].
    *   Once all free nodes have been claimed, we can check for the balance of the splits. We know the ideal deviation of the splits. For example, if we have a network with total value of 25 (a starting rectangle of 5×5) and we want to split it into 4 regions, the real number target area of each split would be 6.25. That would give an ideal deviation of 0.25. Splits with values 6, 6, 6, 7 would satisfy the requirements, as the average deviation will be equal to 0.25.
    *   If the average deviation is too large, this means that there is at least one split with way too small value and at least one with way too large value.
    *   Here comes the negotiation. We can check each pair of neighbouring splits and see if changing ownership of any of the nodes that are on the border of the pair would improve the average deviation [see Negotiation]. We do this a few times until we stop improving the average deviation.
    *   And that should be enough.

**Anchors**
*   In order to ensure the growing splits will not come in contact with each other as long as possible, we need starting nodes (anchors) that are as far from each other as possible.
*   That 'as far from each other as possible' part is ensured by an alternative definition of the overall network - a distance graph. While we are building the graph, we calculate the minimum distance between each pair of nodes. At the end I decided to do this dynamically, while adding the nodes to the network one by one. This means recalculating all already recorded minimal distances when a new node is added, but I felt that it was worth the computational time. What I gain by going this way is the ability to add a new node after the network is complete. Not that the current algorithm requires it. So, we have the distance map. It is composed of a list of all minimal distances and the corresponding node pairs. And the list is, of course, ordered. Meaning that if the largest minimal distance is, say, 5, we have a list of all node pairs that are no less than 5 links apart. Same for pairs that are no less than 4 links apart and so on. The '0' distance part is the list of all nodes (each being 0 steps from itself).
*   From that distance map we need to extract N nodes that are are far from each other as possible. Initially I tried recursively checking if I can combine distance records, starting with the higher values, until I get an N-set of 'each-to-each' nodes. What whent wrong? I hit the max iteration depth with a relatively mediocre example network. Can you improve a recursive algorithm in that regard? I don't think so, but may be there's some trick I don't know. Irrelevant - when it did not work, I was pleased, as this kind of iteration is exactly the brute force approach I would like to avoid.
*   What worked (and that's one of the pieces I'm happy about) is... Well, I went a bit heuristic for a while. Imagine the network drawn on a board. If it is not too big (for a human brain, I mean) you can see the N nodes you need that are spread out as much as possible. All the rest is noise. It kind of bugged me that the object that you need (the N mini network you seek) actually exists within the big network and you only need to find it. However you have only descriptions of the nodes, which mean you have perfect setup for iterating nodes, not evaluating combinations of nodes.
*   So what I thought would be an ideal solution is to have the following:
    *   a definition of the object that is the mini metwork of nodes
    *   a way to encode that definition in the nodes themselves, so that all the nodes can be sieved, basd on that definition
* This did not exactly pan out. I tried several approaches. The main logic was that each node is part of many possible subnetworks, so if each of those networks is given an unique signature and all the nodes in that subnetwork write the signature down... Presumably the signature of the network would be some value that will show it's fitness for the purposes of this subnetwork selection.
* I had the foggy, but exciting idea to use the Fundamental Theorem of Arithmetic - the fact that each composite number can be represented by a unique product of prime numbers. So, the thinking was, if we give all the nodes special values - unique prime numbers - then the all possible combinations of nodes should result in unique composites. Then for each node you can easily find which composite it is part of. Then... No idea how to go on. I got lost there. An added difficulty is that all the prime values were unique, which means that the composited eploded in magnitude pretty quickly and each composite was presented in scientific notation, which simple meant debugging the idea was... unfeasable. You can look at the values all ou want, you can not get anything useful out of them. So I had to drop that prime idea (stash it for further exploartion, I mean. I still think it can be useful in another context).
* The next idea worked. I was still stuck with the idea that I have the objects that I need within the network and I just need to find them.
* I returned to the definition of the object I need:
  * There are exactly N nodes.
  * Each node is connected to each other node.
  * The smallest distance (we are talking about the minimal distances wihtin the network) is as large as possible.
* So... here's how it is done:
  * Start with all the longest distances (a.k.a. all pairs of nodes that have the largest smallest distance between them). This list of links is the 'cut-off'.
  * From the cut-off all links that connect to a node with less than N links WITHIN the cut-off. This ensures that the remaining nodes can be connected to each other with the same distance links. The remaining nodes are 'potentials'.
  * For each of the potentials:
    * Iterate all linked nodes within the cut-off. If the linked node can be connected within the cut-ff to the other potentials, we like it. If not - drop that linked node - it will not do.
    * When the only remaining potentials are the ones that can leank each to one another, count them - we need N ones. If we have more - remove the one that has a shorter average distance to the other potentials within the distribution
  * In the likely case that you can not find these N potentials with the distribution, lax the requirements one step. Create new cut-off, this time containing all distance pairs with the two longest distances. Check again within that cutoff.
  * The above explanation leaves much to be desired (will be, probably, rewritten at a later date), but the main point is that this algorithm did exactly wht I wanted it to do - checked if the desired N-subnetwork existed by shaking the distance cut-off so that the unsuitable nodes fall off then checked what remained. Meaning that I managed to find a way (even if convoluted) to treat the network as information (my desired collection of nodes) and noice (all the rest). Good.
* Of course we get more than one set of anchors, so we cache them for further iteration.
  

**Creep**

**Negotiation**