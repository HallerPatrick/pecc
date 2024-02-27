import tempfile
import subprocess
import time
import os
import signal


class PythonInterpreter:
    def __init__(self, python_bin_path):
        self.process = None
        self.python_bin_path = python_bin_path

    def run_code(self, code, input_content, timeout=None):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_py_file = os.path.join(tmpdir, "tmp.py")
            tmp_input_file = os.path.join(tmpdir, "input.txt")

            with open(tmp_py_file, "w") as f:
                f.write(code)

            if input_content != "":
                with open(tmp_input_file, "w") as f:
                    f.write(input_content)

            cwd = os.path.abspath(tmpdir)

            self.process = subprocess.Popen(
                [self.python_bin_path, tmp_py_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                preexec_fn=os.setsid,
                cwd=cwd
            )

            start_time = time.time()

            try:
                # Wait for the process to finish or exceed the timeout
                while True:
                    # Check if the process has finished
                    if self.process.poll() is not None:
                        break

                    # Check if the timeout has been exceeded
                    if timeout is not None and time.time() - start_time > timeout:
                        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                        return "", "TIMEOUT"

                    time.sleep(0.1)

                output, error = self.process.communicate()
            except:
                if self.process.poll() is None:
                    self.process.terminate()
                return "", "TIMEOUT"

        return output, error
