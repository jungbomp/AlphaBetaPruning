import sys
import re
import copy


MAX_NUM = 2147483647
MIN_NUM = -2147483648


with open(sys.argv[2], "rt") as fi:
    inputList = [line.rstrip() for line in fi]

# get the day (Contains "today" or Yesterday" indicating which day the RPL was posted)
day = inputList[0].upper()

# get the player (Contains either "R1" or "R2" indicating which roommate has next turn)
player = (1 if 'R2' == inputList[1].upper() else 0)

# get the region profitability list (Ordered list of tuples (Region_Identifier, Profit_Number)
temp = re.findall('([a-zA-Z]+\s*[,]\s*[0-9]+)', inputList[2].upper())
RPL_index = {}
RPL = []
for i in range(len(temp)):
    tempItem = temp[i].split(',')
    RPL_index[tempItem[0].strip()] = i
    RPL.insert(i, [tempItem[0].strip(), float(tempItem[1].strip())])

sorted_RPL_index = RPL_index.keys()
sorted_RPL_index.sort(lambda lhs, rhs: cmp(lhs, rhs) if len(lhs) == len(rhs) else cmp(len(lhs), len(rhs)))

# get the adjacency matrix rows (The rows of the adjacency matrix representing the map)
matrix = []
for i in range(len(RPL)):
    matrix.insert(i, re.findall('([0-9]+)', inputList[i + 3]))

# get the picked regions (Comma separated list of regions picked so far. Will contain "*" if no activity yet)
picked_list = re.findall('([A-Z*]+)', inputList[len(RPL) + 3].upper())
pickedRegions = []
for i in range(len(picked_list)):
    if picked_list[i] != "PASS" and picked_list[i] in pickedRegions:
        continue
    pickedRegions.append(picked_list[i])

# get max depth (a number that determines the maximum depth of your search tree)
maxDepth = int(inputList[len(RPL) + 4].strip())
pickedLen = 0
for i in range(len(pickedRegions)):
    if "*" != pickedRegions[i]:
        pickedLen = pickedLen + 1

maxDepth = maxDepth - pickedLen
diff = len(RPL_index) - pickedLen
if diff <= maxDepth:
    maxDepth = diff
if 0 < (maxDepth % 2):
    maxDepth = maxDepth - 1

# sum ((1 / (# of regions)) * (region profitability # from yesterday))
yesterdaySum = 0.0

# list for leaf nodes
leaves = []

# index of leaf node of maximum score
maxIndex = -1

# list containing picked nodes
expanded = []

# accumulated score for each node
scores = [0, 0]

# Evaluation function for the region
eval_func = None


def non_heuristic(ele):
    if "PASS" == ele:
        return 0

    return RPL[RPL_index[ele]][1]


def heuristic(ele):
    if "PASS" == ele:
        return 0.0

    return (yesterdaySum + RPL[RPL_index[ele]][1]) / 2.0


def modified_cmp(lhs, rhs):
    if len(lhs) == len(rhs):
        return cmp(lhs, rhs)

    return cmp(len(lhs), len(rhs))


def insert_region(candidates, region):
    # Insert a candidate into a candidate list
    insert_index = 0
    length = len(candidates)
    if 1 < length:
        left = 0
        right = length - 1
        if modified_cmp(candidates[right], region) < 0:
            insert_index = right + 1
        elif modified_cmp(candidates[left], region) < 0:
            while left <= right:
                insert_index = (left + right) / 2
                if modified_cmp(candidates[insert_index], region) < 0:
                    left = insert_index + 1
                else:
                    right = insert_index - 1
            if modified_cmp(candidates[insert_index], region) < 0:
                insert_index = insert_index + 1
    elif 0 < length:
        if modified_cmp(candidates[insert_index], region) < 0:
            insert_index = insert_index + 1

    candidates.insert(insert_index, region)


def update_candidate(candidates, region):
    """
        Add available candidates into candidates list

        :param candidates: The destination list to update candidates
        :param region: A region to check adjacency with other region
    """

    global expanded  # A dictionary which is supposed to contain picked regions

    if "PASS" != region:
        for candi in sorted_RPL_index:
            if candi not in expanded and candi not in candidates and ('*' == region or '1' == matrix[RPL_index[region]][RPL_index[candi]]):
                # Insert a candidate into a candidate list
                insert_region(candidates, candi)

        if len(candidates) < 1:
            candidates.append("PASS")
    elif "PASS" not in candidates:
        candidates.append("PASS")

    return candidates


def gen_picked_tree(picked_regions, cur_index, candidates):
    """
        :param picked_regions: The list of picked regions
        :param cur_index: An index for the picked_regions list
        :param candidates: A list for the candidate regions
        :return: The leaf node of the tree
    """

    global eval_func  # A function for evaluation
    global expanded  # A dictionary which is supposed to contain picked regions
    global scores  # Accumulated score for each node

    scores = [0, 0]
    cur_player = (cur_index + len(picked_regions)) % 2
    for region in picked_regions:
        expanded.append(region)

    for region in picked_regions:
        score = scores[cur_player] + eval_func(region)
        scores[cur_player] = score

        # Add available candidates into candidates list
        update_candidate(candidates[cur_player], region)

        # opponent index for next turn
        cur_player = (cur_player + 1) % 2

    return {"scores": scores, "candidates": candidates}


def alpha_beta_search(parent, depth, cur_player, candidates, is_max, alpha, beta):
    """
        :param parent: parent node for sub tree
        :param depth: depth for sub tree
        :param cur_player: An index for current player
        :param candidates: An list containing available regions for current player
        :param is_max: Current node type (true: max_node, otherwise: min_node)
        :param alpha: Alpha value
        :param beta: Beta value
        :return: list containing child score, node's score and region's name
    """
    global leaves
    global expanded  # A dictionary of expended node
    global scores  # A list containing accumulated scores by each player
    global eval_func  # A function for evaluation

    opponent = (cur_player + 1) % 2

    if maxDepth < depth:
        leaves.append(int(round(scores[opponent])))
        # if cur_player != player:
        return [scores[opponent], parent]
        # else:
        #     return [scores[opponent], parent]

    if (len(candidates[cur_player]) < 1 or "PASS" == candidates[cur_player][0]) and (len(candidates[opponent]) < 1 or "PASS" == candidates[opponent][0]):
        leaves.append(int(round(scores[cur_player])))
        # if cur_player != player:
        return [scores[cur_player], parent]

    # Initialize value
    value = (MIN_NUM if is_max else MAX_NUM)
    max_region = ""
    opp_index = -1

    cur_candidates = copy.copy(candidates[cur_player])
    for idx in range(len(candidates[cur_player])):
        region = candidates[cur_player].pop(idx)

        expanded.append(region)
        score = eval_func(region)
        scores[cur_player] = scores[cur_player] + score

        # Remove a candidate from opponent's list if one exists
        if "PASS" != region and region in candidates[opponent]:
            opp_index = candidates[opponent].index(region)
            candidates[opponent].remove(region)

        update_candidate(candidates[cur_player], region)

        if is_max:
            child = alpha_beta_search(region, depth + 1, opponent, candidates, False, alpha, beta)
            if value < child[0]:
                value = child[0]
                max_region = region

            if beta <= value:
                scores[cur_player] = scores[cur_player] - score
                expanded.pop(len(expanded) - 1)
                if -1 < opp_index:
                    candidates[opponent].insert(opp_index, region)
                candidates[cur_player] = copy.copy(cur_candidates)
                return [value, region]

            if alpha < value:
                alpha = value
        else:
            child = alpha_beta_search(region, depth + 1, opponent, candidates, True, alpha, beta)
            if child[0] < value:
                value = child[0]
                max_region = region

            if value <= alpha:
                scores[cur_player] = scores[cur_player] - score
                expanded.pop(len(expanded) - 1)
                if -1 < opp_index:
                    candidates[opponent].insert(opp_index, region)
                candidates[cur_player] = copy.copy(cur_candidates)
                return [value, region]

            if value < beta:
                beta = value

        scores[cur_player] = scores[cur_player] - score
        expanded.pop(len(expanded) - 1)
        if -1 < opp_index:
            candidates[opponent].insert(opp_index, region)
        candidates[cur_player] = copy.copy(cur_candidates)

    return [value, max_region]


def main():
    global eval_func
    global leaves

    eval_func = non_heuristic
    if "YESTERDAY" == day:
        eval_func = heuristic
        global yesterdaySum
        for i in range(len(RPL)):
            yesterdaySum = yesterdaySum + (RPL[i][1] / float(len(RPL)))

    # index for a current player
    cur_player = player

    candidates = [[], []]

    parent = (pickedRegions[len(pickedRegions) - 1] if '*' != pickedRegions[0] else '*')
    grand_parent = ('*' if len(pickedRegions) < 2 else pickedRegions[len(pickedRegions) - 2])

    if '*' != parent:
        gen_picked_tree(pickedRegions, cur_player, candidates)

    update_candidate(candidates[(cur_player + 1) % 2], parent)
    update_candidate(candidates[cur_player], grand_parent)
    max_child = alpha_beta_search(parent, 0, cur_player, candidates, True, MIN_NUM, MAX_NUM)

    fo = open("output.txt", "wt")

    sys.stdout.write("{0}, {1}\n".format(max_child[1], len(leaves)))
    for ele in leaves:
        sys.stdout.write("{},".format(ele))

    fo.write("{}\n".format(max_child[1]))
    fo.write("{}".format(leaves.pop(0)))
    for ele in leaves:
        fo.write(",{}".format(ele))

    fo.close()


if __name__ == "__main__":
    main()
