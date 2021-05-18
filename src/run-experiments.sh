#!/bin/bash
cd ..
cd src

# sample sizes array

# chess
declare -a sampleSizes5=(646997 539165 431332 323499 215666 107833)

# retail
declare -a sampleSizes1=(14910 11930 8947 5964 2982 1491)

# kosarak
declare -a sampleSizes2=(5637016 4932390 4227762 3523135 2818508 2113881 1409254)

# foodmart
declare -a sampleSizes3=(12011 9609 72066 4804 2402 1201)

# chainstore
declare -a sampleSizes4=(1000000 1200000 1600000 2000000 2400000 2800000)

# go through each of the five sample sizes
for ssize in "${sampleSizes1[@]}"
do
    echo "Sample size (RETAIL): $ssize" 
    # run each algorithm 2 times at each of the 5 sample sizes
    for i in {1..1}
    do
        echo "Run number: $i"
        python3 two_phase.py ../datasets/retail.txt ../results/retail_results2.txt $ssize
    done
done

for ssize in "${sampleSizes2[@]}"
do
    echo "Sample size (KOSARAK): $ssize" 
    # run each algorithm 2 times at each of the 5 sample sizes
    for i in {1..1}
    do
        echo "Run number: $i"
        python3 two_phase.py ../datasets/kosarak.txt ../results/kosarak_results2.txt $ssize
    done
done

for ssize in "${sampleSizes3[@]}"
do
    echo "Sample size (FOODMART): $ssize" 
    # run each algorithm 2 times at each of the 5 sample sizes
    for i in {1..1}
    do
        echo "Run number: $i"
        python3 two_phase.py ../datasets/foodmart.txt ../results/foodmart_results2.txt $ssize
    done
done

for ssize in "${sampleSizes4[@]}"
do
    echo "Sample size (CHAINSTORE): $ssize" 
    # run each algorithm 2 times at each of the 5 sample sizes
    for i in {1..1}
    do
        echo "Run number: $i"
        python3 two_phase.py ../datasets/chainstore.txt ../results/chainstore_results2.txt $ssize
    done
done