import json
from typing import List
from collections import defaultdict
from pathlib import Path

import pandas as pd
import datasets

AOC_DESCRIPTION = "Some description here"
EULER_DESCRIPTION = "Some other description here"

PECC_CITATION = """\
@article{haller2024,
    title={PECC - Problem Extraction and Coding Challenges
    author={Patrick Haller and Jonas Golde and Alan Akbik},
    journal={LREC-COLING 2024 - The 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation}
    year={2024}
}
"""

PECC_URL = "https://gitub.com/HallerPatrick/pecc"

URLS = {
    "aoc": "aoc_lite",
    "euler": "euler"
}

class PECCConfig(datasets.BuilderConfig):
    """BuilderConfig for PECC."""

    def __init__(self, features, data_url, citation, url, **kwargs):
        super(PECCConfig, self).__init__(version=datasets.Version("1.0.2", ""), **kwargs)
        self.features = features
        self.data_url = data_url
        self.citation = citation
        self.url = url

class PECC(datasets.GeneratorBasedBuilder):
    """The PECC benchmark."""

    BUILDER_CONFIG_CLASS = PECCConfig

    BUILDER_CONFIGS = [
        PECCConfig(
            name="aoc",
            description=AOC_DESCRIPTION,
            features=["year", "day", "part1", "part1_converted", "part1_solution", "part2_solution", "part2", "part2_converted", "input"],
            data_url="aoc",
            citation=PECC_CITATION,
            url=PECC_URL
        ),
        PECCConfig(
            name="euler",
            description=EULER_DESCRIPTION,
            features=["id", "title", "description", "difficulty", "solution", "story_problem"],
            data_url="euler",
            citation=PECC_CITATION,
            url=PECC_URL
        )
    ]

    def _info(self):
        features = {feature: datasets.Value("string") for feature in self.config.features}

        if self.config.name.startswith("aoc"):
            features["year"] = datasets.Value("int32")
            features["day"] = datasets.Value("int32")
            features["part1"] = datasets.Value("string")
            features["part1_converted"] = datasets.Value("string")
            features["part1_solution"] = datasets.Value("string")
            features["part2"] = datasets.Value("string")
            features["part2_solution"] = datasets.Value("string")
            features["part2_converted"] = datasets.Value("string")
            features["input"] = datasets.Value("string")

        if self.config.name.startswith("euler"):
            features["id"] = datasets.Value("int32")
            features["title"] = datasets.Value("string")
            features["description"] = datasets.Value("string")
            features["difficulty"] = datasets.Value("string")
            features["solution"] = datasets.Value("string")
            features["story_problem"] = datasets.Value("string")

        return datasets.DatasetInfo(
            description=self.config.description,
            features=datasets.Features(features),
            citation=self.config.citation,
            homepage=self.config.url
        )

    def _split_generators(self, dl_manager) -> List[datasets.SplitGenerator]:
        subset_dir = URLS[self.config.name]
        if self.config.name.startswith("aoc"):
            ds = load_aoc_from_dir(subset_dir)
            import os
            print(os.getcwd())
            ds.to_csv(f"{subset_dir}/aoc.tsv", sep="\t", index=False)
        if self.config.name.startswith("euler"):
            ds = load_euler_from_dir(subset_dir)
            ds.to_csv(f"{subset_dir}/euler.tsv", sep="\t", index=False)

        return [
            datasets.SplitGenerator(name=datasets.Split.TEST, gen_kwargs={"filepath": f"{subset_dir}/{self.config.name}.tsv"})
        ]

    def _generate_examples(self, filepath):
        df = pd.read_csv(filepath, sep="\t", encoding="utf-8")
        for _id, instance in df.iterrows():
            yield _id, instance.to_dict()


def load_aoc_from_dir(root_dir: str) -> datasets.Dataset:
    root_path = Path(root_dir)

    # Let sort first
    years = list(map(lambda x: int(x.name), [file for file in list(root_path.glob("*")) if Path(file).is_dir()]))
    years.sort()

    samples = defaultdict(list)

    for year in years:
        year_dir = root_path / str(year)
        days = list(map(lambda x: int(x.name.replace("day_", "").replace(".json", "")), list(year_dir.glob("day_*.json"))))
        days.sort()

        for day in days:
            day_file = year_dir / f"day_{day}.json"
            with open(day_file, "r") as f:
                challenge_data = json.load(f)

            samples["year"].append(year)
            samples["day"].append(day)
            samples["part1"].append(challenge_data["part1"]["description"])
            if "converted_description" in challenge_data["part1"]:
                samples["part1_converted"].append(challenge_data["part1"]["converted_description"])
            samples["part1_solution"].append(challenge_data["part1"]["answer"])
            samples["part2"].append(challenge_data["part2"]["description"])
            if "converted_description" in challenge_data["part2"]:
                samples["part2_converted"].append(challenge_data["part2"]["converted_description"])
            samples["part2_solution"].append(challenge_data["part2"]["answer"])
            if "input" in challenge_data:
                samples["input"].append(challenge_data["input"])

    return datasets.Dataset.from_dict(samples)


def load_euler_from_dir(root_dir: str) -> datasets.Dataset:
    root_path = Path(root_dir)
    samples = defaultdict(list)
    for json_file in root_path.iterdir():
        if not json_file.suffix == ".json":
            continue
        with open(json_file, "r") as f:
            data = json.load(f)
        for story in data:
            samples["id"].append(story["id"])
            samples["title"].append(story["title"])
            samples["problem"].append(story["problem"])
            samples["difficulty"].append(story["difficulty"])
            samples["solution"].append(story["solution"])
            samples["story_problem"].append(story["story"])

    return datasets.Dataset.from_dict(samples)


if __name__ == "__main__":
    ds = datasets.load_dataset(__file__, "euler")
    breakpoint()
