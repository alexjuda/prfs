import json
import subprocess
import sys


def validate_gh() -> None:
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(
                "Error: GitHub CLI is not authenticated. Run 'gh auth login' first.",
                file=sys.stderr,
            )
            sys.exit(1)
    except FileNotFoundError:
        print(
            "Error: GitHub CLI (gh) is not installed. Install it from https://cli.github.com/",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"Error checking GitHub CLI: {e}", file=sys.stderr)
        sys.exit(1)


def find_pr_for_branch(
    owner: str, repo: str, branch: str, cwd: str | None = None
) -> int | None:
    result = subprocess.run(
        ["gh", "pr", "view", branch, "--repo", f"{owner}/{repo}", "--json", "number"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    if result.returncode != 0:
        return None

    data = json.loads(result.stdout)
    return data.get("number")


def get_pr_reviews(owner: str, repo: str, pr_number: int) -> list[dict]:
    result = subprocess.run(
        [
            "gh",
            "api",
            f"repos/{owner}/{repo}/pulls/{pr_number}/reviews",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return json.loads(result.stdout)


def get_pr_comments(owner: str, repo: str, pr_number: int) -> list[dict]:
    cmd = [
        "gh",
        "api",
        f"repos/{owner}/{repo}/pulls/{pr_number}/comments",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Couldn't fetch comments. Command {cmd} failed. {result.stderr}"
        )
    return json.loads(result.stdout)
