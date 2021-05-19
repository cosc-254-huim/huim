import os
import sys
import time
import csv
from memory_profiler import memory_usage
from typing import Union, List
from fhm_utils import UtilList, UtilListElem, ItemUtilPair


class FHM:
    """
    Class for FHM.

    Attributes:
        input_path: relative path to the data file
        output_path: relative path to the output file
        minutil: minimum utility
        output_file: output file to write high utility itemsets
        itemset_buffer_size: size for itemset buffer
        itemset_buffer: buffer for itemsets
        EUCS: Estimated Utility Co-Occurrence Structure
        mem_usage: maximum memory usage of algorithm
        hui_count: number of high utility itemsets
        candidate_count: number of candidate high utility itemsets
        prune_count: number of itemsets pruned
        runtime: total runtime of the algorithm
        total_trans_util: total transaction utility of the dataset
    """

    def __init__(self, input_path: str, output_path: str, minutil: int) -> None:
        """
        Constructor for FHM.

        Parameters:
            input_path: relative path to the data file
            output_path: relative path to the output file
            minutil: minimum utility
        """
        self.input_path = input_path
        self.output_path = output_path
        self.minutil = minutil
        self.output_file = None
        self.itemset_buffer_size = 200
        self.itemset_buffer = []
        self.EUCS = {}
        self.mem_usage = 0
        self.hui_count = 0
        self.candidate_count = 0
        self.prune_count = 0
        self.runtime = 0
        self.total_trans_util = 0

    def run(self) -> None:
        """
        Wrapper of the fhm() method that tracks memory usage.
        """
        # get max memory usage for one run of FHM
        self.mem_usage = memory_usage(self.fhm, max_usage=True, max_iterations=1)

    def fhm(self) -> None:
        """
        Run the FHM algorithm.
        """
        start_time = time.time()  # start timing algorithm

        # initialize buffer to store itemsets;
        # we can use such a buffer because FHM is a depth first search algorithm
        self.itemset_buffer = [0] * self.itemset_buffer_size

        # first DB scan to get TWU of each item
        item_TWU_dict = {}  # dictionary of items and their TWU
        with open(self.input_path) as db:
            for transac in db:
                transac_data = transac.split(":")
                items = transac_data[0].split()
                transac_util = int(transac_data[1])
                for item in items:
                    item = int(item)
                    if item in item_TWU_dict:
                        item_TWU_dict[item] += transac_util
                    else:
                        item_TWU_dict[item] = transac_util

        # initialize list of utility lists and dictionary of itemsets and their utility lists
        # that only contain items with TWU >= minutil
        util_lists = []
        item_util_list_dict = {}
        for item, TWU in item_TWU_dict.items():
            if TWU >= self.minutil:
                util_list = UtilList(item)
                util_lists.append(util_list)
                item_util_list_dict[item] = util_list
            else:
                self.prune_count += 1

        # sort util_lists in order of ascending TWU
        util_lists.sort(key=lambda ul: item_TWU_dict[ul.item])

        # second DB scan to populate utility lists and EUCS
        with open(self.input_path) as db:
            for tid, transac in enumerate(db):
                transac_data = transac.split(":")
                items = transac_data[0].split()
                transac_util = int(transac_data[1])
                self.total_trans_util += transac_util
                item_utils = transac_data[2].split()

                # get items that have TWU >= minutil
                item_pairs = []
                rutil = 0
                for i in range(len(items)):
                    item_util_pair = ItemUtilPair(int(items[i]), int(item_utils[i]))
                    if item_TWU_dict[item_util_pair.item] >= self.minutil:
                        item_pairs.append(item_util_pair)
                        rutil += item_util_pair.util

                # sort item_pairs in order of ascending TWU
                item_pairs.sort(key=lambda p: item_TWU_dict[p.item])

                # populate the utility lists in item_util_list_dict with elements
                for i in range(len(item_pairs)):
                    rutil -= item_pairs[i].util
                    util_list_elem = UtilListElem(tid, item_pairs[i].util, rutil)
                    item_util_list_dict[item_pairs[i].item].add_elem(util_list_elem)

                    # populate EUCS
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

        # recursively search for itemsets
        with open(self.output_path, "w") as out:
            self.output_file = out
            self.search(0, None, util_lists)

        self.runtime = (time.time() - start_time) * 1_000  # stop timing algorithm

    def search(
        self,
        prefix_len: int,
        prefix_UL: Union[UtilList, None],
        prefix_ext_ULs: List[UtilList],
    ) -> None:
        """
        Recursive method to search all high utility itemsets and output them into a file.

        Parameters:
            prefix_len: length of the prefix itemset
            prefix_UL: utility list of the prefix itemset
            prefix_ext_ULs: list of utility lists for each extension of the prefix itemset
        """
        # for each extension x of the prefix
        for i in range(len(prefix_ext_ULs)):
            prefix_x_UL = prefix_ext_ULs[i]  # utility list for the itemset prefix U {x}

            # output itemset if it has high utility
            if prefix_x_UL.sum_iutils >= self.minutil:
                self.output(prefix_len, prefix_x_UL.item, prefix_x_UL.sum_iutils)

            # condition to explore extensions of prefix U {x}
            if prefix_x_UL.sum_iutils + prefix_x_UL.sum_rutils >= self.minutil:
                prefix_x_ext_ULs = []  # utility lists for the extensions of prefix U {x}

                # for each extension y of the prefix such that y > x
                for j in range(i + 1, len(prefix_ext_ULs)):
                    prefix_y_UL = prefix_ext_ULs[j]  # utility list for the itemset prefix U {y}
                    if (
                        prefix_x_UL.item in self.EUCS
                        and prefix_y_UL.item in self.EUCS[prefix_x_UL.item]
                    ):
                        # condition to explore extensions of prefix U {x, y}
                        if self.EUCS[prefix_x_UL.item][prefix_y_UL.item] >= self.minutil:
                            self.candidate_count += 1

                            # construct utility list for the itemset prefix U {x, y}
                            # and append it to the utility lists for the extensions of prefix U {x}
                            prefix_x_y_UL = self.construct(prefix_UL, prefix_x_UL, prefix_y_UL)
                            prefix_x_ext_ULs.append(prefix_x_y_UL)
                        else:
                            self.prune_count += 1

                # add item x to prefix in order to create new prefix
                try:
                    self.itemset_buffer[prefix_len] = prefix_x_UL.item
                except IndexError:
                    sys.exit(
                        f"Error: itemset_buffer_size ({self.itemset_buffer_size}) is too small"
                    )

                # recursive search to find all itemsets with the prefix: prefix U {x, y}
                self.search(prefix_len + 1, prefix_x_UL, prefix_x_ext_ULs)

            else:
                self.prune_count += 1

    def output(self, prefix_len: int, item: int, util: int) -> None:
        """
        Write the given high utility itemset and it's utility to self.output_file.

        Parameters:
            prefix_len: length of the prefix itemset
            item: item extension of the prefix itemset
            util: utility of the itemset
        """
        self.hui_count += 1
        line = []
        for i in range(prefix_len):
            line.append(str(self.itemset_buffer[i]))
        line.append(str(item))
        line.append("#UTIL:")
        line.append(str(util))
        self.output_file.write(" ".join(line) + "\n")

    def construct(
        self, prefix_UL: Union[UtilList, None], prefix_x_UL: UtilList, prefix_y_UL: UtilList
    ) -> UtilList:
        """
        Construct the utility list for the itemset prefix U {x, y},
        where x and y are item extension of prefix.

        Parameters:
            prefix_UL: utility list of the prefix itemset
            prefix_x_UL: utility list of the itemset prefix U {x}
            prefix_y_UL: utility list of the itemset prefix U {y}

        Returns:
            utility list of the itemset prefix U {x, y}
        """
        # initialize utility list for the itemset prefix U {x, y}
        prefix_x_y_UL = UtilList(prefix_y_UL.item)

        # for each element ex in the utility list of prefix U {x}
        for ex in prefix_x_UL.elems:
            # get element ey in the utility list of prefix U {y} with the same tid
            ey = self.get_elem_with_tid(prefix_y_UL, ex.tid)
            if ey is None:
                continue

            # case when prefix is the empty set and x and y are 1-itemsets
            if prefix_UL is None:
                # create utility list element for prefix U {x, y}
                # and add it to the utility list of prefix U {x, y}
                exy = UtilListElem(ex.tid, ex.iutil + ey.iutil, ey.rutil)
                prefix_x_y_UL.add_elem(exy)

            # case when prefix is non-empty
            else:
                # get element e in the utility list of prefix with the same tid
                e = self.get_elem_with_tid(prefix_UL, ex.tid)
                if e is not None:
                    # create utility list element for prefix U {x, y}
                    # and add it to the utility list of prefix U {x, y}
                    exy = UtilListElem(ex.tid, ex.iutil + ey.iutil - e.iutil, ey.rutil)
                    prefix_x_y_UL.add_elem(exy)

        return prefix_x_y_UL

    @staticmethod
    def get_elem_with_tid(util_list: UtilList, tid: int) -> Union[UtilListElem, None]:
        """
        Get the element in util_list that has tid as its transaction ID via binary search.

        Parameters:
            util_list: utility list to find element with tid
            tid: transaction ID to find

        Returns:
            the element in the utility list with the given tid or None if no such element is found
        """
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

    def print_stats(self) -> None:
        """
        Print statistics for the FHM algorithm.
        """
        print("===============FHM ALGORITHM STATS===============")
        print(f"total runtime (ms): {self.runtime}")
        print(f"high utility itemset count: {self.hui_count}")
        print(f"candidate itemset count: {self.candidate_count}")
        print(f"pruned itemset count: {self.prune_count}")
        print(f"maximum memory used (MB): {self.mem_usage}")
        print(f"total transaction utility: {self.total_trans_util}")

    # initializes csv file by adding column names if csv file does not exist
    def initialize_csv(self, filename) -> None:
        fields = [
            "minimum utility",
            "total runtime (ms)",
            "high utility itemSet count",
            "candidate itemSet count",
            "pruned itemSet count",
            "maximum memory used (MB)",
        ]

        with open(filename, "w+") as csvfile:
            # creating a csv writer object
            _writer = csv.writer(csvfile)

            # writing the fields
            _writer.writerow(fields)

    # adds rows to the csv file
    def experiment(self, filename) -> None:
        # data rows of csv file
        rows = [
            [
                self.minutil,
                self.runtime,
                self.hui_count,
                self.candidate_count,
                self.prune_count,
                self.mem_usage,
            ]
        ]
        with open(filename, "a+", newline="") as csvfile:
            # creating a csv writer object
            _writer = csv.writer(csvfile)

            # writing the data rows
            _writer.writerows(rows)


if __name__ == "__main__":
    args = sys.argv
    input_path = args[1]
    output_path = args[2]
    minutil = int(args[3])
    fhm = FHM(input_path, output_path, minutil)
    fhm.run()
    fhm.print_stats()

    # initializes csv file by adding column names if csv file does not exist
    # adds rows to the csv file
    # names the csv file after the name of the input file
    # fetch the current directory
    cur_path = os.getcwd()
    cur_path1 = cur_path.split("/")[:-1]  # ensures that we are no longer in src and are instead in

    if not os.path.isdir("/".join(cur_path1) + "/experiments"):
        os.mkdir("/".join(cur_path1) + "/experiments")
    os.chdir("/".join(cur_path1) + "/experiments")

    if "DB_Utility.txt" in input_path:
        if not os.path.exists("experiment_DB_Utility.csv"):
            fhm.initialize_csv("experiment_DB_Utility.csv")
        fhm.experiment("experiment_DB_Utility.csv")

    if "chess.txt" in input_path:
        if not os.path.exists("experiment_chess.csv"):
            fhm.initialize_csv("experiment_chess.csv")
        fhm.experiment("experiment_chess.csv")

    if "foodmart.txt" in input_path:
        if not os.path.exists("experiment_food_mart.csv"):
            fhm.initialize_csv("experiment_food_mart.csv")
        fhm.experiment("experiment_food_mart.csv")

    if "BMS.txt" in input_path:
        if not os.path.exists("experiment_BMS.csv"):
            fhm.initialize_csv("experiment_BMS.csv")
        fhm.experiment("experiment_BMS.csv")

    # return to the original directory so the shell script can correctly find the path
    cur_path = os.getcwd().split("/")[:-1]
    os.chdir("/".join(cur_path))
