# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ====== CONFIG ======
INPUT_FILE = Path("/scratch/users/t02pa24/Project MSC/Pytrich/logtools/Exports/summary_grouped.xlsx")
OUTPUT_PREFIX = Path("/scratch/users/t02pa24/Project MSC/Pytrich/logtools/Plots/statistics")
# ====================

def load_summary(input_file):
    # Read Excel with two header rows
    df = pd.read_excel(input_file, header=[0, 1])

    # Flatten headers
    df.columns = [
        " ".join([str(c).strip() for c in col if pd.notna(c) and str(c).strip()])
        for col in df.columns.values
    ]

    # First column is Domain
    df.rename(columns={df.columns[0]: "Domain"}, inplace=True)

    # Convert wide ? long
    long_df = df.melt(id_vars=["Domain"], var_name="Combined", value_name="Value")

    # Split "Heuristic Metric"
    long_df[["Heuristic", "Metric"]] = long_df["Combined"].str.split(" ", n=1, expand=True)

    return long_df

def plot_bar(data, y_label, title, output_file):
    if data.empty:
        print(f"[WARNING] No data to plot for {title}. Skipping {output_file}")
        return

    plt.figure(figsize=(12, 6))
    sns.barplot(data=data, x="Domain", y="Value", hue="Heuristic")
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel("Domain")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_file, format="pdf")   # save as vector PDF
    plt.close()
    print(f"[SUCCESS] Saved bar plot to {output_file}")

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"[ERROR] Input file not found: {INPUT_FILE}")

    long_df = load_summary(INPUT_FILE)

    # ---- Coverage ----
    coverage_df = long_df[long_df["Metric"] == "Coverage (%)"].copy()
    plot_bar(
        coverage_df,
        "Coverage (%)",
        "Coverage by Domain and Heuristic",
        f"{OUTPUT_PREFIX}_coverage.pdf"
    )

    # ---- Average Expanded Nodes (solved only) ----
    nodes_df = long_df[long_df["Metric"] == "Avg Nodes Expanded"].copy()
    # Drop text entries like "UNSOLVED"
    nodes_df = nodes_df[nodes_df["Value"].apply(lambda x: isinstance(x, (int, float)))]
    plot_bar(
        nodes_df,
        "Avg Nodes Expanded",
        "Average Expanded Nodes by Domain and Heuristic (Solved only)",
        f"{OUTPUT_PREFIX}_expanded_nodes.pdf"
    )

if __name__ == "__main__":
    main()
