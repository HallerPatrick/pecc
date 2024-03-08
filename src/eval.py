import argparse
import csv
from typing import Dict
from pathlib import Path
from collections import defaultdict

import pandas as pd


def evaluate_euler(csv_file) -> float:
    df = pd.read_csv(csv_file)
    total = len(df)
    solved = df[df['status'] == "no_error"]
    print("=== Error Types ===")
    print(f"Syntax Errors:  {len(df[df['status'] == 'syntax_error'])}")
    print(f"Runtime Errors: {len(df[df['status'] == 'runtime_error'])}")
    print(f"Wrong Outputs:  {len(df[df['status'] == 'wrong_output'])}")
    print(f"Timeouts:       {len(df[df['status'] == 'timeout_error'])}")

    print("Accuracy: {:.2f}% ({}/{})".format(len(solved) /
          total * 100, len(solved), total))

    return len(solved) / total * 100


def evaluate_aoc(csv_file) -> float:
    df = pd.read_csv(csv_file)
    # Remove day 25 part2
    df = df[~((df['day'] == 25) & (df['part'] == 2))]

    total = len(df)
    total_part1 = len(df[df['part'] == 1])
    total_part2 = len(df[df['part'] == 2])

    solved = df[df['status'] == "no_error"]
    solved_part1 = len(solved[solved['part'] == 1])
    solved_part2 = len(solved[solved['part'] == 2])

    print("=== Error Types ===")
    print(f"Syntax Errors:  {len(df[df['status'] == 'syntax_error'])}")
    print(f"Runtime Errors: {len(df[df['status'] == 'runtime_error'])}")
    print(f"Wrong Outputs:  {len(df[df['status'] == 'wrong_output'])}")
    print(f"Timeouts:       {len(df[df['status'] == 'timeout_error'])}")
    print(f"Part 1 failed:  {len(df[df['status'] == 'part1_failed'])}")
    print()
    accuracy = len(solved) / total * 100
    print("Accuracy: {:.2f}% ({}/{})".format(accuracy, len(solved), total))
    print("Part 1:   {:.2f}% ({}/{})".format(solved_part1 /
          total_part1 * 100, solved_part1, total_part1))
    try:
        print("Part 2:   {:.2f}% ({}/{})".format(solved_part2 /
              total_part2 * 100, solved_part2, total_part2))
    except ZeroDivisionError:
        print("Accuracy: 0.00% (0/0)")

    return accuracy


def visualize_results(csv_file):

    import matplotlib.pyplot as plt

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        results = list(reader)
        df = pd.DataFrame(results)

    # Creating lists to hold the number of problems solved on each day for part 1 and part 2
    part1_solved = [0] * 24
    part2_solved = [0] * 24

    # Populating the lists based on the data in the dataframe
    for day in range(1, 25):
        part1_solved[day - 1] = len(df[(df['day'].astype("int") == day) & (
            df['part'].astype("int") == 1) & (df['status'] == "no_error")])
        part2_solved[day - 1] = len(df[(df['day'].astype("int") == day) & (
            df['part'].astype("int") == 2) & (df['status'] == "no_error")])

    breakpoint()
    # Plotting the data
    days = list(range(1, 25))

    plt.plot(days, part1_solved, label='Part 1', linestyle='-')
    plt.plot(days, part2_solved, label='Part 2', linestyle='--')

    status_types = df['status'].unique()

    # Adding labels and title
    plt.xlabel('Day')
    plt.xticks(days)
    plt.ylabel('Problems Solved')
    plt.title('Problem Solving Progress Over 24 Days')

    # Adding a legend to differentiate between part 1 and part 2
    plt.legend()

    # Display the grid
    plt.grid(True)

    # Show the plot
    plt.show()


def visualize_all_results(csv_files):

    import matplotlib.pyplot as plt

    days = list(range(1, 25))

    for csv_file in csv_files:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            results = list(reader)
            df = pd.DataFrame(results)

        # Creating lists to hold the number of problems solved on each day for part 1 and part 2
        part1_solved = [0] * 24
        part2_solved = [0] * 24

        # Populating the lists based on the data in the dataframe
        for day in range(1, 25):
            part1_solved[day - 1] = len(df[(df['day'].astype("int") == day) & (
                df['part'].astype("int") == 1) & (df['status'] == "no_error")])
            part2_solved[day - 1] = len(df[(df['day'].astype("int") == day) & (
                df['part'].astype("int") == 2) & (df['status'] == "no_error")])

        # Plotting the data
        model_name = csv_file.split("/")[-1].replace(".csv", "")

        # plt.plot(days, part1_solved, label=f'Part 1 - {model_name}', linestyle='-')
        # plt.plot(days, part2_solved, label=f'Part 2 - {model_name}', linestyle='--')

        # Combine results for part 1 and part 2
        plt.plot(days, [part1_solved[day - 1] + part2_solved[day - 1]
                 for day in days], label=f'Part 1 + Part 2 - {model_name}')  # , linestyle='-.')

    # status_types = df['status'].unique()
    # for status in status_types:
    #     if status != "ErrorType.NO_ERROR":
    #         day_part1 = sorted(df[(df['part'].astype("int") == 1) & (df['status'] == status)]['day'].astype("int"))
    #         day_part2 = sorted(df[(df['part'].astype("int") == 2) & (df['status'] == status)]['day'].astype("int"))
    #         day_part1 = [day for day in day_part1 if day <= 24]
    #         day_part2 = [day for day in day_part2 if day <= 24]
    #         plt.scatter(day_part1, [part1_solved[day-1] for day in day_part1], label=f'Part 1 {status}', marker='x')
    #         plt.scatter(day_part2, [part2_solved[day-1] for day in day_part2], label=f'Part 2 {status}', marker='x')

    # Adding labels and title
    plt.xlabel('Day')
    plt.xticks(days)
    plt.ylabel('Problems Solved')
    plt.title('Problem Solving Progress Over 24 Days')

    # Adding a legend to differentiate between part 1 and part 2
    plt.legend()

    # Display the grid
    plt.grid(True)

    # Show the plot
    plt.show()


def print_latex_table(results: Dict):
    content = [
        "\\begin{tabular}{lcccccccc}",
        "\\toprule",
        "Model & \\multicolumn{2}{c}{AoC} & \\multicolumn{2}{c}{AoC-Leet} & \\multicolumn{2}{c}{Euler} & \\multicolumn{2}{c}{Euler-Stories} \\\\",
        "& $k = 1$ & $k = 3$ & $k = 1$ & $k = 3$ & $k = 1$ & $k = 3$ & $k = 1$ & $k = 3$ \\\\",
        "\\midrule",
    ]

    for model in results:
        row = []
        for subset in ["aoc", "euler"]:
            for subsubset in ["original", "leet", "story"]:
                if subset in results[model] and subsubset in results[model][subset]:
                    row.append(
                        f"{results[model][subset][subsubset]['1']:.2f} & {results[model][subset][subsubset]['3']:.2f}")
        content.append(f"{model.replace('_', '-')} & {' & '.join(row)} \\\\")

    print("\n".join(content))

    content.extend([
        "\\bottomrule",
        "\\end{tabular}"
    ])

    print("\n".join(content))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--result-file",
        type=str,
        help="CSV file containing the results"
    )

    parser.add_argument(
        "--results-folder",
        # default="paper_results",
        type=str,
        help="Folder containing the results. Should be in the form <results-folder>/<model>/<result>.csv"
    )

    args = parser.parse_args()

    if args.result_file and args.results_folder:
        raise ValueError("Only one of --result-file or --results-folder should be provided")

    if args.result_file:
        try:
            evaluate_aoc(args.result_file)
        except:
            evaluate_euler(args.result_file)

        exit()

    results_folder = Path(args.results_folder)
    assert results_folder.exists(
    ), f"Results folder {results_folder} does not exist"

    results = {}

    for model_folder in results_folder.iterdir():
        if model_folder.is_dir():
            model_name = model_folder.name
            print(f"Model: {model_name}")
            for result_file in model_folder.iterdir():

                model_name, subset, passk = result_file.stem.split("-")

                _, passK = passk.split("@")

                if model_name not in results:
                    results[model_name] = {}

                try:
                    subset, story_mode = subset.split("_")
                except ValueError:
                    subset, story_mode = subset, None

                if subset not in results[model_name]:
                    results[model_name][subset] = {}

                if result_file.suffix == ".csv":
                    if "aoc" == subset:
                        acc = evaluate_aoc(result_file)
                        subsubset = "leet" if story_mode else "original"

                    elif "euler" == subset:
                        acc = evaluate_euler(result_file)
                        subsubset = "story" if story_mode else "original"

                    if subsubset not in results[model_name][subset]:
                        results[model_name][subset][subsubset] = defaultdict(
                            float)
                    results[model_name][subset][subsubset][passK] = acc

    print_latex_table(results)
