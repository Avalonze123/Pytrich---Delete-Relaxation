import pandas as pd
from pathlib import Path
import sys

INPUT_FILE = Path("/scratch/users/t02pa24/Project MSC/Pytrich/logtools/Exports/final_structured_output.xlsx")
HEURISTICS = ["DELRELAX", "TDG", "HMAX"]

if not INPUT_FILE.exists():
    sys.exit(f"[ERROR] Input file not found: {INPUT_FILE}")

# Read with two header rows
df = pd.read_excel(INPUT_FILE, header=[0, 1])

# Flatten headers
df.columns = [
    " ".join([str(c).strip() for c in col if pd.notna(c) and str(c).strip()])
    for col in df.columns.values
]

# Force correct names for first two columns
df.rename(columns={df.columns[0]: "Domain", df.columns[1]: "Problem"}, inplace=True)
df["Domain"] = df["Domain"].ffill()

print(f"[INFO] Loaded {df.shape[0]} rows and {df.shape[1]} columns\n")

# Check Search Status unique values
for heuristic in HEURISTICS:
    col_name = f"{heuristic} Search Status"
    if col_name in df.columns:
        unique_vals = df[col_name].dropna().unique()
        print(f"[DEBUG] {heuristic} Search Status unique values:")
        print(unique_vals)
        print()

# Check solved counts per domain and heuristic
for domain, domain_df in df.groupby("Domain"):
    print(f"[DOMAIN] {domain}")
    for heuristic in HEURISTICS:
        col_name = f"{heuristic} Search Status"
        if col_name in domain_df.columns:
            solved_mask = (
                domain_df[col_name]
                .astype(str)
                .str.strip()
                .str.upper()
                .isin(["SOLVED", "GOAL"])
            )
            print(f"  {heuristic}: solved rows = {solved_mask.sum()} / {len(domain_df)}")
    print()

sys.exit("[INFO] Debug run complete.")

