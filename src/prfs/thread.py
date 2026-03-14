from dataclasses import dataclass


@dataclass
class ThreadComment:
    author: str | None
    body: str | None


@dataclass
class Thread:
    id: str
    file_path: str | None
    line: int | None
    patch: str | None
    comments: list[ThreadComment]


def render_thread_to_markdown(thread: Thread) -> str:
    frontmatter = f"""---
file: {thread.file_path}:{thread.line}
patch: |
  {thread.patch}
---
"""

    comments_md = ""
    for comment in thread.comments:
        comments_md += f"\n@{comment.author}:\n\n{comment.body}\n"

    return frontmatter + comments_md
