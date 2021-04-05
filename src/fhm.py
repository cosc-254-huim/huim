import sys
from fhm_utils import get_item_twu_dict, get_I_star, get_util_lists_and_EUCS, get_e_in_P


def fhm(db_path, minutil):
    item_twu_dict = get_item_twu_dict(db_path)
    I_star = get_I_star(item_twu_dict, minutil)
    util_lists, EUCS = get_util_lists_and_EUCS(db_path, item_twu_dict, I_star)
    hu_itemsets = []
    search((), I_star.keys(), minutil, I_star, util_lists, EUCS, hu_itemsets)
    hu_itemsets.sort(key=lambda t: t[0][0], reverse=True)
    print(f"hu_itemsets: {hu_itemsets}")
    print(f"count: {len(hu_itemsets)}")


def search(P, extens_of_P, minutil, I_star, util_lists, EUCS, hu_itemsets):
    for Px in extens_of_P:
        Px_iutil_sum = sum([ex[1] for ex in util_lists[Px]])
        if Px_iutil_sum >= minutil:
            hu_itemsets.append((Px, Px_iutil_sum))
        Px_rutil_sum = sum([ex[2] for ex in util_lists[Px]])
        if Px_iutil_sum + Px_rutil_sum >= minutil:
            extens_of_Px = list()
            for Py in extens_of_P:
                x = Px[-1]
                y = Py[-1]
                if I_star[(y,)] > I_star[(x,)]:
                    try:
                        if EUCS[x][y] >= minutil:
                            Pxy = tuple(list(P) + [x, y])
                            util_lists[Pxy] = construct(P, Px, Py, util_lists)
                            extens_of_Px.append(Pxy)
                    except KeyError:
                        continue
            search(Px, extens_of_Px, minutil, I_star, util_lists, EUCS, hu_itemsets)


def construct(P, Px, Py, util_lists):
    util_list_of_Pxy = []
    for ex in util_lists[Px]:
        for ey in util_lists[Py]:
            if ex[0] == ey[0]:
                if P in util_lists:
                    e = get_e_in_P(P, ex, util_lists)
                    exy = (ex[0], ex[1] + ey[1] - e[1], ey[2])
                else:
                    exy = (ex[0], ex[1] + ey[1], ey[2])
                util_list_of_Pxy.append(exy)
    return util_list_of_Pxy


if __name__ == "__main__":
    args = sys.argv
    fhm(db_path=args[1], minutil=int(args[2]))
