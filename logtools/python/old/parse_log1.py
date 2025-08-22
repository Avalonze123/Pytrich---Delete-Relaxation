import os
import re
import pandas as pd

# === CONFIG ===
LOG_FOLDER = "/scratch/users/t02pa24/Project MSC/Pytrich/logs/out"
OUTPUT_FILE = "parsed_log_summary.xlsx"
PER_PROBLEM_CAP_SEC = 600  # <-- set this to match your experiment timeout

# === REGEX PATTERNS ===
solving_pattern = re.compile(r">>>\s*Solving\s*:\s*(\S+)")
config_pattern = re.compile(
    r"Configuration:\s+Domain:\s+(.+?)\s+Problem:\s+(.+?)\s+Search:.*?Heuristic:\s+(\w+)", re.DOTALL)
search_time_pattern = re.compile(r"Search Time \(seconds\)\s*:\s*([\d.]+)")
nodes_pattern = re.compile(r"Nodes Expanded\s*:\s*(\d+)")
status_pattern = re.compile(r"Search Status\s*:\s*(.*)")
solution_size_pattern = re.compile(r"Solution Size\s*:\s*(\d+)")
revisits_pattern = re.compile(r"Revisits Avoided:\s*(\d+)")
fringe_pattern = re.compile(r"Fringe size\s*:\s*(\d+)")
memory_pattern = re.compile(r"Used Memory:\s*([\d.]+)%")

def infer_domain_from_filename(filename):
    """Infer domain name from 'out_domain_<Domain>_<JobID>.out' format."""
    base = os.path.basename(filename)
    if base.startswith("out_domain_") and base.endswith(".out"):
        mid = base[len("out_domain_"):-len(".out")]
        if "_" in mid:
            return "_".join(mid.split("_")[:-1])
        return mid
    return "UNKNOWN"

all_data = []

# === PROCESS EACH FILE ===
for filename in os.listdir(LOG_FOLDER):
    if not filename.endswith(".out"):
        continue

    file_path = os.path.join(LOG_FOLDER, filename)
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        content = file.read()

        # Get all problems mentioned in ">>> Solving:" lines
        problems_found = solving_pattern.findall(content)

        # Split into blocks for per-problem data
        blocks = content.split(">>> Solving:")

        for idx, problem_line in enumerate(problems_found, start=1):
            problem_name = problem_line.split()[0]
            block = blocks[idx] if idx < len(blocks) else ""

            data = {
                "Heuristic": "DELRELAX",  # Default heuristic for your run
                "Domain": infer_domain_from_filename(filename),
                "Problem": problem_name,
                "Search Time": PER_PROBLEM_CAP_SEC,  # Default to timeout
                "Nodes Expanded": "",
                "Search Status": "NOT_STARTED",
                "Solution Size": "",
                "Revisits Avoided": "",
                "Fringe Size": "",
                "Memory Used (%)": ""
            }

            config_match = config_pattern.search(block)
            if config_match:
                data["Domain"], data["Problem"], data["Heuristic"] = config_match.groups()

                # If there's an actual Search Time, overwrite the default
                if match := search_time_pattern.search(block):
                    data["Search Time"] = float(match.group(1))
                if match := nodes_pattern.search(block):
                    data["Nodes Expanded"] = match.group(1)
                if match := status_pattern.search(block):
                    data["Search Status"] = match.group(1)
                if match := solution_size_pattern.search(block):
                    data["Solution Size"] = match.group(1)
                if match := revisits_pattern.search(block):
                    data["Revisits Avoided"] = match.group(1)
                if match := fringe_pattern.search(block):
                    data["Fringe Size"] = match.group(1)
                if match := memory_pattern.search(block):
                    data["Memory Used (%)"] = match.group(1)

            all_data.append(data)

# === OUTPUT TO EXCEL ===
df = pd.DataFrame(all_data)
df.sort_values(by=["Heuristic", "Domain", "Problem"], inplace=True)
df.to_excel(OUTPUT_FILE, index=False)
print(f"? Parsed {len(df)} results into {OUTPUT_FILE} with default timeout for missing times.")
