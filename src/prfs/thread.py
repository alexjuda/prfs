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

    def render_to_markdown(self) -> str:
        frontmatter = f"""---
file: {self.file_path}:{self.line}
patch: |
  {self.patch}
---
"""

        comments_md = ""
        for comment in self.comments:
            comments_md += f"\n@{comment.author}:\n\n{comment.body}\n"

        return frontmatter + comments_md
