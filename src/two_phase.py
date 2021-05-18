import sys
import os
import time
import csv
from memory_profiler import memory_usage


class TwoPhase:
    def __init__(self, input_path: str, output_path: str, minutil: int) -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.minutil = minutil
        self.itemset_buffer_size = 200
        self.hui_count = 0
        self.prune_count = 0
        self.candidate_count = 0
        self.start_time = 0
        self.end_time = 0

    def run(self) -> None:
        self.mem_usage = memory_usage(self.twophase, max_usage=True, max_iterations=1)

    def twophase(self) -> None:
        self.start_time = time.time()
        all_candidates = set()
        item_twu_dict = {}

        # phase one
        # scan the db to get the twu of all items
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

        print("generating candidates now")
        print(self.minutil)
        # generate candidate set of size 1
        candidates = set()
        for item in item_twu_dict:
            if item_twu_dict.get(item) > self.minutil:
                candidates.add(frozenset({item}))
                all_candidates.add(frozenset({item}))

        item_twu_dict.clear()
        k = 2

        # apriori stuff
        while len(candidates) > 0:
            generated = set()
            pruned = set()
            # generate
            print("generate")
            for item_set in candidates:
                temp1 = set(item_set)
                for item_set_2 in candidates:
                    # convert back to set
                    temp2 = set(item_set_2)
                    # take the union
                    new_set = set.union(temp1, temp2)
                    # if set is right length, add to generated
                    if len(new_set) == k:
                        generated.add(frozenset(new_set))
            # prune
            print("prune")
            for item_set in generated:
                add = True
                for item in item_set:
                    # creates temporary set of size k-1
                    check = set(item_set)
                    check.remove(item)

                    # checks to see if its in the set
                    if check not in candidates:
                        add = False
                if add:
                    pruned.add(frozenset(item_set))
            
            print("done with prune")
            # add pruned itemset to global prune counter
            self.prune_count += len(generated) - len(pruned)

            print("clear")
            print(len(pruned))
            # clear candidates
            candidates.clear()
            # get utility
            print("getting utilities")
            with open(self.input_path) as db:
                for transac in db:
                    transac_data = transac.split(":")
                    transaction = set(transac_data[0].split())
                    transac_util = int(transac_data[1])
                    for item_set in pruned:
                        if all(elem in transaction for elem in item_set):
                            if item_set in item_twu_dict:
                                item_twu_dict[item_set] += transac_util
                            else:
                                item_twu_dict[item_set] = transac_util
            print("adding to candidates")
            # add to candidates
            for item_set in item_twu_dict:
                if item_twu_dict.get(item_set) > self.minutil:
                    candidates.add(frozenset({item_set}))
                    all_candidates.add(frozenset({item_set}))
            item_twu_dict.clear()
            k += 1

        # phase two
        item_set_utility = {}
        with open(self.input_path) as db:
            for transac in db:
                transaction = []
                utilities = []
                transac_data = transac.split(":")
                items = transac_data[0].split()
                item_util = transac_data[2].split()
                for item in items:
                    item = int(item)
                    transaction.append(item)
                for utility in item_util:
                    utility = int(utility)
                    utilities.append(utility)
                for item_set in all_candidates:
                    set_util = 0
                    if all(elem in transaction for elem in item_set):
                        for i in range(len(transaction)):
                            if transaction[i] in item_set:
                                set_util += utilities[i]
                    if set_util > self.minutil:
                        item_set_utility[item_set] = set_util

    def print_stats(self) -> None:
        print("===============Two Phase ALGORITHM STATS===============")
        self.runtime = (self.end_time - self.start_time) * 1000
        print(f"total runtime (ms): {(self.end_time - self.start_time) * 1_000}")
        print(f"high utility itemset count: {self.hui_count}")
        print(f"candidate itemset count: {self.candidate_count}")
        print(f"pruned itemset count: {self.prune_count}")
        print(f"maximum memory used (MB): {max(self.mem_usage)}")

    # initializes csv file by adding column names if csv file does not exist
    def initialize_csv(self, filename) -> None:
        fields = ['minimum utility', 'total runtime (ms)', 'total itemSet count', 'high utility itemSet count',
                  'pruned itemSet count', 'maximum memory used (MB)']

        with open(filename, "w+") as csvfile:
            # creating a csv writer object
            _writer = csv.writer(csvfile)

            # writing the fields
            _writer.writerow(fields)

    # adds rows to the csv file
    def experiment(self, filename) -> None:
        # data rows of csv file
        rows = [[self.minutil, self.runtime,
                self.hui_count,
                self.candidate_count,
                self.prune_count,
                self.mem_usage]]
        with open(filename, "a+", newline='') as csvfile:
            # creating a csv writer object
            _writer = csv.writer(csvfile)

            # writing the data rows
            _writer.writerows(rows)


if __name__ == "__main__":
    args = sys.argv
    twoPhase = TwoPhase(input_path=args[1], output_path=args[2], minutil=int(args[3]))
    twoPhase.run()
    twoPhase.print_stats()
    input_path = args[1]

    # initializes csv file by adding column names if csv file does not exist
    # adds rows to the csv file
    # names the csv file after the name of the input file
    # fetch the current directory
    cur_path = os.getcwd()
    cur_path1 = cur_path.split("/")[:-1] # ensures that we are no longer in src and are instead in experiments

    if not os.path.isdir("/".join(cur_path1)+"/experiments"):
        os.mkdir("/".join(cur_path1)+"/experiments")
    os.chdir("/".join(cur_path1)+"/experiments")

    if "chainstore.txt" in input_path:
        if not os.path.exists("experiment_chain_store2.csv"):
            twoPhase.initialize_csv("experiment_chain_store2.csv")
        twoPhase.experiment("experiment_chain_store2.csv")

    if "DB_Utility.txt" in input_path:
        if not os.path.exists("experiment_DB_Utility2.csv"):
            twoPhase.initialize_csv("experiment_DB_Utility2.csv")
        twoPhase.experiment("experiment_DB_Utility2.csv")

    if "ecommerce_utility_no_timestamps.txt" in input_path:
        if not os.path.exists("experiment_ecommerce_utility_no_timestamps2.csv"):
            twoPhase.initialize_csv("experiment_ecommerce_utility_no_timestamps2.csv")
        twoPhase.experiment("experiment_ecommerce_utility_no_timestamps2.csv")

    if "foodmart.txt" in input_path:
        if not os.path.exists("experiment_food_mart2.csv"):
            twoPhase.initialize_csv("experiment_food_mart2.csv")
        twoPhase.experiment("experiment_food_mart2.csv")

    if "retail.txt" in input_path:
        if not os.path.exists("experiment_retail2.csv"):
            twoPhase.initialize_csv("experiment_retail2.csv")
        twoPhase.experiment("experiment_retail2.csv")
    
    if "kosarak.txt" in input_path:
        if not os.path.exists("experiment_kosarak2.csv"):
            twoPhase.initialize_csv("experiment_kosarak2.csv")
        twoPhase.experiment("experiment_kosarak2.csv")

    if "chess.txt" in input_path:
        if not os.path.exists("experiment_chess2.csv"):
            twoPhase.initialize_csv("experiment_chess2.csv")
        twoPhase.experiment("experiment_chess2.csv")

    # return to the original directory so the shell script can correctly find the path
    cur_path = os.getcwd().split("/")[:-1]
    os.chdir("/".join(cur_path))

