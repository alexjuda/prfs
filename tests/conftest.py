import pytest
import tempfile
from pathlib import Path
from prfs.github import GitHubClient


@pytest.fixture
def temp_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        (repo_path / ".git").mkdir()
        yield repo_path


@pytest.fixture
def github_client():
    return GitHubClient("owner", "repo")
