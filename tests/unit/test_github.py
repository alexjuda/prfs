from unittest.mock import patch

from prfs.github import Comment, GitHubClient, User


class TestGithubClient:
    class TestFetchPRReviewComments:
        @staticmethod
        @patch("prfs.github.GitHubClient.get_pr_comments")
        def test_extracts_thread_properties(mock_comments, github_client):
            mock_comments.return_value = [
                Comment(
                    body="Test comment",
                    diff_hunk="@@",
                    line=42,
                    original_line=42,
                    path="src/utils.js",
                    subject_type="line",
                    user=User(login="alice"),
                )
            ]
            result = list(github_client.fetch_pr_review_comments(123))

            assert len(result) == 1
            assert result[0].file_path == "src/utils.js"
            assert result[0].line == 42

        @staticmethod
        @patch("prfs.github.GitHubClient.get_pr_comments")
        def test_extracts_comment_properties(mock_comments, github_client):
            mock_comments.return_value = [
                Comment(
                    body="Test comment",
                    diff_hunk="@@",
                    line=42,
                    original_line=42,
                    path="src/utils.js",
                    subject_type="line",
                    user=User(login="alice"),
                )
            ]
            result = list(github_client.fetch_pr_review_comments(123))

            assert len(result[0].comments) == 1
            comment = result[0].comments[0]
            assert comment.author == "alice"
            assert "Test comment" in comment.body

        @staticmethod
        @patch("prfs.github.GitHubClient.get_pr_comments")
        def test_returns_empty_for_pr_with_no_reviews(mock_comments, github_client):
            mock_comments.return_value = []
            result = list(github_client.fetch_pr_review_comments(123))
            assert result == []

        @staticmethod
        @patch("prfs.github.GitHubClient.get_pr_comments")
        def test_groups_comments_by_file_location(mock_comments, github_client):
            mock_comments.return_value = [
                Comment(
                    body="First",
                    diff_hunk="@@",
                    line=10,
                    original_line=10,
                    path="src/utils.js",
                    subject_type="line",
                    user=User(login="alice"),
                ),
                Comment(
                    body="Second",
                    diff_hunk="@@",
                    line=10,
                    original_line=10,
                    path="src/utils.js",
                    subject_type="line",
                    user=User(login="alice"),
                ),
            ]
            result = list(github_client.fetch_pr_review_comments(123))

            assert len(result) == 1
            assert len(result[0].comments) == 2

        @staticmethod
        @patch("prfs.github.GitHubClient.get_pr_comments")
        def test_separates_comments_on_different_lines(mock_comments, github_client):
            mock_comments.return_value = [
                Comment(
                    body="Comment on line 10",
                    diff_hunk="@@",
                    line=10,
                    original_line=10,
                    path="src/utils.js",
                    subject_type="line",
                    user=User(login="alice"),
                ),
                Comment(
                    body="Comment on line 20",
                    diff_hunk="@@",
                    line=20,
                    original_line=20,
                    path="src/utils.js",
                    subject_type="line",
                    user=User(login="alice"),
                ),
            ]
            result = list(github_client.fetch_pr_review_comments(123))

            assert len(result) == 2
            lines = {thread.line for thread in result}
            assert lines == {10, 20}
