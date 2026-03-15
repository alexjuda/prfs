import subprocess


def get_current_branch(cwd: str | None = None) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result.stdout.strip()


def get_repo_info(cwd: str | None = None) -> tuple[str, str]:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    url = result.stdout.strip()
    if url.startswith("git@github.com:"):
        path = url.replace("git@github.com:", "").replace(".git", "")
    elif url.startswith("https://github.com/"):
        path = url.replace("https://github.com/", "").replace(".git", "")
    else:
        raise ValueError(f"Unknown git remote format: {url}")

    parts = path.split("/")
    return parts[0], parts[1]
