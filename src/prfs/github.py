import subprocess
import json
from prfs.thread import Thread, ThreadComment


class GitHubError(Exception):
    pass


class GitHubClient:
    def __init__(self, owner: str, repo: str):
        self.owner = owner
        self.repo = repo

    def get_pr_reviews(self, pr_number: int) -> list[dict]:
        result = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{self.owner}/{self.repo}/pulls/{pr_number}/reviews",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []
        return json.loads(result.stdout)

    def get_pr_comments(self, pr_number: int) -> list[dict]:
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
            raise GitHubError(
                f"Couldn't fetch comments. Command {cmd} failed. {result.stderr}"
            )
        return json.loads(result.stdout)

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
