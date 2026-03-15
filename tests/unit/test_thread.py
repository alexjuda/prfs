import pytest

from prfs.thread import Thread, ThreadComment


@pytest.fixture
def sample_thread_with_patch():
    return Thread(
        id="abc123",
        file_path="src/utils.js",
        line=42,
        patch=(
            """diff --git a/src/utils.js b/src/utils.js
--- a/src/utils.js
+++ b/src/utils.js
@@ -40,7 +40,7 @@ function getUser() {
  const db = connect();
-  return db.query('users');
+  return await db.query('users');
}"""
        ),
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


class TestRenderToMarkdown:
    @staticmethod
    def test_produces_frontmatter_with_file_location(sample_thread):
        result = sample_thread.render_to_markdown()

        assert result.startswith("---")
        assert "file: src/utils.js:42" in result

    @staticmethod
    def test_produces_frontmatter_with_patch(sample_thread_with_patch):
        result = sample_thread_with_patch.render_to_markdown()

        assert "patch: |" in result
        patch_lines = sample_thread_with_patch.patch.splitlines()
        for patch_line in patch_lines:
            assert patch_line in result

        result_lines = result.splitlines()
        patch_idx = result_lines.index("patch: |")
        for patch_line_i in range(len(patch_lines)):
            rendered_line = result_lines[patch_idx + 1 + patch_line_i]
            assert rendered_line.startswith(" " * 2), "Patch should be indented"

    @staticmethod
    def test_includes_comment_as_markdown_section(sample_thread):
        result = sample_thread.render_to_markdown()

        assert "@alice" in result
        assert "Test comment" in result

    @staticmethod
    def test_renders_includes_multiple_comments(
        sample_thread_multiple_comments,
    ):
        result = sample_thread_multiple_comments.render_to_markdown()

        assert "@alice" in result
        assert "@bob" in result
        assert "First comment" in result
        assert "Second comment" in result

        # This test is toughtly coupled to the implementation because that's the easiest
        # way to test string rendering. It's fine.
        assert (
            result
            == """---
file: src/utils.js:42
patch: |
  diff
---

First comment

~@alice

---

Second comment

~@bob
"""
        )

    @staticmethod
    def test_handles_thread_with_no_comments(sample_thread_no_comments):
        result = sample_thread_no_comments.render_to_markdown()

        assert "file: src/utils.js:42" in result
