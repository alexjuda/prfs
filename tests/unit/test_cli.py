from unittest.mock import MagicMock, patch

import pytest

from prfs.cli import clean, fetch
from prfs.github import GitHubClient


class TestGhValidation:
    @staticmethod
    @patch("prfs.github.subprocess.run")
    def test_exits_if_gh_not_installed(mock_run):
        mock_run.side_effect = FileNotFoundError("gh")

        with pytest.raises(SystemExit):
            GitHubClient.validate_gh()

    @staticmethod
    @patch("prfs.github.subprocess.run")
    def test_exits_if_gh_not_authenticated(mock_run):
        mock_run.side_effect = Exception("Authentication required")
        with pytest.raises(SystemExit):
            GitHubClient.validate_gh()

    @staticmethod
    @patch("prfs.github.subprocess.run")
    def test_passes_validation_when_gh_ready(mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        GitHubClient.validate_gh()


class TestFetchWithFlags:
    @staticmethod
    @patch("prfs.github.GitHubClient.validate_gh")
    @patch("prfs.github.GitHubClient.get_pr_comments")
    @patch("prfs.cli.get_repo_info")
    def test_fetch_with_pr_flag(
        mock_repo_info, mock_comments, mock_validate, temp_repo
    ):
        mock_repo_info.return_value = ("owner", "repo")
        mock_comments.return_value = []

        fetch(pr=123, repo=str(temp_repo), verbose=False)

        mock_comments.assert_called_once_with(123)

    @staticmethod
    @patch("prfs.github.GitHubClient.validate_gh")
    @patch("prfs.github.GitHubClient.get_pr_comments")
    @patch("prfs.cli.get_repo_info")
    def test_fetch_with_verbose_flag(
        mock_repo_info, mock_comments, mock_validate, temp_repo
    ):
        mock_repo_info.return_value = ("owner", "repo")
        mock_comments.return_value = []

        fetch(pr=1, repo=str(temp_repo), verbose=True)

        mock_comments.assert_called_once_with(1)


class TestClean:
    @staticmethod
    @patch("prfs.github.GitHubClient.validate_gh")
    @patch("prfs.github.GitHubClient.clean_pr")
    @patch("prfs.cli.get_repo_info")
    def test_clean_with_pr_flag(mock_repo_info, mock_clean, mock_validate, temp_repo):
        mock_repo_info.return_value = ("owner", "repo")
        mock_clean.return_value = True

        clean(pr=123, repo=str(temp_repo))

        mock_clean.assert_called_once_with(123, cwd=str(temp_repo))

    @staticmethod
    @patch("prfs.github.GitHubClient.validate_gh")
    @patch("prfs.github.GitHubClient.clean_pr")
    @patch("prfs.cli.get_repo_info")
    @patch("prfs.cli.get_current_branch")
    @patch("prfs.github.GitHubClient.find_pr_for_branch")
    def test_clean_without_pr_flag(
        mock_find_pr, mock_branch, mock_repo_info, mock_clean, mock_validate, temp_repo
    ):
        mock_repo_info.return_value = ("owner", "repo")
        mock_branch.return_value = "feature-branch"
        mock_find_pr.return_value = 456
        mock_clean.return_value = True

        clean(pr=None, repo=str(temp_repo))

        mock_find_pr.assert_called_once()
        mock_clean.assert_called_once_with(456, cwd=str(temp_repo))
