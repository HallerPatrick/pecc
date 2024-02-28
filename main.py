import os
import argparse

import pandas as pd

from src.dataset import load_dataset
from src.pipeline import Runner
from src.config import DatasetConfig, AoCDatasetConfig
from src.eval import pretty_print, evaluate_euler, evaluate_aoc
from src.llm import MODEL_LOADER_MAP


def main():

    argparser = argparse.ArgumentParser()

    argparser.add_argument("--model", type=str, default="gpt-3.5-turbo-16k",
                           help=f"Model to use {list(MODEL_LOADER_MAP.keys())}")
    argparser.add_argument("--subset", type=str, default="aoc",
                           help="Subset of the dataset to use (euler, aoc)")
    argparser.add_argument("--venv-path", type=str,
                           default="pecc_venv", help="Path to the venv")
    argparser.add_argument("--output-file", type=str,
                           default="results.csv", help="Path to output file")
    argparser.add_argument("--instruct", action="store_true", default=False,
                           help="Only run the instruction")
    argparser.add_argument("--kpass", type=int, default=1,
                           help="Number of passes to use")

    args = argparser.parse_args()

    # --- Load Dataset ---
    # Per default, the official AoC dataset is not provided in this repo
    if args.subset == "aoc" and not os.path.exists("dataset/aoc"):
        dataset = load_dataset("aoc", "dataset/aoc_lite")
    else:
        dataset = load_dataset(args.subset, "dataset/{args.subset}")

    assert args.model in MODEL_LOADER_MAP, f"Model {args.model} not found"

    llm = MODEL_LOADER_MAP[args.model](args.model)

    # The venv to use for execution
    python_bin = os.path.join(os.getcwd(), f"{args.venv_path}/bin/python")

    assert os.path.exists(python_bin), f"Venv not found at {python_bin}"

    # For debugging smaller subsets
    if True:
        config = AoCDatasetConfig(
            year_begin=2018,
            year_end=2018,
            day_begin=1,
            day_end=3,
            only_part_one=args.instruct,
            story=False,
            kpass=1
        )
        # config = DatasetConfig.all()
        # config.year_begin = 2021
        # config.kpass = 3
        # config.use_converted = True
    else:
        config = DatasetConfig.from_dataset(args.subset)

    result, one_pass = Runner(llm, dataset, config, python_bin).run()
    pd.DataFrame(result).to_csv(args.output_file)
    pretty_print(result)

    if args.subset == "aoc":
        evaluate_aoc(args.output_file)
    elif args.subset == "euler":
        evaluate_euler(args.output_file)


if __name__ == '__main__':
    main()
