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
        patch_lines = (self.patch or "").splitlines()
        indented = [f"  {line}" for line in patch_lines]
        frontmatter = f"""---
file: {self.file_path}:{self.line}
patch: |
{"\n".join(indented)}"""

        comments_md = ""
        for comment in self.comments:
            comments_md += "\n---\n\n"
            comments_md += f"{comment.body}\n\n"
            comments_md += f"~@{comment.author}\n"

        return frontmatter + comments_md
