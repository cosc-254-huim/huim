import sys
from fhm_utils import get_item_twu_dict, get_I_star, get_util_lists_and_EUCS


def fhm(db_path, minutil):
    item_twu_dict = get_item_twu_dict(db_path)
    I_star = get_I_star(item_twu_dict, minutil)
    util_lists, EUCS = get_util_lists_and_EUCS(db_path, item_twu_dict, I_star)


if __name__ == "__main__":
    args = sys.argv
    fhm(db_path=args[1], minutil=int(args[2]))
