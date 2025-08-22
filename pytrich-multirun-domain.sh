#!/bin/bash -l
set -euo pipefail

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=48G
#SBATCH --partition=compute
#SBATCH --time=05:00:00    # Adjust as needed for bigger runs
#SBATCH --mail-type=ALL
#SBATCH --mail-user=t02pa24@abdn.ac.uk

echo "Started job on $(hostname)"
date

cd "$SLURM_SUBMIT_DIR"
source venv/bin/activate
echo "Activated virtual environment: $VIRTUAL_ENV"

DOMAIN_FILE="$(realpath "$1")"
PROBLEMS_DIR="$(realpath "$2")"
EXPERIMENT_NAME="$3"
SEARCH="$4"
HEURISTICS_CSV="$5"

IFS=',' read -r -a HEURISTICS <<< "$HEURISTICS_CSV"

PER_PROBLEM_CAP_SEC=${PER_PROBLEM_CAP_SEC:-600}

echo "Domain file: $DOMAIN_FILE"
echo "Searching for problems in: $PROBLEMS_DIR"
echo "Per-problem cap: ${PER_PROBLEM_CAP_SEC}s"
echo "Total heuristics: ${#HEURISTICS[@]}"

# Collect .hddl problems (excluding domain.hddl)
PROBLEM_FILES=()
while IFS= read -r -d '' f; do PROBLEM_FILES+=("$f"); done \
  < <(find "$PROBLEMS_DIR" -maxdepth 1 -type f -name "*.hddl" ! -name "domain.hddl" -print0 | sort -z)

if [ ${#PROBLEM_FILES[@]} -eq 0 ]; then
  echo "No problem files found in $PROBLEMS_DIR. Skipping..."; exit 0
fi

OUTDIR_ROOT="psas/$EXPERIMENT_NAME/$(basename "$PROBLEMS_DIR")"
mkdir -p "$OUTDIR_ROOT"

ulimit -v $((48 * 1024 * 1024))

# Loop over each heuristic
for HEURISTIC in "${HEURISTICS[@]}"; do
  SAFE_H=$(echo "$HEURISTIC" | tr -cd '[:alnum:]_=' | sed 's/=$//')
  OUTDIR="$OUTDIR_ROOT/$SAFE_H"
  mkdir -p "$OUTDIR"

  echo "=== Running heuristic: $HEURISTIC ==="

  # Loop over each problem
  for PROBLEM_FILE in "${PROBLEM_FILES[@]}"; do
    PROBLEM_NAME=$(basename "$PROBLEM_FILE" .hddl)
    echo ">>> Solving: $PROBLEM_NAME (cap ${PER_PROBLEM_CAP_SEC}s)"

    if timeout --preserve-status --kill-after=10s -s SIGTERM "${PER_PROBLEM_CAP_SEC}s" \
      bash -c "cd \"$OUTDIR\" && python3 \"$SLURM_SUBMIT_DIR/__main__.py\" \
               \"$DOMAIN_FILE\" \"$PROBLEM_FILE\" -e \"$EXPERIMENT_NAME\" \
               -S \"$SEARCH\" -H \"$HEURISTIC\""; then
      RESULT_STATUS="GOAL"
    else
      RC=$?
      if (( RC == 124 )); then RESULT_STATUS="TIMEOUT(${PER_PROBLEM_CAP_SEC}s)"
      else RESULT_STATUS="FAILED(rc=$RC)"
      fi
    fi
    echo "    Result: $RESULT_STATUS"
  done
done
