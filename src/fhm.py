import sys
import time
from typing import Union, List
from fhm_utils import UtilList, UtilListElem, ItemUtilPair


class FHM:
    def __init__(self, db_path: str, minutil: int) -> None:
        self.db_path = db_path
        self.minutil = minutil
        self.EUCS = {}
        self.itemset_buffer = [0] * 200
        self.hui_count = 0
        self.runtime = 0

    def run(self) -> None:
        time_start = time.time()
        # first DB scan to get TWU of each item
        item_twu_dict = {}
        with open(self.db_path) as db:
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

        # create list of utility lists and
        # map of itemsets to utility lists
        util_lists = []
        itemset_util_list_dict = {}
        for item, twu in item_twu_dict.items():
            if twu >= self.minutil:
                util_list = UtilList(item)
                itemset_util_list_dict[item] = util_list
                util_lists.append(util_list)

        # sort util_lists in order of ascending TWU
        util_lists.sort(key=lambda ul: item_twu_dict[ul.item])

        # second DB scan to populate utility lists and EUCS
        with open(self.db_path) as db:
            for tid, transac in enumerate(db):
                transac_data = transac.split(":")
                items = transac_data[0].split()
                transac_util = int(transac_data[1])
                item_utils = transac_data[2].split()

                # get items that have TWU >= minutil
                item_pairs = []
                rutil = 0
                for i in range(len(items)):
                    item_util_pair = ItemUtilPair(int(items[i]), int(item_utils[i]))
                    if item_twu_dict[item_util_pair.item] >= self.minutil:
                        item_pairs.append(item_util_pair)
                        rutil += item_util_pair.util
                item_pairs.sort(key=lambda p: item_twu_dict[p.item])

                # add items to utility lists
                for i in range(len(item_pairs)):
                    rutil -= item_pairs[i].util
                    util_list_elem = UtilListElem(tid, item_pairs[i].util, rutil)
                    itemset_util_list_dict[item_pairs[i].item].add_elem(util_list_elem)

                    # create EUCS
                    for j in range(i + 1, len(item_pairs)):
                        item = item_pairs[i].item
                        next_item = item_pairs[j].item
                        if item in self.EUCS:
                            if next_item in self.EUCS[item]:
                                self.EUCS[item][next_item] += transac_util
                            else:
                                self.EUCS[item][next_item] = transac_util
                        else:
                            self.EUCS[item] = {next_item: transac_util}
        self.search(self.itemset_buffer, 0, None, util_lists)
        self.runtime = (time.time() - time_start) * 1000

    def search(
        self,
        prefix: List[int],
        prefix_len: int,
        prefix_util_list: Union[UtilList, None],
        util_lists: List[UtilList],
    ) -> None:
        for i in range(len(util_lists)):
            X = util_lists[i]
            if X.sum_iutils >= self.minutil:
                self.output(prefix, prefix_len, X.item, X.sum_iutils)
            if X.sum_iutils + X.sum_rutils >= self.minutil:
                ex_util_lists = []
                for j in range(len(util_lists)):
                    Y = util_lists[j]
                    try:
                        if self.EUCS[X.item][Y.item] >= self.minutil:
                            Pxy_util_list = self.construct(prefix_util_list, X, Y)
                            ex_util_lists.append(Pxy_util_list)
                    except KeyError:
                        continue
                try:
                    self.itemset_buffer[prefix_len] = X.item
                except IndexError:
                    sys.exit("Error: length itemset_buffer is too small")
                self.search(self.itemset_buffer, prefix_len + 1, X, ex_util_lists)

    def output(self, prefix: List[int], prefix_len: int, item: int, util: int) -> None:
        self.hui_count += 1
        out = []
        for i in range(prefix_len):
            out.append(str(prefix[i]))
        out.append(str(item))
        out.append("#UTIL:")
        out.append(str(util))
        print(" ".join(out))

    def construct(self, P: Union[UtilList, None], Px: UtilList, Py: UtilList) -> UtilList:
        Pxy_util_list = UtilList(Py.item)
        for ex in Px.elems:
            ey = self.get_elem_with_tid(Py, ex.tid)
            if ey is None:
                continue
            if P is None:
                exy = UtilListElem(ex.tid, ex.iutil + ey.iutil, ey.rutil)
                Pxy_util_list.add_elem(exy)
            else:
                e = self.get_elem_with_tid(P, ex.tid)
                if e is not None:
                    exy = UtilListElem(ex.tid, ex.iutil + ey.iutil - e.iutil, ey.rutil)
                    Pxy_util_list.add_elem(exy)
        return Pxy_util_list

    def get_elem_with_tid(self, util_list: UtilList, tid: int) -> Union[UtilListElem, None]:
        elems = util_list.elems
        first = 0
        last = len(elems) - 1
        while first <= last:
            mid = (first + last) // 2
            if elems[mid].tid < tid:
                first = mid + 1
            elif elems[mid].tid > tid:
                last = mid - 1
            else:
                return elems[mid]

    def get_stats(self) -> None:
        print(f"hui_count: {self.hui_count}")
        print(f"runtime (ms): {self.runtime}")


if __name__ == "__main__":
    args = sys.argv
    fhm = FHM(db_path=args[1], minutil=int(args[2]))
    fhm.run()
    fhm.get_stats()
