import importlib.metadata
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from prfs.git import get_current_branch, get_repo_info
from prfs.github import GitHubClient
from prfs.github_cli import find_pr_for_branch

console = Console()


def get_version() -> str:
    return importlib.metadata.version("prfs")


app = typer.Typer(no_args_is_help=True)


@app.command()
def fetch(
    pr: Annotated[int, typer.Option("--pr", help="PR number to fetch")] | None = None,
    repo: Annotated[str, typer.Option("--repo", help="Path to repository")] = ".",
    verbose: Annotated[
        bool, typer.Option("-v", "--verbose", help="Verbose output")
    ] = False,
) -> None:
    """Fetch PR review comments and save them as local files."""
    GitHubClient.validate_gh()
    repo_path = Path(repo).resolve()

    if not (repo_path / ".git").exists():
        console.print("[red]Error: Not a git repository[/red]")
        raise typer.Exit(1)

    if pr is None:
        branch = get_current_branch(cwd=str(repo_path))
        owner, repo_name = get_repo_info(cwd=str(repo_path))
        pr_number = find_pr_for_branch(owner, repo_name, branch, cwd=str(repo_path))
        if pr_number is None:
            console.print(f"[red]Error: No PR found for branch: {branch}[/red]")
            raise typer.Exit(1)
    else:
        pr_number = pr

    client = GitHubClient(*get_repo_info(cwd=str(repo_path)))
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Fetching PR #{pr_number}...", total=None)
        threads = client.fetch_pr_review_comments(pr_number)

    prfs_dir = repo_path / ".prfs" / str(pr_number)
    prfs_dir.mkdir(parents=True, exist_ok=True)

    for thread in threads:
        thread_file = prfs_dir / f"{thread.id}.md"
        content = thread.render_to_markdown()
        thread_file.write_text(content)
        if verbose:
            console.print(
                f"[green]Written:[/green] {thread_file.relative_to(repo_path)}"
            )

    console.print(
        f"[bold green]Success:[/bold green] Fetched {len(threads)}"
        f" threads for PR #{pr_number}"
    )


@app.command()
def clean(
    pr: Annotated[int | None, typer.Option("--pr", help="PR number to clean")] = None,
    repo: Annotated[str, typer.Option("--repo", help="Path to repository")] = ".",
) -> None:
    """Remove local PR files."""
    GitHubClient.validate_gh()
    repo_path = Path(repo).resolve()

    if pr is None:
        branch = get_current_branch(cwd=str(repo_path))
        owner, repo_name = get_repo_info(cwd=str(repo_path))
        pr_number = find_pr_for_branch(owner, repo_name, branch, cwd=str(repo_path))
        if pr_number is None:
            console.print(f"[red]Error: No PR found for branch: {branch}[/red]")
            raise typer.Exit(1)
    else:
        pr_number = pr

    client = GitHubClient(*get_repo_info(cwd=str(repo_path)))
    if client.clean_pr(pr_number, cwd=str(repo_path)):
        console.print(f"[bold green]Success:[/bold green] Cleaned PR #{pr_number}")
    else:
        console.print(f"[yellow]Warning:[/yellow] No files found for PR #{pr_number}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
