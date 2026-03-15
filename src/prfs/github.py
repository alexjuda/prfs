import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Literal

import msgspec.json

from prfs.thread import Thread, ThreadComment


@dataclass
class User:
    login: str


@dataclass
class Comment:
    body: str
    diff_hunk: str
    line: int
    original_line: int
    path: str
    subject_type: Literal["line", "file"]
    user: User


class GitHubClient:
    def __init__(self, owner: str, repo: str):
        self.owner = owner
        self.repo = repo

    @staticmethod
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

    def find_pr_for_branch(self, branch: str, cwd: str | None = None) -> int | None:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "view",
                branch,
                "--repo",
                f"{self.owner}/{self.repo}",
                "--json",
                "number",
            ],
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        if result.returncode != 0:
            return None

        data = json.loads(result.stdout)
        return data.get("number")

    def get_pr_comments(self, pr_number: int) -> list[Comment]:
        cmd = [
            "gh",
            "api",
            f"repos/{self.owner}/{self.repo}/pulls/{pr_number}/comments",
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
        return msgspec.json.decode(result.stdout, type=List[Comment])

    def fetch_pr_review_comments(self, pr_number: int) -> list[Thread]:
        comments = self.get_pr_comments(pr_number)
        threads = {}

        for comment in comments:
            thread_id = f"{comment.path}_{comment.line}"

            if thread_id not in threads:
                threads[thread_id] = Thread(
                    id=thread_id,
                    file_path=comment.path,
                    line=comment.line,
                    patch=comment.diff_hunk,
                    comments=[],
                )
            threads[thread_id].comments.append(
                ThreadComment(author=comment.user.login, body=comment.body)
            )

        return list(threads.values())

    def clean_pr(self, pr_number: int, cwd: str | None = None) -> bool:
        prfs_dir = Path(cwd or ".") / ".prfs" / str(pr_number)
        if prfs_dir.exists():
            shutil.rmtree(prfs_dir)
            return True
        return False
