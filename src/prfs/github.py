import shutil
from pathlib import Path

from prfs.github_cli import get_pr_comments, get_pr_reviews, validate_gh
from prfs.thread import Thread, ThreadComment


class GitHubError(Exception):
    pass


class GitHubClient:
    def __init__(self, owner: str, repo: str):
        self.owner = owner
        self.repo = repo

    @staticmethod
    def validate_gh() -> None:
        validate_gh()

    def get_pr_reviews(self, pr_number: int) -> list[dict]:
        return get_pr_reviews(self.owner, self.repo, pr_number)

    def get_pr_comments(self, pr_number: int) -> list[dict]:
        return get_pr_comments(self.owner, self.repo, pr_number)

    def fetch_pr_review_comments(self, pr_number: int) -> list[Thread]:
        comments = self.get_pr_comments(pr_number)
        threads = {}

        for comment in comments:
            user = comment.get("user", {}).get("login")
            path = comment.get("path")
            line = comment.get("line") or comment.get("original_line")
            diff_hunk = comment.get("diff_hunk")
            body = comment.get("body")

            thread_id = f"{path}:{line}"
            if thread_id not in threads:
                threads[thread_id] = Thread(
                    id=thread_id,
                    file_path=path,
                    line=line,
                    patch=diff_hunk,
                    comments=[],
                )
            threads[thread_id].comments.append(ThreadComment(author=user, body=body))

        return list(threads.values())

    def clean_pr(self, pr_number: int, cwd: str | None = None) -> bool:
        prfs_dir = Path(cwd or ".") / ".prfs" / str(pr_number)
        if prfs_dir.exists():
            shutil.rmtree(prfs_dir)
            return True
        return False
