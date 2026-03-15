# prfs

Pull Request File System. PR review comments as local files. Browse, filter, and script against GitHub PR review threads using familiar Unix tools.

## Installation

```bash
uv tool install prfs
```

## How it works

`prfs fetch` pulls comments from a GitHub PR to `{repo}/.prfs/{pr_number}/{thread_id}.md`. One markdown file per thread with YAML frontmatter containing the file path and git patch.

## Quick start

```bash
gh auth login # gh is used under the hood
prfs fetch
```

## Features

- One file per review thread
- Works offline after initial fetch
- Natively integrates with `rg`, `vim`, etc.

## Format

Each thread file contains:
- `file`: path and line number (`src/utils.js:42`). This format is supported by Vim jumps with `gF`.
- `patch`: the git diff where the comment thread was attached to.
- Comments in markdown separated with `---`.

Example comment file (`.prfs/123/456.md`):

```markdown
---
file: src/utils.js:42
patch: |
  diff --git a/src/utils.js b/src/utils.js
  --- a/src/utils.js
  +++ b/src/utils.js
  @@ -40,7 +40,7 @@ function getUser() {
    const db = connect();
  -  return db.query('users');
  +  return await db.query('users');
  }
---

@alice:

The return type should be `Promise<User>` not `User`.

---

@bob:

Good catch. I'll fix it.
```
