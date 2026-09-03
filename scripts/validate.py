"""This module runs all checks to ensure the code is in a good state."""

import subprocess
import sys


def run_command(command: list[str], description: str) -> int:
    """Runs a command, prints its status, and returns its exit code.

    Args:
        command (list): The command to run as a list of strings.
        description (str): A description of the check being performed.

    Returns:
        int: The exit code of the command.
    """
    print(f"{description}... ", end="", flush=True)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("failed" if result.returncode else "passed")
    return result.returncode


def validate() -> int:
    """Runs all checks to ensure the code is in a good state.

    Returns:
        int: The combined exit code of all checks.
    """
    exit_code = 0

    # Run type checks
    if run_command(["poetry", "run", "mypy", "grandschemathings/"], "Type check"):
        exit_code = 1

    # Run lint checks
    if run_command(["poetry", "run", "flake8", "."], "Lint check"):
        exit_code = 1
    if run_command(["poetry", "run", "pydocstyle", "."], "Docstring style check"):
        exit_code = 1

    # Run format checks
    if run_command(["poetry", "run", "black", "--check", "."], "Format check"):
        exit_code = 1

    # Run tests
    if run_command(["poetry", "run", "pytest"], "Tests"):
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(validate())
