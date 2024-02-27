import pylint.lint
import pylint.reporters.text
import io
import tempfile

def lint_code_with_pylint_api(code_snippet):
    """
    Lint the given code snippet using pylint's API.

    Args:
    - code_snippet (str): The code snippet to lint.

    Returns:
    - tuple: A tuple containing a list of linting messages and a score.
    """
    # Create a temporary in-memory file (StringIO) to capture the pylint output
    pylint_output = io.StringIO()

    # Custom reporter to capture the pylint messages
    class CustomReporter(pylint.reporters.text.TextReporter):
        def __init__(self, output):
            super().__init__(output)
            self.messages = []

        def handle_message(self, msg):
            self.messages.append(f"{msg.category}: {msg.msg} at Line {msg.line}, Column {msg.column}")

    reporter = CustomReporter(pylint_output)

    # Lint the code snippet using pylint's API
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as temp_file:
        temp_file_name = temp_file.name
        temp_file.write(code_snippet)
        linter = pylint.lint.Run(["--disable=overgeneral-exceptions", temp_file_name], reporter=reporter, do_exit=False)

    # Extract the score
    score = linter.linter.stats.global_note

    return reporter.messages, score

if __name__ == '__main__':
    # Example usage:
    code_snippet = """

def add(a, b):
    return a+b
    """

    messages, score = lint_code_with_pylint_api(code_snippet)
    print("Linting Messages:")
    print("\n".join(messages))
    print("\nScore:", score)
