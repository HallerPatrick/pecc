import json
import os
import sys
from typing import List, Dict

import pandas as pd


def collect_results(folder_path: str) -> List[Dict]:
    results = []

    # folder = "/home/phmaker/Projects/pecc/extra_results"
    for model in os.listdir(folder_path):
        for subset in ["aoc", "aoc_converted", "euler", "euler_stories"]:
            for kpass in [3]:
                if "gpt" in model:
                    model_name = "gpt3.5"
                else:
                    model_name = model.replace("-", "_")
                file_name = "{}-{}-pass@{}.csv".format(model_name, subset, kpass)
                if os.path.exists(os.path.join(folder_path, model, file_name)):
                    print("Evaluating {}".format(file_name))
                    df = pd.read_csv(os.path.join(folder_path, model, file_name))
                    # Remove duplicates
                    if "euler" in subset:
                        df = df.drop_duplicates(subset=["id"])
                    else:
                        df = df.drop_duplicates(subset=["year", "day", "part"])

                    df = df[df["status"] != "no_error"]
                    df = df[df["status"] != "part1_failed"]
                    total_errors = len(df)
                    results.append(
                        {
                            "model": model,
                            "subset": subset,
                            "total_errors": total_errors,
                            "syntax_errors": len(df[df["status"] == "syntax_error"])
                            / total_errors,
                            "runtime_errors": len(df[df["status"] == "runtime_error"])
                            / total_errors,
                            "timeout_errors": len(df[df["status"] == "timeout_error"])
                            / total_errors,
                            "runtime_errors": len(df[df["status"] == "runtime_error"])
                            / total_errors,
                            "wrong_outputs": len(df[df["status"] == "wrong_output"])
                            / total_errors,
                        }
                    )

    return results


def build_latex_table(results: List[Dict]) -> str:
    df = pd.DataFrame.from_dict(results)

    cols_order = [
        "model",
        "subset",
        "syntax_errors",
        "runtime_errors",
        "timeout_errors",
        "wrong_outputs",
        "total_errors",
    ]

    # Convert error rates to percentages and round to one decimal place
    error_types = ["syntax_errors", "runtime_errors", "timeout_errors", "wrong_outputs"]
    for error in error_types:
        df[error] = (df[error] * 100).round(1)

    # Reorder columns
    df = df[cols_order]

    def latex_color_cells(val):
        # Determine the color percentage based on the value
        color_percentage = int(val // 5)
        # Define the color name based on the percentage
        color_name = f"color{color_percentage}"
        return f"\\cellcolor{{{color_name}}} {val}"

    for col in ["syntax_errors", "runtime_errors", "timeout_errors", "wrong_outputs"]:
        df[col] = df[col].apply(latex_color_cells)

    def format_subset(val):
        return {
            "aoc": "AoC",
            "aoc_converted": "AoC-Leet",
            "euler": "Euler",
            "euler_stories": "Euler-Stories",
        }[val]

    df["subset"] = df["subset"].apply(format_subset)

    latex_table = df.to_latex(index=False, escape=False)

    return latex_table


def main(folder_path: str):
    results = collect_results(folder_path)
    latex_table = build_latex_table(results)
    print(latex_table)


if __name__ == "__main__":
    folder_path = sys.argv[1]
    main(folder_path)
