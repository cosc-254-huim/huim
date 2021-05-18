import sys
import time
from memory_profiler import memory_usage


class TwoPhase:
    """
    Class for TwoPhase.

    Attributes:
        input_path: relative path to the data file
        output_path: relative path to the output file
        minutil: minimum utility
        output_file: output file to write high utility itemsets
        mem_usage: maximum memory usage of algorithm
        itemset_count: total number of itemsets
        hui_count: number of high utility itemsets
        candidate_count: number of candidate high utility itemsets
        prune_count: number of itemsets pruned
        runtime: total runtime of the algorithm
        total_trans_util: total transaction utility of the dataset
    """

    def __init__(self, input_path: str, output_path: str, minutil: int) -> None:
        """
        Constructor for TwoPhase.

        Parameters:
            input_path: relative path to the data file
            output_path: relative path to the output file
            minutil: minimum utility
        """
        self.input_path = input_path
        self.output_path = output_path
        self.minutil = minutil
        self.output_file = None
        self.mem_usage = 0
        self.itemset_count = 0
        self.hui_count = 0
        self.candidates = []
        self.candidate_count = 0
        self.prune_count = 0
        self.runtime = 0
        self.total_trans_util = 0

    def run(self) -> None:
        """
        Wrapper of the two_phase() method that tracks memory usage.
        """
        # get max memory usage for one run of Two Phase
        self.mem_usage = memory_usage(self.two_phase, max_usage=True, max_iterations=1)

    def two_phase(self) -> None:
        """
        Run the FHM algorithm.
        """
        start_time = time.time()

        # Phase 1
        # scan DB to calculate TWU of each item
        item_TWU_dict = {}
        with open(self.input_path) as db:
            for transac in db:
                transac_data = transac.split(":")
                items = transac_data[0].split()
                transac_util = int(transac_data[1])
                self.total_trans_util += transac_util
                for item in items:
                    item = int(item)
                    if item in item_TWU_dict:
                        item_TWU_dict[item] += transac_util
                    else:
                        item_TWU_dict[item] = transac_util

        self.itemset_count = (2 ** len(item_TWU_dict)) - 1

        # get candidate high utility 1-itemsets with TWU >= minutil
        one_itemsets = []
        for item, TWU in item_TWU_dict.items():
            if TWU >= self.minutil:
                one_itemsets.append([item])
            else:
                self.prune_count += 1

        self.candidates += one_itemsets

        k_min_one_itemsets = one_itemsets
        while True:
            # generate candidate high utility k-itemsets
            k_itemsets = self.itemset_generation(k_min_one_itemsets)

            # scan DB to calculate TWU of each candidate high utility k-itemset
            k_itemset_TWU_dict = {}
            with open(self.input_path) as db:
                for transac in db:
                    transac_data = transac.split(":")
                    items = {int(item) for item in transac_data[0].split()}
                    transac_util = int(transac_data[1])
                    for k_itemset in k_itemsets:
                        if set(k_itemset).issubset(items):
                            k_itemset_tuple = tuple(k_itemset)
                            if k_itemset_tuple in k_itemset_TWU_dict:
                                k_itemset_TWU_dict[k_itemset_tuple] += transac_util
                            else:
                                k_itemset_TWU_dict[k_itemset_tuple] = transac_util

            # get candidate high utility k-itemsets with TWU >= minutil
            k_itemsets = []
            for k_itemset, TWU in k_itemset_TWU_dict.items():
                if TWU >= self.minutil:
                    k_itemsets.append(list(k_itemset))
                else:
                    self.prune_count += 1

            self.candidates += k_itemsets

            # break if there are no more candidate high utility k-itemsets
            if len(k_itemsets) == 0:
                break
            # otherwise, proceed to next k level
            k_min_one_itemsets = k_itemsets

        self.candidate_count = len(self.candidates)

        # Phase 2
        # scan DB to calculate the utility of each candidate itemset
        itemset_util_dict = {}
        with open(self.input_path) as db:
            for transac in db:
                transac_data = transac.split(":")
                items = [int(item) for item in transac_data[0].split()]
                utils = [int(util) for util in transac_data[2].split()]
                item_util_dict = dict(zip(items, utils))
                items = set(items)
                for itemset in self.candidates:
                    if set(itemset).issubset(items):
                        itemset_transac_util = 0
                        for item in itemset:
                            itemset_transac_util += item_util_dict[item]
                        itemset_tuple = tuple(itemset)
                        if itemset_tuple in itemset_util_dict:
                            itemset_util_dict[itemset_tuple] += itemset_transac_util
                        else:
                            itemset_util_dict[itemset_tuple] = itemset_transac_util

        # output each candidate itemset with util >= minutil
        with open(self.output_path, "w") as self.output_file:
            for itemset, util in itemset_util_dict.items():
                if util >= self.minutil:
                    self.hui_count += 1
                    line = []
                    for item in itemset:
                        line.append(str(item))
                    line.append("#UTIL:")
                    line.append(str(util))
                    self.output_file.write(" ".join(line) + "\n")

        self.runtime = (time.time() - start_time) * 1_000

    @staticmethod
    def itemset_generation(k_min_one_itemsets: list[list[int]]) -> list[list[int]]:
        """
        Generate candidate itemsets of length k using
        itemsets of length k-1 via algorithm described in
        Data Mining - The Textbook (page 100 - 101).
        """
        k_itemsets = []
        # compare all pairs of candidate itemsets of length k-1
        for i in range(len(k_min_one_itemsets)):
            k_min_1_itemset_i = k_min_one_itemsets[i]
            for j in range(i + 1, len(k_min_one_itemsets)):
                k_min_1_itemset_j = k_min_one_itemsets[j]
                # check to see if all but the last items are the same in the two itemsets
                if k_min_1_itemset_i[:-1] == k_min_1_itemset_j[:-1]:
                    k_itemset = k_min_1_itemset_i[:-1]
                    # add last item of the two itemsets in order
                    if k_min_1_itemset_i[-1] < k_min_1_itemset_j[-1]:
                        k_itemset.append(k_min_1_itemset_i[-1])
                        k_itemset.append(k_min_1_itemset_j[-1])
                    else:
                        k_itemset.append(k_min_1_itemset_j[-1])
                        k_itemset.append(k_min_1_itemset_i[-1])
                    k_itemsets.append(k_itemset)
        return k_itemsets

    def print_stats(self) -> None:
        """
        Print statistics for the Two Phase algorithm.
        """
        print("===============Two Phase ALGORITHM STATS===============")
        print(f"total runtime (ms): {self.runtime}")
        print(f"total itemset count: {self.itemset_count}")
        print(f"high utility itemset count: {self.hui_count}")
        print(f"candidate itemset count: {self.candidate_count}")
        print(f"pruned itemset count: {self.prune_count}")
        print(f"maximum memory used (MB): {self.mem_usage}")
        print(f"total transaction utility: {self.total_trans_util}")


if __name__ == "__main__":
    args = sys.argv
    input_path = args[1]
    output_path = args[2]
    minutil = int(args[3])
    two_phase = TwoPhase(input_path, output_path, minutil)
    two_phase.run()
    two_phase.print_stats()
