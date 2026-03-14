import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
from prfs.cli import fetch
from prfs.thread import Thread, ThreadComment


@pytest.fixture
def sample_thread():
    return Thread(
        id="abc123",
        file_path="src/utils.js",
        line=42,
        patch="diff content",
        comments=[ThreadComment(author="alice", body="Test comment")],
    )


@pytest.fixture
def sample_thread_no_comments():
    return Thread(
        id="abc123",
        file_path="src/utils.js",
        line=42,
        patch="diff",
        comments=[],
    )


def mock_fetch(thread, pr_number=123, content="rendered content"):
    mock_client = MagicMock()
    mock_client.fetch_pr_review_comments.return_value = [thread]
    return patch.multiple(
        "prfs.cli",
        get_repo_info=lambda cwd=None: ("owner", "repo"),
        get_current_branch=lambda cwd=None: "feature-branch",
        find_pr_for_branch=lambda owner, repo, branch, cwd=None: pr_number,
        GitHubClient=lambda owner, repo: mock_client,
        render_thread_to_markdown=lambda thread: content,
    )


def mock_no_pr():
    return patch.multiple(
        "prfs.cli",
        get_repo_info=lambda cwd=None: ("owner", "repo"),
        get_current_branch=lambda cwd=None: "feature-branch",
        find_pr_for_branch=lambda owner, repo, branch, cwd=None: None,
    )


class TestFetch:
    def test_writes_thread_content_to_file(self, sample_thread, temp_repo):
        with mock_fetch(sample_thread):
            fetch(str(temp_repo))

        expected_file = temp_repo / ".prfs" / "123" / "abc123.md"
        assert expected_file.exists()

    def test_writes_correct_content(self, sample_thread, temp_repo):
        with mock_fetch(sample_thread, content="rendered content"):
            fetch(str(temp_repo))

        expected_file = temp_repo / ".prfs" / "123" / "abc123.md"
        assert expected_file.read_text() == "rendered content"

    def test_raises_when_no_pr_found(self, temp_repo):
        with mock_no_pr():
            with pytest.raises(SystemExit, match="No PR found"):
                fetch(str(temp_repo))

    def test_raises_when_not_git_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            with pytest.raises(SystemExit, match="Not a git repository"):
                fetch(str(repo_path))

    def test_creates_prfs_directory(self, sample_thread_no_comments, temp_repo):
        with mock_fetch(sample_thread_no_comments, pr_number=456, content="content"):
            fetch(str(temp_repo))

        prfs_dir = temp_repo / ".prfs" / "456"
        assert prfs_dir.exists()
        assert prfs_dir.is_dir()
