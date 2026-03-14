import pytest
from prfs.thread import render_thread_to_markdown, ThreadComment, Thread


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
def sample_thread_with_patch():
    return Thread(
        id="abc123",
        file_path="src/utils.js",
        line=42,
        patch="@@ -1,2 +1,3 @@",
        comments=[ThreadComment(author="alice", body="Test comment")],
    )


@pytest.fixture
def sample_thread_multiple_comments():
    return Thread(
        id="abc123",
        file_path="src/utils.js",
        line=42,
        patch="diff",
        comments=[
            ThreadComment(author="alice", body="First comment"),
            ThreadComment(author="bob", body="Second comment"),
        ],
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


class TestRenderThreadToMarkdown:
    def test_produces_frontmatter_with_file_location(self, sample_thread):
        result = render_thread_to_markdown(sample_thread)

        assert result.startswith("---")
        assert "file: src/utils.js:42" in result

    def test_produces_frontmatter_with_patch(self, sample_thread_with_patch):
        result = render_thread_to_markdown(sample_thread_with_patch)

        assert "patch: |" in result
        assert "@@ -1,2 +1,3 @@" in result

    def test_includes_comment_as_markdown_section(self, sample_thread):
        result = render_thread_to_markdown(sample_thread)

        assert "@alice" in result
        assert "Test comment" in result

    def test_renders_multiple_comments_as_separate_sections(
        self, sample_thread_multiple_comments
    ):
        result = render_thread_to_markdown(sample_thread_multiple_comments)

        assert "@alice" in result
        assert "@bob" in result
        assert "First comment" in result
        assert "Second comment" in result

    def test_handles_thread_with_no_comments(self, sample_thread_no_comments):
        result = render_thread_to_markdown(sample_thread_no_comments)

        assert "file: src/utils.js:42" in result
