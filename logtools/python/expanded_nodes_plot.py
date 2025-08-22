import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path

# ====== CONFIG ======
INPUT_FILE = Path("/scratch/users/t02pa24/Project MSC/Pytrich/logtools/Exports/final_structured_output.xlsx")
OUTPUT_DIR = Path("/scratch/users/t02pa24/Project MSC/Pytrich/logtools/Plots")
EXPERIMENT_X = "DELRELAX"   # heuristic for x-axis
EXPERIMENT_Y = "TDG"        # heuristic for y-axis
# ====================

def load_data(input_file, experiment_x, experiment_y):
    df = pd.read_excel(input_file, header=[0, 1])

    # Flatten headers
    df.columns = [
        " ".join([str(c).strip() for c in col if pd.notna(c) and str(c).strip()])
        for col in df.columns.values
    ]
    df.rename(columns={df.columns[0]: "Domain", df.columns[1]: "Problem"}, inplace=True)

    col_x = f"{experiment_x} Nodes Expanded"
    col_y = f"{experiment_y} Nodes Expanded"
    status_x = f"{experiment_x} Search Status"
    status_y = f"{experiment_y} Search Status"

    # Keep relevant columns
    data = df[["Domain", "Problem", col_x, col_y, status_x, status_y]].copy()
    data.rename(columns={
        col_x: experiment_x,
        col_y: experiment_y,
        status_x: f"{experiment_x}_status",
        status_y: f"{experiment_y}_status"
    }, inplace=True)

    return data

def clean_numeric(df, x, y):
    """Keep only rows with numeric values for both x and y."""
    df = df.copy()
    df[x] = pd.to_numeric(df[x], errors="coerce")
    df[y] = pd.to_numeric(df[y], errors="coerce")
    df = df.dropna(subset=[x, y])
    return df

def plot_expanded_nodes(data, experiment_x, experiment_y, output_file, title_suffix=""):
    if data.empty:
        print(f"[WARNING] No data to plot for {title_suffix}. Skipping {output_file}")
        return

    plt.figure(figsize=(10, 8))
    sns.scatterplot(
        data=data,
        x=experiment_x,
        y=experiment_y,
        hue="Domain",
        palette="tab10",
        s=80,
        edgecolor="w",
        alpha=0.7
    )

    plt.xscale("log")
    plt.yscale("log")

    max_value = data[[experiment_x, experiment_y]].max().max()
    plt.xlim(1, max_value * 1.1)
    plt.ylim(1, max_value * 1.1)

    plt.plot([1, 1e8], [1, 1e8], ls="--", color="red", label="x = y")
    plt.xlabel(experiment_x)
    plt.ylabel(experiment_y)
    plt.title(f"Expanded Nodes: {experiment_x} vs {experiment_y} {title_suffix}")
    plt.legend(title="Domain", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(output_file, format="pdf")
    plt.close()
    print(f"[SUCCESS] Saved scatter plot to {output_file}")

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"[ERROR] Input file not found: {INPUT_FILE}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data = load_data(INPUT_FILE, EXPERIMENT_X, EXPERIMENT_Y)

    # 1. Solved only
    solved_data = data[
        (data[f"{EXPERIMENT_X}_status"] == "SOLVED") &
        (data[f"{EXPERIMENT_Y}_status"] == "SOLVED")
    ]
    solved_data = clean_numeric(solved_data, EXPERIMENT_X, EXPERIMENT_Y)
    print("[DEBUG] Solved-only rows to plot:")
    print(solved_data.head(10))
    plot_expanded_nodes(solved_data, EXPERIMENT_X, EXPERIMENT_Y,
                        OUTPUT_DIR / "expanded_nodes_solved.pdf",
                        "(solved only)")

    # 2. All non-empty
    full_data = clean_numeric(data, EXPERIMENT_X, EXPERIMENT_Y)
    print("[DEBUG] All non-empty rows to plot:")
    print(full_data.head(10))
    plot_expanded_nodes(full_data, EXPERIMENT_X, EXPERIMENT_Y,
                        OUTPUT_DIR / "expanded_nodes_full.pdf",
                        "(all non-empty)")

if __name__ == "__main__":
    main()
