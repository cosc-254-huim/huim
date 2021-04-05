def get_item_twu_dict(db_path):
    item_twu_dict = {}
    with open(db_path) as db:
        for transac in db:
            transac_data = transac.split(":")
            items = transac_data[0].split()
            transac_util = int(transac_data[1])
            for item in items:
                item = int(item)
                if item in item_twu_dict:
                    item_twu_dict[item] += transac_util
                else:
                    item_twu_dict[item] = transac_util
    return item_twu_dict


def get_I_star(item_twu_dict, minutil):
    I_star = {}
    for item, twu in item_twu_dict.items():
        if twu >= minutil:
            I_star[(item,)] = twu
    return I_star


def get_util_lists_and_EUCS(db_path, item_twu_dict, I_star):
    util_lists = {}
    EUCS = {}
    with open(db_path) as db:
        for tid, transac in enumerate(db):
            transac_data = transac.split(":")
            items = transac_data[0].split()
            transac_util = int(transac_data[1])
            item_utils = transac_data[2].split()
            item_util_tuples = list(zip(items, item_utils))
            item_util_tuples.sort(key=lambda t: item_twu_dict[int(t[0])])
            for i, item_util_tuple in enumerate(item_util_tuples):
                item = int(item_util_tuple[0])
                itemset = (item,)
                if itemset in I_star:
                    iutil = int(item_util_tuple[1])
                    rutil = 0
                    for j in range(i + 1, len(item_util_tuples)):
                        rutil += int(item_util_tuples[j][1])
                        next_item = int(item_util_tuples[j][0])
                        add_to_EUCS(item, next_item, EUCS, transac_util)
                    util_list_tuple = (tid, iutil, rutil)
                    if itemset in util_lists:
                        util_lists[itemset].append(util_list_tuple)
                    else:
                        util_lists[itemset] = [util_list_tuple]
    return util_lists, EUCS


def add_to_EUCS(item, next_item, EUCS, transac_util):
    if item in EUCS:
        if next_item in EUCS[item]:
            EUCS[item][next_item] += transac_util
        else:
            EUCS[item][next_item] = transac_util
    else:
        EUCS[item] = {next_item: transac_util}


def get_e_in_P(P, ex, util_lists):
    for e in util_lists[P]:
        if e[0] == ex[0]:
            return e
