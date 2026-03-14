import pytest
from unittest.mock import patch
from prfs.github import GitHubClient


@pytest.fixture
def sample_review_comment():
    return {
        "body": "Test comment",
        "user": {"login": "alice"},
        "path": "src/utils.js",
        "line": 42,
        "original_line": 42,
        "diff_hunk": "@@",
    }


@pytest.fixture
def sample_review_comment_same_line():
    return [
        {
            "body": "First",
            "user": {"login": "alice"},
            "path": "src/utils.js",
            "line": 10,
            "original_line": 10,
            "diff_hunk": "@@",
        },
        {
            "body": "Second",
            "user": {"login": "alice"},
            "path": "src/utils.js",
            "line": 10,
            "original_line": 10,
            "diff_hunk": "@@",
        },
    ]


@pytest.fixture
def sample_review_comment_different_lines():
    return [
        {
            "body": "Comment on line 10",
            "user": {"login": "alice"},
            "path": "src/utils.js",
            "line": 10,
            "original_line": 10,
            "diff_hunk": "@@",
        },
        {
            "body": "Comment on line 20",
            "user": {"login": "alice"},
            "path": "src/utils.js",
            "line": 20,
            "original_line": 20,
            "diff_hunk": "@@",
        },
    ]


class TestGithubClient:
    class TestFetchPRReviewComments:
        @staticmethod
        @patch.object(GitHubClient, "get_pr_comments")
        def test_extracts_thread_properties(
            mock_get_comments, sample_review_comment, github_client
        ):
            mock_get_comments.return_value = [sample_review_comment]
            result = list(github_client.fetch_pr_review_comments(123))

            assert len(result) == 1
            assert result[0].file_path == "src/utils.js"
            assert result[0].line == 42

        @staticmethod
        @patch.object(GitHubClient, "get_pr_comments")
        def test_extracts_comment_properties(
            mock_get_comments, sample_review_comment, github_client
        ):
            mock_get_comments.return_value = [sample_review_comment]
            result = list(github_client.fetch_pr_review_comments(123))

            assert len(result[0].comments) == 1
            comment = result[0].comments[0]
            assert comment.author == "alice"
            assert "Test comment" in comment.body

        @staticmethod
        def test_returns_empty_for_pr_with_no_reviews(github_client):
            with patch.object(github_client, "get_pr_comments", return_value=[]):
                result = list(github_client.fetch_pr_review_comments(123))
                assert result == []

        @staticmethod
        @patch.object(GitHubClient, "get_pr_comments")
        def test_groups_comments_by_file_location(
            mock_get_comments, sample_review_comment_same_line, github_client
        ):
            mock_get_comments.return_value = sample_review_comment_same_line
            result = list(github_client.fetch_pr_review_comments(123))

            assert len(result) == 1
            assert len(result[0].comments) == 2

        @staticmethod
        @patch.object(GitHubClient, "get_pr_comments")
        def test_separates_comments_on_different_lines(
            mock_get_comments,
            sample_review_comment_different_lines,
            github_client,
        ):
            mock_get_comments.return_value = sample_review_comment_different_lines
            result = list(github_client.fetch_pr_review_comments(123))

            assert len(result) == 2
            lines = {thread.line for thread in result}
            assert lines == {10, 20}
