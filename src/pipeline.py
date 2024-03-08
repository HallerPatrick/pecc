import re
import ast
import copy
from enum import Enum
from pathlib import Path

from tqdm import tqdm


from loguru import logger
import pandas as pd

from .config import DatasetConfig
from .templates import (
    TemplateProvider,
    PaperTemplateProvider,
    TemplateBuilder

)
from .interpreter import PythonInterpreter


class Runner:
    def __init__(
        self,
        llm,
        dataset,
        dataset_config: DatasetConfig,
        python_bin: str,
        template_provider: TemplateProvider = PaperTemplateProvider
    ):
        self.llm = llm
        self.template_provider = TemplateBuilder(llm, template_provider)
        self.dataset = dataset
        self.dataset_config = dataset_config
        self.interpreter = PythonInterpreter(python_bin)

        # Lets sort first
        try:
            self.years = list(set(dataset["year"]))
            self.years.sort()
            self.days = list(set(dataset["day"]))
            self.days.sort()
        except KeyError:
            pass

    def run(self, subset: str, story: bool, output_file: str, kpass: int, ignore=None):
        if subset == "aoc":
            return self.run_aoc(story, output_file, kpass, ignore)
        elif subset == "euler":
            return self.run_euler(story, output_file, kpass, ignore)

        raise ValueError(f"Unknown subset {subset}")

    def to_skip(self, year=None, day=None):
        if year:
            if (
                year < self.dataset_config.year_begin
                or year > self.dataset_config.year_end
            ):
                logger.debug(f"Skipping year {year}")
                return True

            if year > self.dataset_config.year_end:
                logger.debug(f"Skipping year {year}")
                return True

        if day:
            if day < self.dataset_config.day_begin:
                logger.debug(f"Skipping day {day}")
                return True
            if day > self.dataset_config.day_end:
                logger.debug(f"Skipping day {day}")
                return True

        return False

    def run_aoc(self, story: bool, output_file: str, kpass: int, ignore=None):
        results = []
        kpass_results = []

        for year in self.years:
            if self.to_skip(year=year):
                continue

            for day in self.days:
                if self.to_skip(day=day):
                    continue

                if ignore is not None:
                    ignore_day = ignore[(ignore["day"] == day) & (
                        ignore["year"] == year)]
                    if len(ignore_day) == 2:
                        logger.debug(f"Skipping day {day}")
                        continue

                logger.info(f"Running Year {year} Day {day}")

                challenge = get_challenge(self.dataset, year, day)

                for current_kpass in range(kpass):
                    if self.dataset_config.only_part_one:
                        chain_part1 = self.template_provider.build_instruct_chain_part1()
                    else:
                        chain_part1 = self.template_provider.build_chat_chain_part1()

                    code, output, error_type, error_message = self.run_challenge(
                        chain_part1,
                        challenge["part1"] if story else challenge["part1_converted"],
                        challenge["input"],
                        challenge["part1_solution"],
                    )

                    # Always record the first pass
                    if current_kpass == 0:
                        kpass_results.append(
                            {
                                "year": year,
                                "day": day,
                                "part": 1,
                                "status": error_type,
                                "output": output,
                                "expected_output": challenge["part1_solution"],
                                "error": error_message,
                                "code": code,
                                "kpass": current_kpass,
                            }
                        )

                    # If the code is correct or we have reached the last pass
                    if error_type == ErrorType.NO_ERROR or current_kpass == kpass - 1:
                        results.append(
                            {
                                "year": year,
                                "day": day,
                                "part": 1,
                                "status": error_type,
                                "output": output,
                                "expected_output": challenge["part1_solution"],
                                "error": error_message,
                                "code": code,
                                "kpass": current_kpass,
                            }
                        )

                        break

                if self.dataset_config.only_part_one:
                    logger.debug("Skipping part 2")
                    continue

                # If Part 1 fails, Part 2 also fails
                if error_type != ErrorType.NO_ERROR:
                    results.append(
                        {
                            "year": year,
                            "day": day,
                            "part": 2,
                            "status": ErrorType.PART1_FAILED,
                            "output": "",
                            "expected_output": challenge["part2_solution"],
                            "error": "",
                            "code": "",
                        }
                    )
                    continue

                if day == 25:
                    # No part 2 on day 25
                    continue

                messages = chain_part1.memory.chat_memory.messages

                for current_kpass in range(kpass):
                    chain_part2 = self.template_provider.build_chat_chain_part2(
                        copy.deepcopy(messages))
                    code, output, error_type, error_message = self.run_challenge(
                        chain_part2,
                        challenge["part2"] if story else challenge["part2_converted"],
                        challenge["input"],
                        challenge["part2_solution"],
                    )

                    if current_kpass == 0:
                        kpass_results.append(
                            {
                                "year": year,
                                "day": day,
                                "part": 2,
                                "status": error_type,
                                "output": output,
                                "expected_output": challenge["part2_solution"],
                                "error": error_message,
                                "code": code,
                                "kpass": current_kpass,
                            }
                        )

                    if error_type == ErrorType.NO_ERROR or current_kpass == kpass - 1:
                        results.append(
                            {
                                "year": year,
                                "day": day,
                                "part": 2,
                                "status": error_type,
                                "output": output,
                                "expected_output": challenge["part2_solution"],
                                "error": error_message,
                                "code": code,
                                "kpass": current_kpass,
                            }
                        )
                        break

            # pd.DataFrame(kpass_results).to_csv("current_gpt4_aoc_converted-pass@1.csv")
            # pd.DataFrame(results).to_csv("current_gpt4_aoc_converted-pass@3.csv")

            output_file_stem = Path(output_file).stem

            pd.DataFrame(kpass_results).to_csv(
                f"current-{output_file_stem}-pass@1.csv")
            pd.DataFrame(results).to_csv(
                f"current-{output_file_stem}-pass@3.csv")

        return results, kpass_results

    def run_challenge(
        self, chain, description: str, challenge_input: str, solution: str
    ):
        try:
            generated_code = chain.predict(description=description)
        except Exception as e:
            generated_code = "SyntaxError: " + str(e)

        logger.info("======= Generated code =======")
        logger.info(generated_code)
        logger.info("======= End of generated code =======")

        if not is_parseable(generated_code):
            logger.info("Generated output is not syntacticaly correct")
            potential_code = extract_python_code(generated_code)
            if potential_code:
                logger.info("Extracting python snippet from generated output")
                generated_code = potential_code
            else:
                logger.info("Generated output is not parseable")
        else:
            logger.info("Generated output is parseable")

        error_type = ErrorType.NO_ERROR

        output, error_message = self.interpreter.run_code(
            generated_code, challenge_input, timeout=60
        )

        # First check for interpreter errors
        if error_message:
            error_type = parse_error(error_message)
            return generated_code, output, error_type, error_message

        # Then check for output errors
        if not output and error_type != ErrorType.NO_ERROR:
            error_type = ErrorType.NO_OUTPUT

        parsed_output = parse_output(output)

        if parsed_output != solution:
            # extraction_chain = result_extraction_chain(self.llm)
            extraction_chain = self.template_provider.build_result_extraction_chain()
            try:
                final_output = extraction_chain.predict(
                    program_output=parsed_output)
            except Exception as e:
                final_output = parsed_output

            final_parsed_output = parse_output(final_output)

            if final_parsed_output != solution:
                error_type = ErrorType.WRONG_OUTPUT
            else:
                output = final_parsed_output

        return generated_code, output, error_type, error_message

    def run_euler_challenge_answer(self, chain, title: str, description: str, solution: str):

        output = chain.predict(title=title, description=description)

        error_type = ErrorType.NO_ERROR

        parsed_output = parse_output(output)

        try:
            is_int = int(solution)
        except ValueError:
            is_int = False

        if is_int:
            # If the solution is an integer, check if we can extract the last integer from the output
            int_output = re.findall(r"\d+", parsed_output)
            if int_output:
                parsed_output = int_output[-1].strip()

        if parsed_output != solution:
            try:
                int(parsed_output.strip())
                error_type = ErrorType.WRONG_OUTPUT
            except ValueError:
                # extraction_chain = result_extraction_chain(self.llm)
                extraction_chain = self.template_provider.aoc_result_extraction_template()
                final_output = extraction_chain.predict(
                    program_output=parsed_output)
                final_parsed_output = parse_output(final_output)

                if final_parsed_output != solution:
                    error_type = ErrorType.WRONG_OUTPUT
                else:
                    output = final_parsed_output

        return output, error_type

    def run_euler_challenge(
            self, chain, title: str, description: str, solution: str
    ):
        generated_code = chain.predict(title=title, description=description)

        if not is_parseable(generated_code):
            logger.info("Generated output is not syntacticaly correct")
            potential_code = extract_python_code(generated_code)
            if potential_code:
                logger.info("Extracting python snippet from generated output")
                generated_code = potential_code
        else:
            logger.info("Generated output is parseable")

        error_type = ErrorType.NO_ERROR

        output, error_message = self.interpreter.run_code(
            generated_code, "", timeout=60
        )

        # First check for interpreter errors
        if error_message:
            error_type = parse_error(error_message)
            return generated_code, output, error_type, error_message

        # Then check for output errors
        if not output and error_type != ErrorType.NO_ERROR:
            error_type = ErrorType.NO_OUTPUT

        parsed_output = parse_output(output)

        if parsed_output != solution:

            # If the output is a number, then the problem can not be solved
            try:
                int(parsed_output.strip())
                error_type = ErrorType.WRONG_OUTPUT
            except ValueError:
                # extraction_chain = result_extraction_chain(self.llm)
                extraction_chain = self.template_provider.build_result_extraction_chain()
                final_output = extraction_chain.predict(
                    program_output=parsed_output)
                final_parsed_output = parse_output(final_output)

                if final_parsed_output != solution:
                    error_type = ErrorType.WRONG_OUTPUT
                else:
                    output = final_parsed_output

        return generated_code, output, error_type, error_message

    def run_euler(self, story: bool, output_file: str, kpass: int, ignore=None):

        if not ignore:
            ignore = []

        results = []
        kpass_results = []

        for problem in tqdm(self.dataset):

            if problem["id"] in ignore:
                logger.info(f"Skipping problem {problem['id']}")
                continue

            code_generator_prompt = self.template_provider.build_euler_instruct_chain()

            problem_description = (
                problem["story_problem"] if story else problem["problem"]
            )

            for current_kpass in range(kpass):

                code_chain = self.template_provider.build_euler_instruct_chain()

                code, output, error_type, error_message = self.run_euler_challenge(
                    code_chain, problem["title"], problem_description, problem["solution"]
                )

                if current_kpass == 0:
                    kpass_results.append(
                        {
                            "id": problem["id"],
                            "status": error_type,
                            "output": output,
                            "expected_output": problem["solution"],
                            "error": error_message,
                            "code": code,
                            "difficulty": problem["difficulty"],
                        }
                    )

                if error_type == ErrorType.NO_ERROR or current_kpass == kpass - 1:
                    results.append(
                        {
                            "id": problem["id"],
                            "status": error_type,
                            "output": output,
                            "expected_output": problem["solution"],
                            "error": error_message,
                            "code": code,
                            "difficulty": problem["difficulty"],
                        }
                    )

            # pd.DataFrame(kpass_results).to_csv("current-gpt3.5-euler-pass@1.csv")
            pd.DataFrame(results).to_csv("current-gpt3.5-euler-pass@1.csv")

        return results, kpass_results


class ErrorType(str, Enum):
    NO_ERROR = "no_error"
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT_ERROR = "timeout_error"
    WRONG_OUTPUT = "wrong_output"
    NO_OUTPUT = "no_output"
    PART1_FAILED = "part1_failed"


def parse_output(output):
    return output.strip()


def parse_error(error):
    # We should be able to identify following errors based on the output
    # - SyntaxError
    # - RuntimeError

    if "SyntaxError:" in error:
        return ErrorType.SYNTAX_ERROR

    if "TIMEOUT" in error:
        return ErrorType.TIMEOUT_ERROR

    return ErrorType.RUNTIME_ERROR


def get_challenge(dataset, year, day):
    challenge = dataset.filter(lambda x: x["year"] == year and x["day"] == day)
    assert len(challenge) == 1
    return challenge[0]


def extract_python_code(code_block: str) -> str:
    code_snippets = re.findall(r"```python(.*?)```", code_block, re.DOTALL)

    if len(code_snippets) >= 1:
        return "\n".join(code_snippets)

    code_snippets = re.findall(r"```(.*?)```", code_block, re.DOTALL)
    return "\n".join(code_snippets)


def is_parseable(text: str) -> bool:
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False
