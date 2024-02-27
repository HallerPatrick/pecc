from langchain.prompts.chat import (
    ChatPromptTemplate,
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


def build_instruct_chain_part1(llm):
    prompt_template = """You are a code generator and given a programming task. A file with the input to your program is called 'input.txt'. Generate only directly executable python code.

Task: {description}"""

    return LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(prompt_template),
        verbose=True,
    )


def build_chain_part1(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            system_message_template(),
            HumanMessagePromptTemplate.from_template(template="{description}"),
        ]
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    return LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )


def build_chain_part2(llm, messages):
    prompt = ChatPromptTemplate.from_messages(
        [
            system_message_template(),
            *messages,
            system_message_intermediate_template(),
            HumanMessagePromptTemplate.from_template(template="{description}"),
        ]
    )

    return LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
    )


def result_extraction_chain(llm):
    extraction_prompt = "Here is the output of your program: '{program_output}'. Please only return the resulting number or text and nothing else."

    return LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(extraction_prompt),
        verbose=True,
    )


def system_message_template():
    system_template = "You are a code generator and given a programming task. A file with the input to your program is called 'input.txt'. Generate only directly executable python code."
    return SystemMessagePromptTemplate.from_template(system_template)


def system_message_intermediate_template():
    system_template = "You are a code generator and given a second part of a programming task. A file with the input to your program is called 'input.txt'. Generate only directly executable python code."
    return SystemMessagePromptTemplate.from_template(system_template)


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


def one_shot():
    return """Input Challenge - Part 1:
Santa is trying to deliver presents in a large apartment building, but he can't find the right floor - the directions he got are a little confusing. He starts on the ground floor (floor `0`) and then follows the instructions one character at a time.

An opening parenthesis, `(`, means he should go up one floor, and a closing parenthesis, `)`, means he should go down one floor.

The apartment building is very tall, and the basement is very deep; he will never find the top or bottom floors.

For example:

* `(())` and `()()` both result in floor `0`.
* `(((` and `(()(()(` both result in floor `3`.
* `))(((((` also results in floor `3`.
* `())` and `))(` both result in floor `-1` (the first basement level).
* `)))` and `)())())` both result in floor `-3`.

To *what floor* do the instructions take Santa?

Input Challenge - Part 2:
Now, given the same instructions, find the *position* of the first character that causes him to enter the basement (floor `-1`). The first character in the instructions has position `1`, the second character has position `2`, and so on.

For example:

* `)` causes him to enter the basement at character position `1`.
* `()())` causes him to enter the basement at character position `5`.

What is the *position* of the character that causes Santa to first enter the basement?

First 50 Characters of the input file:
((((()(()(((((((()))(((()((((()())(())()(((()(((((

Converted Challenge - Part 1:
You are given a string of parentheses. You need to find the floor of the building. The floor is defined as the number of opening parentheses minus the number of closing parentheses. The first floor is 0. For example, the string `((()))` results in floor 0. The string `(()(()(` results in floor 3. The string `))(((((` results in floor 3. The string `())` results in floor -1. The string `))(` results in floor -1. The string `)))` results in floor -3.

Input Format:
The input is a string of parentheses.

Converted Challenge - Part 2:
Now, given the same instructions, find the position of the first character that causes you to enter the basement (floor -1). The first character in the instructions has position 1, the second character has position 2, and so on.

Input Format:
The input is a string of parentheses.
"""
