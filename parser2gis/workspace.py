"""Git workspace validation utilities."""

import subprocess
import sys
from typing import Any


class WorkspaceError(Exception):
    """Raised when the workspace environment is not properly configured."""


def _git(*args: str) -> subprocess.CompletedProcess[Any]:
    """Run a git command and return the result."""
    try:
        return subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        raise WorkspaceError("Git is not installed or not in PATH")
    except subprocess.TimeoutExpired:
        raise WorkspaceError("Git command timed out")


def validate_workspace() -> None:
    """Validate that the current workspace is a healthy Git repository.

    Checks:
    - Current directory is inside a Git repository.
    - Git is installed and reachable.
    - Repository has at least one commit.
    - Repository is on a valid branch (not detached HEAD).
    - Working tree is clean (no uncommitted changes to tracked files).

    Raises WorkspaceError if any check fails.
    """
    result = _git("rev-parse", "--show-toplevel")
    if result.returncode != 0:
        raise WorkspaceError("Not inside a Git repository")

    repo_root = result.stdout.strip()

    result = _git("rev-parse", "--abbrev-ref", "HEAD")
    if result.returncode != 0:
        raise WorkspaceError("Repository has no commits yet. Make an initial commit first.")

    branch = result.stdout.strip()
    if branch == "HEAD":
        raise WorkspaceError("Repository is in detached HEAD state")

    result = _git("status", "--porcelain", "--untracked-files=no")
    if result.returncode != 0:
        raise WorkspaceError("Git status check failed")

    if result.stdout.strip():
        raise WorkspaceError(
            f"Working tree is not clean in {repo_root}. "
            "Commit or stash changes before running."
        )


def main() -> None:
    """CLI entry point for workspace validation."""
    try:
        validate_workspace()
        print("Workspace validation passed.")
        sys.exit(0)
    except WorkspaceError as e:
        print(f"Workspace validation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

