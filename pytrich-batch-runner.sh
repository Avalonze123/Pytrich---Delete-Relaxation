#!/bin/bash

# Configuration
SEARCH="Astar(use_early=True)"
HEURISTIC="LMCOUNT(use_bid=True)"
EXPERIMENT_NAME="parallel-domain-run"
PARTITION="--partition=compute"

DOMAIN_ROOT="ipc2023-domains/total-order"

# Create central log folders
mkdir -p logs/out logs/err

# Loop over each domain folder
for DOMAIN_FOLDER in ${DOMAIN_ROOT}/*; do
    DOMAIN_NAME=$(basename "$DOMAIN_FOLDER")
    DOMAIN_FILE="${DOMAIN_FOLDER}/domain.hddl"

    # Skip if no domain file
    if [ ! -f "$DOMAIN_FILE" ]; then
        echo "Skipping $DOMAIN_NAME (no domain.hddl found)"
        continue
    fi

    echo "Submitting job for domain: $DOMAIN_NAME"

    sbatch $PARTITION -J "domain-${DOMAIN_NAME}" \
        -o "logs/out/out_domain_${DOMAIN_NAME}_%j.out" \
        -e "logs/err/err_domain_${DOMAIN_NAME}_%j.err" \
        pytrich-multirun-domain.sh "$DOMAIN_FILE" "$DOMAIN_FOLDER" "$EXPERIMENT_NAME" "$SEARCH" "$HEURISTIC"
done
