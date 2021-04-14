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
        all_candidates = set()
        item_twu_dict = {}

        # phase one
        with open(self.input_path) as db:
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

        candidates = set()
        for item in item_twu_dict:
            if item_twu_dict.get(item) > self.minutil:
                to_add = set()
                to_add.add(item)
                candidates.add(to_add)
                all_candidates.add(to_add)

        item_twu_dict.clear()
        generated = set()
        pruned = set()
        k = 2
        
        # apriori stuff
        while len(candidates) > 0:
            # generate
            for item_set in candidates:
                for item_set_2 in candidates:
                    new_set = set.union(item_set_2, item_set)
                    if len(new_set) == k:
                        generated.add(new_set)
            # prune
            for item_set in generated:
                add = True
                for item in item_set:
                    check = set()
                    check.union(generated)
                    check.remove(item)
                    if check not in candidates:
                        add = False
                if add:
                    pruned.add(item_set)
            # clear candidates
            candidates.clear()
            # get utility
            with open(self.input_path) as db:
                for transac in db:
                    transaction = set()
                    transac_data = transac.split(":")
                    items = transac_data[0].split()
                    transac_util = int(transac_data[1])
                    for item in items:
                        item = int(item)
                        transaction.add(item)
                    for item_set in pruned:
                        if all(elem in transaction for elem in item_set):
                            item_twu_dict[item_set] += transac_util
                        else:
                            item_twu_dict[item_set] = transac_util
            # add to candidates
            for item_set in item_twu_dict:
                if item_twu_dict.get(item) > self.minutil:
                    candidates.add(item_set)
                    all_candidates.add(item_set)
            k += 1

        # phase two??



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
