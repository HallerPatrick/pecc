import json
from pathlib import Path
from collections import defaultdict

from datasets import Dataset

def load_dataset(dataset_name: str, root_dir: str) -> Dataset:
    if dataset_name == "aoc":
        return load_aoc(root_dir)
    elif dataset_name == "euler":
        return load_euler(root_dir)
    else:
        raise ValueError(f"Unknown dataset {dataset_name}")


def load_aoc(root_dir: str) -> Dataset:

    root_path = Path(root_dir)

    # Let sort first
    years = list(map(lambda x: int(x.name), list(root_path.glob("*"))))
    years.sort()

    samples = defaultdict(list)

    for year in years:
        year_dir = root_path / str(year)
        days = list(map(lambda x: int(x.name.replace("day_", "").replace(".json", "")), list(year_dir.glob("day_*.json"))))
        days.sort()

        for day in days:
            day_file = year_dir / f"day_{day}.json"
            try:
                with open(day_file, "r") as f:
                    challenge_data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                print(day_file)
                print(e.msg)
                continue

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

    return Dataset.from_dict(samples)


def load_euler(root_dir: str) -> Dataset:
    root_path = Path(root_dir)

    # json looks like this
    # euler_stories_dif_10.json, euler_stories_dif_15.json

    samples = defaultdict(list)

    for json_file in root_path.iterdir():
        with open(json_file, "r") as f:
            data = json.load(f)

        for story in data:
            samples["id"].append(story["id"])
            samples["title"].append(story["title"])
            samples["problem"].append(story["problem"])
            samples["difficulty"].append(story["difficulty"])
            samples["solution"].append(story["solution"])
            samples["story_problem"].append(story["story"])

    return Dataset.from_dict(samples)
