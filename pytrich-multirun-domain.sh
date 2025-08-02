#!/bin/bash -l

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=48G
#SBATCH --partition=compute
#SBATCH --mail-type=ALL
#SBATCH --mail-user=t02pa24@abdn.ac.uk

echo "Started job on $(hostname)"
date

cd "$SLURM_SUBMIT_DIR"
source venv/bin/activate
echo "Activated virtual environment: $VIRTUAL_ENV"

DOMAIN_FILE="$1"
PROBLEMS_DIR="$2"
EXPERIMENT_NAME="$3"
SEARCH="$4"
HEURISTIC="$5"

echo "Domain file: $DOMAIN_FILE"
echo "Searching for problems in: $PROBLEMS_DIR"

# Collect all .hddl files except domain.hddl
PROBLEM_FILES=()
for f in "$PROBLEMS_DIR"/*.hddl; do
    if [[ $(basename "$f") != "domain.hddl" ]]; then
        PROBLEM_FILES+=("$f")
    fi
done

# Exit early if no problems found
if [ ${#PROBLEM_FILES[@]} -eq 0 ]; then
    echo "No problem files found in $PROBLEMS_DIR. Skipping..."
    exit 0
fi

# Create folder for psas outputs
OUTDIR="psas/$(basename "$PROBLEMS_DIR")"
mkdir -p "$OUTDIR"

# Loop over problems and solve them
for PROBLEM_FILE in "${PROBLEM_FILES[@]}"; do
    PROBLEM_NAME=$(basename "$PROBLEM_FILE" .hddl)
    echo ">>> Solving: $PROBLEM_NAME"

    python3 __main__.py "$DOMAIN_FILE" "$PROBLEM_FILE" -e "$EXPERIMENT_NAME" -S "$SEARCH" -H "$HEURISTIC"

    # Move result if generated
    if [ -f "${PROBLEM_NAME}.psas" ]; then
        mv "${PROBLEM_NAME}.psas" "$OUTDIR/"
    fi
done
