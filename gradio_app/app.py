import sys
import json

import gradio as gr
import pandas as pd

from text import CITATION_BUTTON_LABEL, CITATION_BUTTON_TEXT, INTRODUCTION_TEXT, TITLE_TEXT, TASK_DESCRIPTION

with open("app.css") as f:
    css_code = f.read()

demo = gr.Blocks(css=css_code)

with open("current_results.json") as f:
    result_list = json.load(f)

df = pd.DataFrame(result_list)

df["Model"] = df.apply(lambda x: f"<a style='text-decoration: underline' href='{x['link']}'>{x['Model']}</a>" if isinstance(x["link"], str) else x["Model"], axis=1)

# Sort columns by aoc_original, aoc_leet, euler_original, euler_story
df = df[["Model", "instruction_only", "aoc_original", "aoc_leet", "euler_original", "euler_story"]]

df["instruction_only"] = df["instruction_only"].map({True: 1, False: 0})


average_scores = df.iloc[:, 2:].mean(axis=1).round(2)

# Replace Column names
df.columns = ["Model", "Evaluation", "AOC Original",
              "AOC Leet", "Euler Original", "Euler Story"]

average_scores = df.iloc[:, 2:].mean(axis=1).round(2)
df.insert(loc=2, column="⬆️ Average", value=average_scores)
df = df.sort_values(by=["Evaluation", "⬆️ Average"], ascending=[True, False])
df["Evaluation"] = df["Evaluation"].map({1: "🔶", 0: "🟩"})

with demo:
    gr.HTML(f"<h2 style='text-align: center'>{TITLE_TEXT}</h2>")
    # gr.HTML('<hr>')
    gr.HTML(f"<h3>{INTRODUCTION_TEXT}<h3>")
    gr.HTML('<hr class="dotted">')

    gr.HTML("<h3>📊 Results</h3>")
    gr.HTML("<p>Results are reported as <b>Pass@3 Accuracy</b>.</p>")
    with gr.Tabs() as tabs:
        with gr.TabItem("All"):
            gr.components.Dataframe(
                value=df,
                datatype=["html"]

            )
        with gr.TabItem("AoC"):
            aoc_df = df[["Model", "Evaluation", "AOC Original", "AOC Leet"]]
            average_scores = aoc_df.iloc[:, 2:].mean(axis=1).round(2)
            aoc_df.insert(loc=2, column="⬆️ Average", value=average_scores)
            aoc_df = aoc_df.sort_values(by=["Evaluation", "⬆️ Average"], ascending=[False, False])
            gr.components.Dataframe(
                value=aoc_df,
                datatype=["html"]
            )

        with gr.TabItem("Euler"):
            euler_df = df[["Model", "Euler Original", "Euler Story"]]
            average_scores = euler_df.iloc[:, 1:].mean(axis=1).round(2)
            euler_df.insert(loc=1, column="⬆️ Average", value=average_scores)
            euler_df = euler_df.sort_values(by="⬆️ Average", ascending=False)
            gr.components.Dataframe(
                value=euler_df,
                datatype=["html"]
            )

    gr.HTML("<h3>Legend</h3>")
    gr.HTML("<p>🔶: Evaluated only on the first part of each AoC day</p>")
    gr.HTML("<p>🟩: Complete Evaluation</p>")

    with gr.Row():
        with gr.Accordion("📙 Citation", open=False):
            citation_button = gr.Textbox(
                value=CITATION_BUTTON_TEXT,
                label=CITATION_BUTTON_LABEL,
                lines=20,
                elem_id="citation-button",
                show_copy_button=True,
            )

demo.launch()
