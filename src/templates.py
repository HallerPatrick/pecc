from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import LLMChain


class TemplateProvider:
    """
    This class provides templates for the different parts of the interaction with the model.

    The AoC chat template will look like this:

    Part 1:
        {aoc_system_message_template} -> "The following is a progamming task..."
        {human_chat_message} -> "<The task description>"
        Optional: {result_extraction_template} -> "Here is the result of your program: <result>. Extract it""

    Part 2:
        {part_1_chat_history}
        {aoc_part2_chat_template} -> "The following is the second progamming task..."
        Optional: {result_extraction_template}

    Instruction-only:
        {aoc_part1_instruction_template} -> "The following is a progamming task..."
        Optional: {result_extraction_template}

    Euler:
        {euler_instruction_template} -> "The following is a programming task..."
        Optional: {result_extraction_template}

    """

    @staticmethod
    def aoc_part1_instruction_template():
        """Build a chain for the AoC instruction-based interaction with part 1.

        This template will receive the "{description}" placeholder.
        """
        raise NotImplementedError

    @staticmethod
    def aoc_system_message_template():
        """Build a chain for the AoC system message.
        This template will receive no placeholder.
        """
        raise NotImplementedError

    @staticmethod
    def aoc_part2_chat_template():
        """Build a chain for the AoC chat-based interaction with part 2.

        This template will be appended to the previous chain history. Will not receive a placeholder.
        """
        raise NotImplementedError

    @staticmethod
    def result_extraction_template():
        """Build a chain for the AoC result extraction.
        This template will receive the "{program_output}" placeholder.
        """
        raise NotImplementedError

    @staticmethod
    def euler_instruction_template():
        """Build a chain for the Euler instruction-based interaction with part 1.
        This template will receive the "{title}" and "{description}" placeholder.
        """
        raise NotImplementedError


class PaperTemplateProvider(TemplateProvider):

    @staticmethod
    def aoc_part1_instruction_template():
        return """You are a code generator and given a programming task. A file with the input to your program is called 'input.txt'. Generate only directly executable python code."""

    @staticmethod
    def aoc_part2_chat_template():
        return """You are a code generator and given a second part of a programming task. A file with the input to your program is called 'input.txt'. Generate only directly executable python code."""

    @staticmethod
    def result_extraction_template():
        return "Here is the output of your program: '{program_output}'. Please only return the resulting number or text and nothing else."

    @staticmethod
    def aoc_system_message_template():
        return "You are a code generator and given a programming task. A file with the input to your program is called 'input.txt'. Generate only directly executable python code."

    @staticmethod
    def euler_instruction_template():
        return """You are a code generator and given a programming task.
Write a function that efficiently solves the given problem. Generate only directly executable python code.

Title: {title}
Task: {description}"""


class TemplateBuilder:

    def __init__(self, llm, template_provider: TemplateProvider):
        self.llm = llm
        self.template_provider = template_provider

    def build_instruct_chain_part1(self):

        return LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(
                self.template_provider.aoc_part1_instruction_template()),
            verbose=True,
        )

    def build_chat_chain_part1(self):
        return LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_messages(
                [
                    MessagesPlaceholder(variable_name="chat_history"),
                    SystemMessagePromptTemplate.from_template(
                        self.template_provider.aoc_system_message_template()),
                    HumanMessagePromptTemplate.from_template(
                        template="{description}"),
                ]
            ),
            verbose=True,
            memory=ConversationBufferMemory(
                memory_key="chat_history", return_messages=True),
        )

    def build_chat_chain_part2(self, messages):
        return LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(
                self.template_provider.aoc_part2_chat_template()),
            verbose=True,
            memory=ConversationBufferMemory(
                memory_key="chat_history", return_messages=True),
        )

    def build_result_extraction_chain(self):
        return LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(
                self.template_provider.result_extraction_template()),
            verbose=True,
        )

    def build_euler_instruct_chain(self):
        return LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(
                self.template_provider.euler_instruction_template()),
            verbose=True,
        )


def convert_instruct(llm):
    converter_prompt = """You are given an Advent of Code challenge framed as a Christmas story. Extract the core problem and rephrase it into a neutral, technical challenge similar to those found on LeetCode. Pay attention to following aspects:\n1. The challenge has two parts: Part 1 and Part 2. Label them with 'Part 1:' and 'Part 2:'\n2. The input to the program is provided through a seperate text file.\n3. Please include the format of the input file in your challenge.\n4. Replace names with different names. I give you an already converted challenge as a guideline for you.

Already Converted Challenge:
```{converted_challenges}```

Input Challenge - Part1:
{story_part1}

Input Challenge - Part2:
{story_part2}

First 50 Characters of the input:
{sample_input}

"""

    return LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(converter_prompt),
        verbose=True,
    )
