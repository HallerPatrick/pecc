<h1 style="text-align: center"> PECC - Problem Extraction and Coding Challenges </h1>

Complementary repository for the paper **"PECC: A Dataset for Problem Extraction and Coding Challenges"** by Patrick Haller, Jonas Golde and Alan Akbik.

<p align="center" style="font-style: italic">
    Our paper got accepted to LREC-Coling 2024! 🥳
</p>

---

<p align="center">
<a href="https://huggingface.co/datasets/PatrickHaller/pecc"> 🤗 Dataset</a>
</br>
<a href="https://huggingface.co/spaces/PatrickHaller/pecc-leaderboard">🏅 Leaderboard</a>
</br>
<a href="">📄 Paper (Coming soon!)</a>
</br>
<!-- Blog Post -->
<a href=""> 📝 Blog Post (Coming soon!)</a>
<p>

---


## Setup 

Create a virtual environment and install the requirements.

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```


Depending on the model in use, you will need to provide the respective API keys, e.g. for the OpenAI model. 

```bash
export OPENAI_API_KEY="your-api-key"
```

## Usage 

The evalation script provides several arguments to configure the evaluation. 

```txt
usage: main.py [-h] [--model MODEL] [--subset SUBSET] [--story] [--venv-path VENV_PATH] [--output-file OUTPUT_FILE] [--instruct] [--kpass KPASS]

optional arguments:
  -h, --help            show this help message and exit
  --model MODEL         Model to use ['gpt-3.5-turbo-16k', 'gpt-3.5-turbo-turbo', 'vertex_ai/chat-bison', 'vertex_ai/codechat-bison', 'vertex_ai/gemini-pro', 'vertex_ai/gemini-1.5-pro', 'WizardCoder-34B', 'mixtral', 'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
  --subset SUBSET       Subset of the dataset to use (euler, aoc)
  --story               Use the story subset of the dataset
  --venv-path VENV_PATH
                        Path to the venv
  --output-file OUTPUT_FILE
                        Path to output file
  --instruct            Only run the instruction
  --kpass KPASS         Number of passes to use
```

> [!NOTE]
> The generated code will be executed by the python environment provide, while we didn't experience any issues, we cannot guarantee the safety of the code. 


## Download original AoC subset

Due to licensing restrictions, we cannot provide the original data from the AoC dataset. However, you can download the original AoC dataset with a bash script we provide. 

Following requirements are needed:
1. First, you need to have a registered account in the [AoC website](https://adventofcode.com/).
2. You need to complete the AoC challenges from 2015 to 2022 to download the respective challenges
3. You need to install the `aoc` CLI tool from [here](https://github.com/scarvalhojr/aoc-cli) and have th `jq` and `sponge` tool installed. 
4. Following the `aoc` [documentation](https://github.com/scarvalhojr/aoc-cli?tab=readme-ov-file#session-cookie-), a session token is needed which can be obtained from the AoC website after login. 


```bash
export ADVENT_OF_CODE_SESSION="your-session-token"
bash tools/download_puzzles.sh
```

Per default, the script will download the AoC challenges from 2015 to 2022 and merge it into 
the `dataset/aoc_lite` directory. Refer to the script for more details.


## Reported Results

All results reported in the paper can be found in the `paper_results` folder. Which contains the
raw output of the evaluation script for all models.

To produce a LaTeX table, run the following command:

```bash
python src.eval.py --results-folder paper_results
```

