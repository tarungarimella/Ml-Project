import json
from FOON_class import Object
from search import check_if_exist_in_kitchen, read_universal_foon, save_paths_to_file


with open('motion.txt', 'r') as file:
    lines = file.readlines()
    
def DLS(src,target,maxDepth):     
        if src == target : return True

        # If reached the maximum depth, stop recursing.
        if maxDepth <= 0 : return False

        # Recur for all the vertices adjacent to this vertex
        for i in len(src):
                if(DLS(src[i],target,maxDepth-1)):
                    return True
        return False
        
# IDDFS to search if target is reachable.
# It uses recursive DLS()
def IDDFS(src, target, maxDepth):
    # Repeatedly depth-limit search till the
    # maximum depth
    for i in range(maxDepth):
        if (DLS(src, target, i)):
            candidate = foon_object_to_FU_map[target][0] #Choose the first path
            return candidate
    return False


def h1_GreedySearch(candidate_units):
    rate = 0
    motions = []
    # print(candidate_units)
    # Iterating through the paths to find one with the highest success rate
    for unit in candidate_units:                    
        motion = foon_functional_units[unit].motion_node 
        motions.append(motion)    

        ##Finding the motion in each node and finding its success rate from motion.txt
        for line in lines:
            if line.split('\t')[0] == str(motion):
                success_rate = line.split('\t')[1].replace("\n", "")
                
        if float(success_rate) > rate:
            rate = float(success_rate)
            m = motion
            candidate = unit # Path with the highest success rate
    # print(motions)
    # print(m," = ",rate, "Unit: ", candidate)
    
    return candidate

# Heuristic function based on the number of inputs in the functional unit
def h2_GreedySearch(candidate_units):
    no_of_obj = 0
    
    #Find the path that requires less number of input nodes
    for unit in candidate_units:            
        inputs = foon_functional_units[unit].input_nodes     
        
        if no_of_obj  < len(inputs):
            no_of_obj = len(inputs) ##The least number of objects
         
    # Finding the path with the least number of objects        
    for unit_node in candidate_units:
        input_nodes = foon_functional_units[unit_node].input_nodes
        if len(input_nodes) == no_of_obj:
            candidate = unit_node
            
    return candidate


def search_Main(kitchen_items=[], goal_node=None, search=None):
    # list of indices of functional units
    reference_task_tree = []

    # list of object indices that need to be searched
    items_to_search = []

    # find the index of the goal node in object node list
    items_to_search.append(goal_node.id)

    # list of item already explored
    items_already_searched = []

    while len(items_to_search) > 0:
        current_item_index = items_to_search.pop(0)  # pop the first element
        if current_item_index in items_already_searched:
            continue

        else:
            items_already_searched.append(current_item_index)

        current_item = foon_object_nodes[current_item_index]

         

        if not check_if_exist_in_kitchen(kitchen_items, current_item):

            candidate_units = foon_object_to_FU_map[current_item_index]
            depth = 1
            
            # selecting the first path
            # this is the part where you should use heuristic for Greedy Best-First search             
        
            if  search == "h1_greedy":
                selected_candidate_idx = h1_GreedySearch(candidate_units)    
            elif search == "h2_greedy":     
                selected_candidate_idx = h2_GreedySearch(candidate_units)
            elif search == "IDDFS":
                selected_candidate_idx = IDDFS(current_item.id, current_item_index,depth)               
            
            
            if selected_candidate_idx in reference_task_tree:
                continue

            reference_task_tree.append(selected_candidate_idx)

            # all input of the selected FU need to be explored
            for node in foon_functional_units[
                    selected_candidate_idx].input_nodes:
                node_idx = node.id
                if node_idx not in items_to_search:

                    # if in the input nodes, we have bowl contains {onion} and onion, chopped, in [bowl]
                    # explore only onion, chopped, in bowl
                    flag = True
                    if node.label in utensils and len(node.ingredients) == 1:
                        for node2 in foon_functional_units[
                                selected_candidate_idx].input_nodes:
                            if node2.label == node.ingredients[
                                    0] and node2.container == node.label:

                                flag = False
                                break
                    if flag:
                        items_to_search.append(node_idx)

    # reverse the task tree
    reference_task_tree.reverse()

    # create a list of functional unit from the indices of reference_task_tree
    task_tree_units = []
    for i in reference_task_tree:
        task_tree_units.append(foon_functional_units[i])

    return task_tree_units


if __name__ == '__main__':
    foon_functional_units, foon_object_nodes, foon_object_to_FU_map = read_universal_foon(
    )

    utensils = []
    with open('utensils.txt', 'r') as f:
        for line in f:
            utensils.append(line.rstrip())

    kitchen_items = json.load(open('kitchen.json'))

    goal_nodes = json.load(open("goal_nodes.json"))

    for node in goal_nodes:
        node_object = Object(node["label"])
        node_object.states = node["states"]
        node_object.ingredients = node["ingredients"]
        node_object.container = node["container"]

        for object in foon_object_nodes:
            if object.check_object_equal(node_object):
                h1_task_tree = search_Main(kitchen_items, object, "h1_greedy")
                save_paths_to_file(h1_task_tree,
                                   'h1_greedy_{}.txt'.format(node["label"]))

                h2_task_tree = search_Main(kitchen_items, object, "h2_greedy")
                save_paths_to_file(h2_task_tree,
                                   'h2_greedy_{}.txt'.format(node["label"]))
                h3_task_tree = search_Main(kitchen_items, object, "IDDFS")
                save_paths_to_file(h3_task_tree,
                                   'IDDFS_{}.txt'.format(node["label"]))
                break
        else:
                print("The goal node does not exist")
