import copy


def remove_common_no_duplicate(a, b):
    a_rmd, b_rmd = list(set(a).difference(b)), list(set(b).difference(a))
    # print(a_rmd)
    # print(b_rmd)
    return a_rmd, b_rmd


def remove_common(a, b):
    a_rmd = copy.deepcopy(a)
    b_rmd = copy.deepcopy(b)
    for item_a in a:
        if item_a in b_rmd:
            b_rmd.remove(item_a)
    for item_b in b:
        if item_b in a_rmd:
            a_rmd.remove(item_b)
        # for item_b in b:
        #    if item_a == item_b:
        #        a_rmd.remove(item_a)
        #        b_rmd.remove(item_a)
    # print(a_rmd)
    # print(b_rmd)
    return a_rmd, b_rmd


def mark_cancel(list_mark_pairs):
    # Part I: Mark Cancellation
    list_mark_pairs_selected = []
    for mark_pairs in list_mark_pairs:
        if len(mark_pairs) != 2:
            print('warning: len(mark_pairs) != 2 in rcd_ranking()')
        list_loser = mark_pairs[0]
        list_winner = mark_pairs[1]
        list_loser_clear, list_winner_clear = remove_common(list_loser, list_winner)
        if len(list_winner_clear) > 0:
            list_mark_pairs_selected.append([list_loser_clear, list_winner_clear])
    return list_mark_pairs_selected


def recursive_ranking(list_constraint, list_mark_pairs_selected):
    list_highest_ranked_constraints = []
    not_ranked_constraints = list_constraint

    while len(not_ranked_constraints) > 0:
        # print(not_ranked_constraints)
        highest_ranked_constraints = copy.deepcopy(not_ranked_constraints)
        # for i in range(len(list_mark_pairs_selected)):

        for mark_pairs in list_mark_pairs_selected:
            list_winner = mark_pairs[1]
            # print(list_winner)
            # print(highest_ranked_constraints)
            # list(highest_ranked_constraints) creates a new list!!
            # otherwise, list gets updated but index does not
            for constraint in list(highest_ranked_constraints):
                if constraint in list_winner:
                    highest_ranked_constraints.remove(constraint)
                    # print('in: ' + constraint)
                # else:
                # print('notin: ' + constraint)

        for constraint in highest_ranked_constraints:
            not_ranked_constraints.remove(constraint)

        list_mark_pairs_selected_tmp = []
        for mark_pairs in list_mark_pairs_selected:
            list_loser = mark_pairs[0]
            if len(set(list_loser).intersection(highest_ranked_constraints)) == 0:
                list_mark_pairs_selected_tmp.append(mark_pairs)
        list_mark_pairs_selected = copy.deepcopy(list_mark_pairs_selected_tmp)

        list_highest_ranked_constraints.append(highest_ranked_constraints)

    return list_highest_ranked_constraints


def recursive_ranking_force_end(list_constraint, list_mark_pairs_selected):
    list_highest_ranked_constraints = []
    not_ranked_constraints = list_constraint

    prev_len_2 = len(not_ranked_constraints) + 1
    prev_len = len(not_ranked_constraints) + 1
    while len(not_ranked_constraints) > 0 and len(not_ranked_constraints) != prev_len_2:
        prev_len_2 = prev_len
        prev_len = len(not_ranked_constraints)
        #print(not_ranked_constraints)

        highest_ranked_constraints = copy.deepcopy(not_ranked_constraints)
        # for i in range(len(list_mark_pairs_selected)):

        for mark_pairs in list_mark_pairs_selected:
            list_winner = mark_pairs[1]
            # print(list_winner)
            # print(highest_ranked_constraints)
            # list(highest_ranked_constraints) creates a new list!!
            # otherwise, list gets updated but index does not
            for constraint in list(highest_ranked_constraints):
                if constraint in list_winner:
                    highest_ranked_constraints.remove(constraint)
                    # print('in: ' + constraint)
                # else:
                # print('notin: ' + constraint)

        for constraint in highest_ranked_constraints:
            not_ranked_constraints.remove(constraint)

        list_mark_pairs_selected_tmp = []
        for mark_pairs in list_mark_pairs_selected:
            list_loser = mark_pairs[0]
            if len(set(list_loser).intersection(highest_ranked_constraints)) == 0:
                list_mark_pairs_selected_tmp.append(mark_pairs)
        list_mark_pairs_selected = copy.deepcopy(list_mark_pairs_selected_tmp)

        list_highest_ranked_constraints.append(highest_ranked_constraints)

    if len(not_ranked_constraints) > 0:
        list_highest_ranked_constraints.append(not_ranked_constraints)
        print('Warning: unable to rank ' + ', '.join(not_ranked_constraints) + ', forcing them to be appended at the end')

    return list_highest_ranked_constraints


# list_constraint: list of constraints [c1, ... , cn]
# list_mark_pairs: list of marked pairs [[list_loser_marks, list_winner_marks], [list_loser_marks, list_winner_marks], ...]
# list_loser_marks: list containing constraints (can have duplicated, having in list means violation)
def rcd_ranking(list_constraint, list_mark_pairs):
    # Part I: Mark Cancellation
    list_mark_pairs_selected = mark_cancel(list_mark_pairs)
    # print(list_mark_pairs_selected)
    # Part II: Recursive Ranking
    list_ranked = recursive_ranking_force_end(list_constraint, list_mark_pairs_selected)
    return list_ranked


def flat_ranked_rcd_list(list_ranked):
    list_flat = []
    for list_sub in list_ranked:
        for item in list_sub:
            list_flat.append(item)
    return list_flat


# dict_in: {entry: number}
def dict_to_list_items(dict_in):
    list_out = []
    for k, v in dict_in.items():
        while v > 0:
            v = v - 1
            list_out.append(k)
    return list_out


# convert results of marks into input of rcd_ranking
# ur_in: a dict in the form of {constraint_1: number of violations, ..., constraint_n: number of violations}
# similarly, stuff in list_cand_in
def mark_to_rcd_input(sr_in, list_cand_in):
    list_out = []
    sr_list = dict_to_list_items(sr_in)
    for cand in list_cand_in:
        cand_list = dict_to_list_items(cand)
        list_out.append([cand_list, sr_list])
    return list_out