#!/bin/bash

# minutils arrays
db_utility_minutils=(40 30 20)

# chess
chess_minutils=(646997 539165 431332)

# foodmart
foodmart_minutils=(72066 12011 9609)

# BMS
bms_minutils=(2268000 2264000 2260000)

for i in {0..2}; do
    # DB_Utility - for testing
    db_utility_minutil=${db_utility_minutils[i]}
    echo "minutil (DB_Utility): $db_utility_minutil"
    python3 two_phase.py ../datasets/DB_Utility.txt ../results/DB_Utility_two_phase_${db_utility_minutil}.txt $db_utility_minutil
    echo "minutil (DB_Utility) (FHM): $db_utility_minutil"
    python3 fhm.py ../datasets/DB_Utility.txt ../results/DB_Utility_two_phase_${db_utility_minutil}.txt $db_utility_minutil

    # chess
    chess_minutil=${chess_minutils[i]}
    echo "minutil (CHESS): $chess_minutil"
    python3 two_phase.py ../datasets/chess.txt ../results/chess_two_phase_${chess_minutil}.txt $chess_minutil
    echo "minutil (CHESS) (FHM): $chess_minutil"
    python3 fhm.py ../datasets/chess.txt ../results/chess_fhm_${chess_minutil}.txt $chess_minutil

    # foodmart
    foodmart_minutil=${foodmart_minutils[i]}
    echo "minutil (FOODMART): $foodmart_minutil"
    python3 two_phase.py ../datasets/foodmart.txt ../results/foodmart_two_phase_${foodmart_minutil}.txt $foodmart_minutil
    echo "minutil (FOODMART) (FHM): $retail_minutil"
    python3 fhm.py ../datasets/foodmart.txt ../results/foodmart_fhm_${foodmart_minutil}.txt $foodmart_minutil

    # BMS
    bms_minutil=${bms_minutils[i]}
    echo "minutil (BMS): $bms_minutil"
    python3 two_phase.py ../datasets/BMS.txt ../results/BMS_two_phase_${bms_minutil}.txt $bms_minutil
    echo "minutil (BMS) (FHM): $bms_minutil"
    python3 fhm.py ../datasets/BMS.txt ../results/BMS_fhm_${bms_minutil}.txt $bms_minutil
done
