import pandas as pd
from pathlib import Path
import sys

INPUT_FILE = Path("/scratch/users/t02pa24/Project MSC/Pytrich/logtools/Exports/final_structured_output.xlsx")

if not INPUT_FILE.exists():
    sys.exit(f"[ERROR] Input file not found: {INPUT_FILE}")

# Read with two header rows
df = pd.read_excel(INPUT_FILE, header=[0, 1])

# Flatten headers the same way
df.columns = [
    " ".join([str(c).strip() for c in col if pd.notna(c) and str(c).strip()])
    for col in df.columns.values
]

# Force first two columns to correct names
df.rename(columns={df.columns[0]: "Domain", df.columns[1]: "Problem"}, inplace=True)

print("\n[INFO] Column names after cleaning:\n")
for col in df.columns:
    print(f"- {col}")

sys.exit("\n[INFO] End of debug run.")

