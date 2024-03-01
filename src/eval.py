import argparse
import csv
from typing import Dict, List

import pandas as pd

from prettytable.colortable import ColorTable, Themes


def pretty_print(results: List[Dict], subset: str):

    if subset == "euler":
        pass
        # pretty_print_euler(results)
    elif subset == "aoc":
        pretty_print_aoc(results)


def pretty_print_aoc(results: List[Dict]):
    from .pipeline import ErrorType
    print("\nResults:")
    table = ColorTable(theme=Themes.OCEAN)

    # Add the field names (column headers)
    table.field_names = ["Year", "Day", "Part", "Status", "Output", "Expected Output", "Error"]

    # Add rows to the table using the data from the list of dictionaries
    for entry in results:
        status_display = "✔" if entry['status'] == ErrorType.NO_ERROR.value else entry['status']
        table.add_row([entry['year'], entry['day'], entry['part'], status_display, entry['output'].strip(), entry['expected_output'], entry['error']])

    # Print the table
    print(table)


def evaluate(results: List[Dict]):
    df = pd.DataFrame(results)
    breakpoint()
    df.to_csv("results.csv")


def evaluate_euler(csv_file):
    df = pd.read_csv(csv_file)
    total = len(df)
    solved = df[df['status'] == "no_error"]
    print("=== Error Types ===")
    print(f"Syntax Errors:  {len(df[df['status'] == 'syntax_error'])}")
    print(f"Runtime Errors: {len(df[df['status'] == 'runtime_error'])}")
    print(f"Wrong Outputs:  {len(df[df['status'] == 'wrong_output'])}")
    print(f"Timeouts:       {len(df[df['status'] == 'timeout_error'])}")

    print("Accuracy: {:.2f}% ({}/{})".format(len(solved) / total * 100, len(solved), total))


def evaluate_aoc(csv_file):
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
    print("Accuracy: {:.2f}% ({}/{})".format(len(solved) / total * 100, len(solved), total))
    print("Part 1:   {:.2f}% ({}/{})".format(solved_part1 / total_part1 * 100, solved_part1, total_part1))
    print("Part 2:   {:.2f}% ({}/{})".format(solved_part2 / total_part2 * 100, solved_part2, total_part2))


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
        part1_solved[day - 1] = len(df[(df['day'].astype("int") == day) & (df['part'].astype("int") == 1) & (df['status'] == "no_error")])
        part2_solved[day - 1] = len(df[(df['day'].astype("int") == day) & (df['part'].astype("int") == 2) & (df['status'] == "no_error")])

    breakpoint()
    # Plotting the data
    days = list(range(1, 25))

    plt.plot(days, part1_solved, label='Part 1', linestyle='-')
    plt.plot(days, part2_solved, label='Part 2', linestyle='--')

    status_types = df['status'].unique()
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
            part1_solved[day - 1] = len(df[(df['day'].astype("int") == day) & (df['part'].astype("int") == 1) & (df['status'] == "no_error")])
            part2_solved[day - 1] = len(df[(df['day'].astype("int") == day) & (df['part'].astype("int") == 2) & (df['status'] == "no_error")])

        # Plotting the data
        model_name = csv_file.split("/")[-1].replace(".csv", "")

        # plt.plot(days, part1_solved, label=f'Part 1 - {model_name}', linestyle='-')
        # plt.plot(days, part2_solved, label=f'Part 2 - {model_name}', linestyle='--')

        # Combine results for part 1 and part 2
        plt.plot(days, [part1_solved[day - 1] + part2_solved[day - 1] for day in days], label=f'Part 1 + Part 2 - {model_name}')  # , linestyle='-.')

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


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    # Accept a list of csv files
    parser.add_argument('csv_files', nargs='+', help='CSV files to visualize')
    args = parser.parse_args()

    visualize_all_results(args.csv_files)
