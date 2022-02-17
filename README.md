Definition
===

*Task*: Create an algorithm that takes a rectangle composed of multiple rectangles (input ONE) and splits it into N (input TWO) portions, with areas as close to each other as possible.

*Input*: ONE - A rectangle, composed of other rectangles. The format of the input is not essentially important. TWO - a number of desired regions.

*Conditions*: Try to avoid brute forcing the problem through recursion. The task has no intended real-life benefit, the goal is to find an interesting solution

Development
===

**Plan of attack**:

* Weapon of choice
  * Create a network out of the input - each rectangle is a node, with value equal to the rectangle area. The edges of the network reflect the adjacency of rectangles.
  * Let's call the resulting divisions of the graph 'splits'. 
* Outline of a brute force approach - Select a node. Add adjacent nodes (breadth first iteration) until a total value of (total area / N) is reached (as close as possible). Repeat the process within the remaining unselected portion of the network N-2 more times. Calculate the average deviation of the splits and compare to the ideal average deviation ((total value % N) / N). If there is a split with larger deviation, roll back and try again with different starting nodes for each split.
* Selected method:
  * Try to create the splits simultaneously, instead of one by one.
  * What would that look like - N splits start with one node each. Then each split appropriates one of it's adjoining unclaimed nodes. Repeat until all nodes are claimed. Essentially a voronoi fill with a twist. [see Creep]
  * Whenever a node is evaluated whether it could be adjoined to a split, if the node has already been claimed by another split, this limits the options for the network that needs to claim a new node. Ideally this should happen only at the end, when all free nodes are already claimed.
  * Therefore it is better to avoid splits reaching each other for as long as possible.
  * To achieve this, let's select starting nodes that are as far from each other as possible [see Anchors].
  * Once we have a list of N nodes that are as far from each other as possible, we init splits with them and we can start adding free nodes to the splits [see Creep].
  * Once all free nodes have been claimed, we can check for the balance of the splits. We know the ideal deviation of the splits. For example, if we have a network with total value of 25 (a starting rectangle of 5×5) and we want to split it into 4 regions, the real number target area of each split would be 6.25. That would give an ideal deviation of 0.25. Splits with values 6, 6, 6, 7 would satisfy the requirements, as the average deviation will be equal to 0.25.
  * If the average deviation is too large, this means that there is at least one split with way too small value and at least one with way too large value.
  * Here comes the negotiation. We can check each pair of neighbouring splits and see if changing ownership of any of the nodes that are on the border of the pair would improve the average deviation [see Negotiation]. We do this a few times until we stop improving the average deviation.
  * And that should be enough.

**Anchors**

* In order to ensure that the growing splits will not come in contact with each other for as long as possible, we need starting nodes (anchors) that are as far from each other as possible.
* That '*as far from each other as possible*' part is ensured by an alternative definition of the overall network - a distance graph. While we are building the graph, we calculate the minimum distance between each pair of nodes. At the end I decided to do this dynamically, while adding the nodes to the network one by one. This means recalculating all already recorded minimal distances when a new node is added, but I felt that it was worth the computational time. What I gain by going this way is the ability to add a new node after the network is complete (even though that the current algorithm does not require it). So, we have the distance map. It is composed of a list of all minimal distances and the corresponding node pairs. And the list is, of course, ordered. Meaning that if the largest minimal distance is, say, 5, we have a list of all node pairs that are no less than 5 links apart. Same for pairs that are no less than 4 links apart and so on. The '0' distance part is the list of all nodes (each being 0 steps from itself).
* From that distance map we need to extract N nodes that are far from each other as possible. Initially I tried recursively checking if I can combine distance records, starting with the higher values, until I get an N-set of 'each-to-each' nodes. What went wrong? I hit the max iteration depth with a relatively mediocre test network. Can you improve a recursive algorithm in that regard? I don't think so, but may be there's some trick I don't know. Irrelevant - when it did not work, I was pleased, as this kind of iteration is exactly the brute force approach I would like to avoid.
* What worked (and that's one of the pieces I'm happy about) is... Well, I went a bit heuristic for a while. Imagine the network drawn on a board. If it is not too big (for a human brain, I mean) you can see the N nodes you need that are spread out as much as possible. All the rest is noise. It kind of bugged me that the object that you need (the N mini network you seek) actually exists within the big network and you only need to find a way do separate it from the rest. However you have only descriptions of the nodes and not of any collections of nodes, which mean you have perfect setup for iterating nodes, not evaluating combinations of nodes.
* So what I thought would be an ideal solution is to have the following:
  * a definition of the object that is the sub-network of nodes
  * a way to encode that definition in the nodes themselves, so that all the nodes can be sieved, based on that definition
* This did not exactly pan out. I tried several approaches. The main logic was that each node is part of many possible sub-networks, so if each of those networks is given an unique signature and all the nodes in that sub-network write the signature down... Presumably the signature of the network would be some value that will show it's fitness for the purposes of this sub-network selection.
* I had the foggy, but exciting idea to use the Fundamental Theorem of Arithmetic - the fact that each composite number can be represented by a unique product of prime numbers. So, the thinking was, if we give all the nodes special values - unique prime numbers - then the all possible combinations of nodes should result in unique composites. Then for each node you can easily find which composite it is part of. Then... No sure how to go on. I got lost there. An added difficulty is that all the prime values were unique, which means that the composited exploded in magnitude pretty quickly and each composite was therefore presented by the debugger in scientific notation, which simple meant debugging the idea was... unfeasible. You can look at the values all you want, you can not get anything useful out of them. So I had to drop that prime idea (stash it for further exploration, I mean. I still think it can be useful in another context).
* The next idea worked. I was still stuck with the idea that I have the objects that I need within the network and I just need to find them.
* I returned to the definition of the object I need:
  * There are exactly N nodes.
  * Each node is connected to each other node.
  * The smallest distance between each pair of nodes is as large as possible.
* So... here's how it is done:
  * Start with all the longest distances (a.k.a. all pairs of nodes that have the largest smallest distance between them). This list of links is the 'cut-off'.
  * From the cut-off remove all links that connect to a node with less than N links WITHIN the cut-off. Such nodes will not connect to enough number of other nodes with at least that minimal distance. The remaining nodes are 'potentials'.
  * For each of the potentials:
    * Iterate all linked nodes within the cut-off. If the linked node can be connected within the cut-ff to the other potentials, we like it. If not - drop that linked node - it will not do.
    * When the only remaining potentials are the ones that can link each to one another, count them - we need N ones. If we have more - remove the one that has a shorter average distance to the other potentials within the distribution
  * In the likely case that you can not find these N potentials with the distribution, lax the requirements one step. Create new cut-off, this time containing all distance pairs with the two longest distances. Check again within that cut-off.
  * The above explanation leaves much to be desired (will be, probably, rewritten at a later date), but the main point is that this algorithm did exactly what I wanted it to do - checked if the desired N-subnetwork existed by shaking the distance cut-off so that the unsuitable nodes fall off then checked what remained. Meaning that I managed to find a way (even if convoluted) to treat the network as information (my desired collection of nodes) and noice (all the rest). Good.
* Of course we get more than one set of anchors, so we cache them for further iteration.

**Creep**

* The creep is actually a variation on the Voronoi fill.
* All the steps of the creep and negotiation are repeated for each of the sets of anchors found previously.
* We initiate a sub-network with one starting node - each of the anchors. The sub-networks are called splits.
* Each tick each of the splits adds to itself one of the unclaimed nodes it is connected to.
* If the nodes had no value and we were looking for an equilibrium in the number of nodes, that would be it - claim until no unclaimed remain.
* However, what we care about is the total value of each split at the end. So we need to adjust the claiming process.
* We need to take into account the value of the nodes we claim.
  * Let's say we have a 1 dimensional network of nodes with values 1-3-3-1-1-1
  * We start with the two nodes at the ends as anchors. If we simply add a node a tick, we will end up with 1-3-3 and 1-1-1, which will result in total values of 7 and 3, which is far from ideal.
  * The better outcome would be 1-3 and 3-1-1-1, i.e. 4 and 6.
  * Meaning - we need to give the split on the right the change to claim the rightmost 3-node.
* So we give the splits some variable claiming power. Whenever a split encounters an unclaimed node, it starts trying to acquire it.
* It assigns to that particular node an initial claiming power of 1. It is a value to be checked against the value of the node (nodes with higher value require larger claiming power)
* If the node has a value of 1, it will be claimed in the tick it was encountered.
* If not, then more effort is needed.
* After each split has tried to claim all unclaimed nodes it is connected to, we move to a new tick.
* Two things happen:
  * For each node that is newly encountered by a split, assign a claiming power of 1
  * For each node that a split failed to claim in the previous tick, increase the claiming power of that split for that particular node by 1.
* Check if anything can be claimed.
* In short, when a split encounters a node with value 5, it will need 5 ticks to claim it.
* This means that if a split starts in a sector of the graph with heavier nodes, it will progress more slowly, whereas a split in parts of the graph with lower value nodes will burn through them faster and this will bias the acquisition towards more balanced total split values.
* When a node is claimed, all other splits that are linked to it stop trying to claim it.
* One last thing - to account for the difference of values of the starting nodes for the splits, the negative value is taken as starting claiming power for the splits. Meaning that if a split starts with a higher value, it will have to wait a bit more, before starting to try and claim other nodes.

**Negotiation**

* The negotiation ended up having less impact on the overall result than I expected. But I give that to the efficiency of the creep.

* Essentially, we iterate through the splits and check if the difference of the splits total values needs addressing (using the ideal average deviation as a guide). If the two splits are too far apart in terms of total values, we check if we can fix that by moving a node from the larger split to the smaller.

* We create a border map - a nested dictionary listing all nodes in a split that border another split.

* We call the larger split the donor and the smaller - the recipient.

* We iterate all nodes that the donor split has listed as bordering the recipient. We check if the value of that node would make a difference in the way we want.
  
  * If so, we need to make another check - will moving the node from the donor to the recipient break the donor into two or more networks. I did not foresee that initially and it tends to happen fairly regularly.
  
  * What I ended up doing was a tedious part in which you take the a copy of the split with only links within itself (a.k.a. discount all links leading to other splits), remove the node in question (producing a reduced split), then take any one of the nodes in the new split and list all nodes within the split it is connected to. If that starting node and all nodes it connects to amount to all the nodes in the reduced split, then the reduced split is not broken. So you CAN safely remove the candidate node.

* The negotiation is conducted in rounds. In each round each pair of bordering splits is checked for adjustments and if even one adjustment is made - new iteration is in order. If you run through the split pairs and you find you can not move any node, then you are done.

And that's about it!

The input ended up as good as I can think of right now - you give it a text file, in which each unit square is represented by a symbol. If you want a component rectangle to be 2 by 3, you have 6 equal symbols, arranged in a square. And the whole starting big rectangle that needs splitting is composed of such text-based smaller rectangles.

Here's an example:

eee
aab
ccb
ddb

We have:

3×1 (e)

3×1 (b)

2×1 (a)

2×1 (c)

2×1 (d)

The program can work with that, but for larger inputs you hit the limit of symbols you can use. 10 digits plus 32 letters (lowercase and uppercase) + some special symbols give you a cap about 50 and you might want to try with more than 5 starting cells.

So I modified the code to not case what symbols are used, but assign it's own signatures when reading the input. The signatures are strings, instead of characters. Essentially a base lowercase system - a through z, then aa through az, then ba onwards. This gives 676 possible starting cells which should be enough (unless it isn't).

What this gives is the option to fill in the starting cells with only 4 symbols (see Four color theorem) and not bother with the whole keyboard.

Output... less clear at the moment.

The resulting splits are provided in two ways - in the log file there is a copy of the starting text array, but all unit cells are replaced by the signature of the split they are part of.

There is also a .csv file where split signatures are replaced with digits. This was done specifically so that (if you go through the tedious step of replacing commas with tabs) you can paste it into an excel file which colors has conditional formatting for the digits between 1 and 9. Clumsy, but the result is pleasing to the eye.

**TODO**

A coloured output directly to the console would be nice, but that's not implemented yet. There are libraries for easy use of color, so it would not be hard.

