import json
import tempfile
from pathlib import Path

import pytest

from prfs.github import GitHubClient
from prfs.thread import Thread, ThreadComment


@pytest.fixture
def temp_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        (repo_path / ".git").mkdir()
        yield repo_path


@pytest.fixture
def github_client():
    return GitHubClient("owner", "repo")


@pytest.fixture
def sample_thread():
    return Thread(
        id="abc123",
        file_path="src/utils.js",
        line=42,
        patch="diff content",
        comments=[ThreadComment(author="alice", body="Test comment")],
    )


def make_gh_api_response(data: list[dict]) -> str:
    return json.dumps(data)
