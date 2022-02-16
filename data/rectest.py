import copy
nodes = [2, 3, 4, 5, 6, 1, 7, 8, 9]

def getsum(target, nodes, collection, checked_states):
    '''
    # add node
        # if complete - return win
        # else:
            # if under
                # send in again
            # if over
                # pop
                # send in
    # if there are no mode nodes - return fail
    '''
    # add node - unique combination
    for node in nodes:
        if node in collection:
            continue
        state = copy.deepcopy(collection)
        state.append(node)
        if sorted(state) in checked_states:
            continue
        collection = copy.deepcopy(state)
        checked_states.append(sorted(state))

        # check for completion
        print(f'checking {collection}')
        if sum(collection) == target:
            return collection, True
        else:
            # if over:
            if sum(collection) > target:
                collection.pop()
                return getsum(target, nodes, collection, checked_states)
            # if under
            else:
                return getsum(target, nodes, collection, checked_states)
    # no more nodes
    if len(collection) > 0:
        collection.pop()
        return getsum(target, nodes, collection, checked_states)

    # nodes exhausted
    return collection, False
                


target = 23
collection = []
checked_states = []
collection, found = getsum(target, nodes, collection, checked_states)
print(f'! {found} {collection}')
