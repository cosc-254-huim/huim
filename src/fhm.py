import sys
from fhm_utils import get_item_twu_dict, get_I_star, get_util_lists_and_EUCS


def fhm(db_path, minutil):
    item_twu_dict = get_item_twu_dict(db_path)
    I_star = get_I_star(item_twu_dict, minutil)
    util_lists, EUCS = get_util_lists_and_EUCS(db_path, item_twu_dict, I_star)
    print(util_lists)
    print(EUCS)


def search(P, extens_of_P, minutil, util_lists, EUCS):
    # TODO: finish this function
    for Px in extens_of_P:
        Px_util = 0
        for Px_util_list_tuple in util_lists[Px]:
            Px_util += Px_util_list_tuple[1]
        print(Px_util)


if __name__ == "__main__":
    args = sys.argv
    fhm(db_path=args[1], minutil=int(args[2]))
