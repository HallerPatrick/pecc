import os
import argparse

import pandas as pd

from src.dataset import load_dataset
from src.pipeline import Runner
from src.config import DatasetConfig
from src.eval import evaluate_euler, evaluate_aoc
from src.llm import MODEL_LOADER_MAP


def main():

    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo-16k",
        help=f"Model to use {list(MODEL_LOADER_MAP.keys())}",
    )
    argparser.add_argument(
        "--subset",
        type=str,
        default="aoc",
        help="Subset of the dataset to use (euler, aoc)",
    )
    argparser.add_argument(
        "--story", action="store_true", help="Use the story subset of the dataset"
    )
    argparser.add_argument(
        "--venv-path", type=str, default="pecc_venv", help="Path to the venv"
    )
    argparser.add_argument(
        "--output-file", type=str, default="results.csv", help="Path to output file"
    )
    argparser.add_argument(
        "--instruct",
        action="store_true",
        default=False,
        help="Only run the instruction",
    )
    argparser.add_argument(
        "--kpass", type=int, default=1, help="Number of passes to use"
    )

    args = argparser.parse_args()

    # --- Load Dataset ---
    # Per default, the official AoC dataset is not provided in this repo
    if args.subset == "aoc" and not os.path.exists("dataset/aoc"):
        dataset = load_dataset("aoc", "dataset/aoc_lite")
    else:
        dataset = load_dataset(args.subset, f"dataset/{args.subset}")

    assert args.model in MODEL_LOADER_MAP, f"Model {args.model} not found"

    llm = MODEL_LOADER_MAP[args.model]()

    # The venv to use for execution
    if not os.path.isabs(args.venv_path):
        python_bin = os.path.join(os.getcwd(), args.venv_path, "bin/python")
    else:
        python_bin = os.path.join(args.venv_path, "bin/python")

    assert os.path.exists(python_bin), f"Venv not found at {python_bin}"

    # For debugging smaller subsets
    if False:
        config = DatasetConfig.from_dataset(args.subset)
        config.year_begin = 2015
        config.year_end = 2015
    else:
        config = DatasetConfig.from_dataset(args.subset)
    
    # NOTE: In case you want to ignore some solutions
    # NOTE: For Euler
    # ignore = list(set(pd.read_csv("euler_results.csv")[["id"]].values.flatten().tolist()))
    # NOTE: For AoC
    # ignore = pd.read_csv("aoc_results.csv")
    ignore = None

    result, one_pass = Runner.from_subset(
        args.subset, llm, dataset, config, python_bin
    ).run(args.story, args.output_file, args.kpass, ignore=ignore)
    pd.DataFrame(result).to_csv(args.output_file)

    if args.subset == "aoc":
        evaluate_aoc(args.output_file)
    elif args.subset == "euler":
        evaluate_euler(args.output_file)


if __name__ == "__main__":
    main()
