#!/bin/bash

############################################################
# Configuration
############################################################

EXEC="./NuMSD/NuMDS/NuMDS"
INPUT_DIR="graphs_dimacs"
OUTPUT_DIR="results_numds"

PARAM1=600
SEEDS=(10 20 30 40 50)

# Max number of parallel jobs
MAX_JOBS=4

############################################################
# Setup
############################################################

mkdir -p "$OUTPUT_DIR"

echo "======================================"
echo " Starting batch execution"
echo " Instances: $INPUT_DIR"
echo " Output:    $OUTPUT_DIR"
echo " Seeds:     ${SEEDS[*]}"
echo " Max jobs:  $MAX_JOBS"
echo "======================================"

job_count=0

############################################################
# Execution
############################################################

for instance in "$INPUT_DIR"/*.dimacs; do
    # Skip if no files match
    [ -e "$instance" ] || continue

    base_name=$(basename "$instance" .dimacs)

    for seed in "${SEEDS[@]}"; do

        output_file="$OUTPUT_DIR/${base_name}_seed${seed}.out"

        (
            echo "[START] $(date '+%H:%M:%S') | $base_name | seed=$seed"

            timeout -k 10s 600 $EXEC "$instance" $PARAM1 $seed > "$output_file"

           if [ $? -eq 124 ]; then
               echo "[TIMEOUT] $(date '+%H:%M:%S') | $base_name | seed=$seed" >> "$output_file"
           else
               echo "[DONE ] $(date '+%H:%M:%S') | $base_name | seed=$seed"
           fi
        ) &

        ((job_count++))

        # Control parallel jobs
        if (( job_count % MAX_JOBS == 0 )); then
            wait
        fi

    done
done

# Wait for remaining jobs
wait

echo "======================================"
echo " All jobs finished."
echo "======================================"
