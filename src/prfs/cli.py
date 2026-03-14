import json
import subprocess
import sys
from pathlib import Path

from prfs.github import GitHubClient
from prfs.thread import render_thread_to_markdown


def main():
    if len(sys.argv) < 2:
        print("Usage: prfs <command>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "fetch":
        fetch(".")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


def get_current_branch(cwd: str | None = None) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result.stdout.strip()


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


def get_repo_info(cwd: str | None = None) -> tuple[str, str]:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    url = result.stdout.strip()
    if url.startswith("git@github.com:"):
        path = url.replace("git@github.com:", "").replace(".git", "")
    elif url.startswith("https://github.com/"):
        path = url.replace("https://github.com/", "").replace(".git", "")
    else:
        raise ValueError(f"Unknown git remote format: {url}")

    parts = path.split("/")
    return parts[0], parts[1]


def fetch(repo_root: str):
    repo_path = Path(repo_root).resolve()
    if not (repo_path / ".git").exists():
        raise SystemExit("Not a git repository")

    branch = get_current_branch(cwd=str(repo_path))
    owner, repo = get_repo_info(cwd=str(repo_path))
    pr_number = find_pr_for_branch(owner, repo, branch, cwd=str(repo_path))

    if pr_number is None:
        raise SystemExit(f"No PR found for branch: {branch}")

    client = GitHubClient(owner, repo)
    threads = client.fetch_pr_review_comments(pr_number)

    prfs_dir = repo_path / ".prfs" / str(pr_number)
    prfs_dir.mkdir(parents=True, exist_ok=True)

    for thread in threads:
        thread_file = prfs_dir / f"{thread.id}.md"
        content = render_thread_to_markdown(thread)
        thread_file.write_text(content)
        print(f"Written: {thread_file.relative_to(repo_path)}")

    print(f"Fetched {len(threads)} threads for PR #{pr_number}")
