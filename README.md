# huim

This project hopes to implement and evaluate the Two-Phase and FHM algorithms for mining high-utility itemsets.

## Environment Setup

1. Create a virtual environment and activate it.
```
python3 -m venv venv
source venv/bin/activate
```
Every time you want to run the scripts you need to activate the virtual environment.

2. Install dependencies.
```
python -m pip install -r requirements.txt
```

## Run Algorithms

To run an algorithm (either `two_phase.py` or `fhm.py`) execute something like:
```
python src/some_algo.py datasets/dataset_name.txt results/result_file_name.txt minutil
```

For example, to run the Two-Phase alogrithm on the DB_Utility.txt dataset with a minutil of 30 and save the results in `results/test_results.txt`, execute the following:
```
python src/two_phase.py datasets/DB_Utility.txt results/test_results.txt 30
```

Similarly, for the FHM algorithm, execute the command below:
```
python src/fhm.py datasets/DB_Utility.txt results/test_results.txt 30
```
