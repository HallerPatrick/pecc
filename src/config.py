from typing import List, Optional


class DatasetConfig:

    def __init__(self, kpass: int, story: int):
        """Base class for dataset configuration

        Args:
            kpass: How many passes to use for evaluation
            story: Weather to use the story subset or the leet code subset
        """
        self.kpass = kpass
        self.story = story

    @staticmethod
    def from_dataset(dataset_name: str):
        if dataset_name == "aoc":
            return AoCDatasetConfig.all()
        elif dataset_name == "euler":
            return EulerDatasetConfig.all()


class AoCDatasetConfig(DatasetConfig):

    def __init__(self, year_begin: int, year_end: int, day_begin: int, day_end: int, only_part_one: bool = False, story: bool = True, kpass: int = 1) -> None:
        """AoC Dataset Configuration

        Args:
            year_begin: First year to use
            year_end: Last year to use
            day_begin: First day to use
            day_end: Last day to use
            only_part_one: Weather to use only part one of the days (for instruction based models)

        """
        super().__init__(kpass, story)
        self.year_begin = year_begin
        self.year_end = year_end
        self.day_begin = day_begin
        self.day_end = day_end
        self.only_part_one = only_part_one

    @classmethod
    def one_year(cls, year: int, only_part_one: bool = False):
        return cls(year, year, 1, 25, only_part_one=only_part_one)

    @classmethod
    def one_day(cls, year: int, day: int, only_part_one: bool = False):
        return cls(year, year, day, day, only_part_one=only_part_one)

    @classmethod
    def all(cls, only_part_one: bool = False, kpass: int = 1):
        return cls(2015, 2022, 1, 25, only_part_one=only_part_one)


class EulerDatasetConfig(DatasetConfig):

    def __init__(self, kpass: int, story: bool = True, ids_to_ignore: Optional[List[int]] = None) -> None:
        """Euler Dataset Configuration

        Args:
            ids_to_ignore: List of ids to ignore
        """
        super().__init__(kpass, story)
        self.ids_to_ignore = ids_to_ignore or []

    @classmethod
    def all(cls, kpass: int = 1, story: bool = True):
        return cls(kpass, story, ids_to_ignore=None)
