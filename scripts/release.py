"""This module upversions, tags, and pushes the project, triggering a release workflow.

Functions:
    release(version_type: str): Upversion, tag, and push the project.
    main(): Parses command-line arguments and initiates the version bump.

Usage:
    poetry run release [patch|minor|major]
"""

import subprocess
import sys

RELEASE_BRANCH = "main"


def run_check(command: list[str]) -> tuple[int, str, str]:
    """Runs a subprocess command and checks for errors.

    Args:
        command (list[str]): The command to run as a list of arguments.

    Returns:
        tuple[int, str, str]: A tuple containing the return code, stdout, and stderr.
    """
    print(">", " ".join(command))
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        print(f"Command '{' '.join(command)}' failed with error:\n{result.stderr}")
        sys.exit(result.returncode)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def release(version_type: str) -> None:
    """Bumps the project version using Poetry and commits the changes to Git.

    Args:
        version_type (str): The type of version bump to perform. Must be one of 'patch',
            'minor', or 'major'.

    Raises:
        subprocess.CalledProcessError: If any of the subprocess commands fail.
    """
    print("Upversioning")
    run_check(["poetry", "version", version_type])

    # Get the new version number
    _, new_version, _ = run_check(["poetry", "version", "-s"])

    print("Commit, tag and push")
    run_check(["git", "add", "pyproject.toml"])
    run_check(["git", "commit", "-m", f"Version {new_version}"])

    # Add an annotated git tag with the new version number
    tag_name = f"v{new_version}"
    run_check(["git", "tag", "-a", tag_name, "-m", f"Version {tag_name}"])

    # Push the commit and the tag to origin
    run_check(["git", "push", "origin", RELEASE_BRANCH])
    run_check(["git", "push", "origin", tag_name])


def main() -> None:
    """Parses command-line arguments and initiates the version bump.

    Raises:
        SystemExit: If the number of arguments is incorrect or the argument is not one
            of 'patch', 'minor', or 'major'.
    """
    if len(sys.argv) != 2 or sys.argv[1] not in ["patch", "minor", "major"]:
        print("Usage: poetry run release [patch|minor|major]")
        sys.exit(1)

    print("Checking branch")
    _, branch, _ = run_check(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if branch != RELEASE_BRANCH:
        print(
            f"Error: You must be on the '{RELEASE_BRANCH}' branch to bump the version."
        )
        sys.exit(1)

    print("Validating code")
    run_check(["poetry", "run", "validate"])

    release(sys.argv[1])


if __name__ == "__main__":
    main()
