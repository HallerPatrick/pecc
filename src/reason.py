
#             only_answer_template = """<s>[INST]You are a mathematician and given a task. Solve this task and generate only the answer.
#
# Title: {title}
# Task: {description}[/INST]"""
#
#
#
#             only_answer_prompt = PromptTemplate.from_template(
#                 template=only_answer_template
#             )
#
#             for kpass in range(self.dataset_config.kpass):
#
#                 code_chain = LLMChain(
#                     llm=self.llm, prompt=only_answer_prompt, verbose=True
#                 )
#
#                 output, error_type = self.run_euler_challenge_answer(
#                     code_chain, problem["title"], problem_description, problem["solution"]
#                 )
#
#                 if kpass == 0:
#                     kpass_answer_results.append(
#                         {
#                             "id": problem["id"],
#                             "status": error_type,
#                             "output": output,
#                             "expected_output": problem["solution"],
#                             "error": "",
#                             "difficulty": problem["difficulty"],
#                         }
#                     )
#
#                 if error_type == ErrorType.NO_ERROR or kpass == self.dataset_config.kpass - 1:
#                     answer_results.append(
#                         {
#                             "id": problem["id"],
#                             "status": error_type,
#                             "output": output,
#                             "expected_output": problem["solution"],
#                             "error": "",
#                             "difficulty": problem["difficulty"],
#                         }
#                     )
#
#             reasoning_template = """<s>[INST]You are a mathematician and given a task that you should solve. 
# If you can, generate only the answer. You should not generate code and
# your final answer at the end should only be the right value.
#
# Title: {title}
# Task: {description}[/INST]"""
#
#             reasoning_prompt = PromptTemplate.from_template(
#                 template=reasoning_template
#             )
#                 
#             for kpass in range(self.dataset_config.kpass):
#
#                 code_chain = LLMChain(
#                     llm=self.llm, prompt=reasoning_prompt, verbose=True
#                 )
#
#                 output, error_type = self.run_euler_challenge_answer(
#                     code_chain, problem["title"], problem_description, problem["solution"]
#                 )
#
#                 if kpass == 0:
#                     kpass_reasoning_results.append(
#                         {
#                             "id": problem["id"],
#                             "status": error_type,
#                             "output": output,
#                             "expected_output": problem["solution"],
#                             "error": "",
#                             "difficulty": problem["difficulty"],
#                         }
#                     )
#
#                 if error_type == ErrorType.NO_ERROR or kpass == self.dataset_config.kpass - 1:
#                     reasoning_results.append(
#                         {
#                             "id": problem["id"],
#                             "status": error_type,
#                             "output": output,
#                             "expected_output": problem["solution"],
#                             "error": "",
#                             "difficulty": problem["difficulty"],
#                         }
#                     )
