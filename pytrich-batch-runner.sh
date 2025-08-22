#!/bin/bash
set -euo pipefail

# ==== CONFIGURATION ====
SEARCH="Astar(use_early=True)"

# Match exactly what's in planner.py HEURISTICS dict
HEURISTICS=(
    "DELRELAX(use_ordering_relaxation=True)"
    "TDG()"
    "HMAX()"
)

EXPERIMENT_NAME="multi-heuristics-total-order"
PARTITION="--partition=compute"

DOMAIN_ROOT="$(realpath ipc2023-domains/total-order)"   # Absolute path

DOMAIN_TIME_MIN=90      # total minutes per domain
PER_PROBLEM_CAP_SEC=600 # seconds per problem

# Create central log folders
mkdir -p logs/out logs/err

# Loop over each domain folder
for DOMAIN_FOLDER in "${DOMAIN_ROOT}"/*; do
    DOMAIN_NAME=$(basename "$DOMAIN_FOLDER")
    DOMAIN_FILE="${DOMAIN_FOLDER}/domain.hddl"

    # Skip if no domain file
    if [ ! -f "$DOMAIN_FILE" ]; then
        echo "Skipping $DOMAIN_NAME (no domain.hddl found)"
        continue
    fi

    echo "Submitting job for domain: $DOMAIN_NAME"

    # Join heuristics array into a single string for passing
    HEURISTIC_LIST=$(IFS=','; echo "${HEURISTICS[*]}")

    sbatch $PARTITION \
        -J "domain-${DOMAIN_NAME}" \
        -o "logs/out/out_domain_${DOMAIN_NAME}_%j.out" \
        -e "logs/err/err_domain_${DOMAIN_NAME}_%j.err" \
        --export=ALL,DOMAIN_TIME_MIN=$DOMAIN_TIME_MIN,PER_PROBLEM_CAP_SEC=$PER_PROBLEM_CAP_SEC \
        pytrich-multirun-domain.sh \
        "$(realpath "$DOMAIN_FILE")" \
        "$(realpath "$DOMAIN_FOLDER")" \
        "$EXPERIMENT_NAME" \
        "$SEARCH" \
        "$HEURISTIC_LIST"
done
