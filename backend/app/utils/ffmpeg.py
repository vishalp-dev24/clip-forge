# minimal wrappers if needed by future stages
import subprocess
import shlex

# The `run_cmd` function executes a shell command and captures its output.
def run_cmd(cmd: str):
    # The `subprocess.run` function is used to execute the command.
    # `shell=True` allows the command to be run in a shell, enabling shell-specific features.
    # `capture_output=True` ensures that stdout and stderr are captured.
    # `text=True` decodes stdout and stderr as text.
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # The function returns the exit code, stdout, and stderr of the command.
    return proc.returncode, proc.stdout, proc.stderr
