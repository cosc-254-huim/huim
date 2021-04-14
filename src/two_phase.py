import sys
import time
from memory_profiler import memory_usage


class TwoPhase:
    def __init__(self, input_path: str, output_path: str, minutil: int) -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.minutil = minutil
        self.itemset_buffer_size = 200
        self.hui_count = 0
        self.candidate_count = 0
        self.start_time = 0
        self.end_time = 0

    def run(self) -> None:
        self.mem_usage = memory_usage(self.twophase)

    def twophase(self) -> None:
        self.start_time = time.time()
        allCandidates = []

        # first DB scan to get TWU of each item
        item_twu_dict = {}
        entireDB = []
        with open(self.input_path) as db:
            for transac in db:
                transaction = set()
                transac_data = transac.split(":")
                items = transac_data[0].split()
                transac_util = int(transac_data[1])
                for item in items:
                    item = int(item)
                    transaction.add(item)
                    if item in item_twu_dict:
                        item_twu_dict[item] += transac_util
                    else:
                        item_twu_dict[item] = transac_util

        # create list of utility lists and map of itemsets to utility lists
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
        with open(self.input_path) as db:
            for tid, transac in enumerate(db):
                transac_data = transac.split(":")
                items = transac_data[0].split()
                transac_util = int(transac_data[1])
                item_utils = transac_data[2].split()

    def print_stats(self) -> None:
        print("===============Two Phase ALGORITHM STATS===============")
        print(f"total runtime (ms): {(self.end_time - self.start_time) * 1_000}")
        #print(f"high utility itemset count: {self.hui_count}")
        #print(f"candidate itemset count: {self.candidate_count}")
        #print(f"maximum memory used (MB): {max(self.mem_usage)}")


if __name__ == "__main__":
    args = sys.argv
    twoPhase = TwoPhase(input_path=args[1], output_path=args[2], minutil=int(args[3]))
    twoPhase.run()
    twoPhase.print_stats()
