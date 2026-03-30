#!/bin/bash

############################################################
# Configuration
############################################################

EXEC="./KMis/KaMIS/deploy/redumis"
INPUT_DIR="graphs_metis"
OUTPUT_DIR="results_redumis"

SEEDS=(10 20 30 40 50)
TIME_LIMIT=600

# Parallel jobs
MAX_JOBS=4

############################################################
# Setup
############################################################

mkdir -p "$OUTPUT_DIR"

echo "======================================"
echo " Running KaMIS (redumis)"
echo " Input:     $INPUT_DIR"
echo " Output:    $OUTPUT_DIR"
echo " Seeds:     ${SEEDS[*]}"
echo " TimeLimit: $TIME_LIMIT sec"
echo " Max jobs:  $MAX_JOBS"
echo "======================================"

job_count=0

############################################################
# Execution
############################################################

for instance in "$INPUT_DIR"/*.graph; do
    [ -e "$instance" ] || continue

    base_name=$(basename "$instance" .graph)

    for seed in "${SEEDS[@]}"; do

        output_file="$OUTPUT_DIR/${base_name}_${seed}.out"

        (
            echo "[START] $(date '+%H:%M:%S') | $base_name | seed=$seed"

            timeout -k 10s 650  $EXEC "$instance" \
                --output "$output_file" \
                --time_limit "$TIME_LIMIT" \
                --seed "$seed"
             
           if [ $? -eq 124 ]; then
               echo "[TIMEOUT] $(date '+%H:%M:%S') | $base_name | seed=$seed" >> "$output_file"
           else
               echo "[DONE ] $(date '+%H:%M:%S') | $base_name | seed=$seed"
           fi
        ) &

        ((job_count++))

        # Control parallelism
        if (( job_count % MAX_JOBS == 0 )); then
            wait
        fi

    done
done

wait

echo "======================================"
echo " All KaMIS runs completed."
echo "======================================"
