#!/bin/bash

# minutils arrays

db_utility_minutils=(40 30 20)

# retail
retail_minutils=(14910 11930 8947)

# foodmart
foodmart_minutils=(72066 12011 9609)

# kosarak
kosarak_minutils=(5637016 4932390 4227762)

for i in {0..2}; do
    # DB_Utility - for testing
    db_utility_minutil=${db_utility_minutils[i]}
    echo "minutil (DB_Utility): $db_utility_minutil"
    python3 two_phase.py ../datasets/DB_Utility.txt ../results/DB_Utility_two_phase_${db_utility_minutil}.txt $db_utility_minutil

    # retail
    retail_minutil=${retail_minutils[i]}
    echo "minutil (RETAIL): $retail_minutil"
    python3 two_phase.py ../datasets/retail.txt ../results/retail_two_phase_${retail_minutil}.txt $retail_minutil

    # foodmart
    foodmart_minutil=${foodmart_minutils[i]}
    echo "minutil (FOODMART): $foodmart_minutil"
    python3 two_phase.py ../datasets/foodmart.txt ../results/foodmart_two_phase_${foodmart_minutil}.txt $foodmart_minutil

    # kosarak
    kosarak_minutil=${kosarak_minutils[i]}
    echo "minutil (KOSARAK): $kosarak_minutil"
    python3 two_phase.py ../datasets/kosarak.txt ../results/kosarak_two_phase_${kosarak_minutil}.txt $kosarak_minutil
done
