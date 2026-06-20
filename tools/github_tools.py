from services.github import GitHubService
from models.schemas import Repository, Issue


def search_repositories(query: str, limit: int = 10, **kwargs):
    """
    Search GitHub repositories and return structured results.
    Extra kwargs (e.g. language) are silently absorbed — the LLM may pass them.
    If a language kwarg is provided, it is appended to the query string instead.
    """

    language = kwargs.get("language")
    if language and isinstance(language, str):
        query = f"{query} language:{language}"

    result = GitHubService.search_repositories(
        query=query,
        per_page=limit
    )

    repositories = []

    for repo in result.get("items", []):

        repositories.append(
            Repository(
                name=repo["name"],
                full_name=repo["full_name"],
                description=repo.get("description") or "",
                stars=repo["stargazers_count"],
                language=repo.get("language") or "Unknown",
                html_url=repo["html_url"]
            )
        )

    return repositories


def get_repository(
    owner: str,
    repo: str,
    **kwargs
):
    """
    Fetch repository details.
    """

    return GitHubService.get_repository(
        owner,
        repo
    )


def get_issues(
    owner: str,
    repo: str,
    limit: int = 20,
    **kwargs
):
    """
    Get repository issues.
    """

    issues = GitHubService.get_issues(
        owner,
        repo,
        per_page=limit
    )

    structured_issues = []

    for issue in issues:

        # Skip pull requests
        if "pull_request" in issue:
            continue

        structured_issues.append(
            Issue(
                number=issue["number"],
                title=issue["title"],
                body=issue.get("body") or "",
                url=issue["html_url"],
                labels=issue.get("labels", [])
            )
        )

    return structured_issues


def get_issue(
    owner: str,
    repo: str,
    issue_number: int,
    **kwargs
):
    """
    Fetch a single GitHub issue.
    """

    issue = GitHubService.get_issue(
        owner,
        repo,
        issue_number
    )

    return Issue(
        number=issue["number"],
        title=issue["title"],
        body=issue.get("body") or "",
        url=issue["html_url"],
        labels=issue.get("labels", [])
    )


def get_readme(
    owner: str,
    repo: str,
    **kwargs
):
    """
    Retrieve repository README.
    """

    return GitHubService.get_readme(
        owner,
        repo
    )


def get_file_contents(
    owner: str,
    repo: str,
    path: str,
    **kwargs
):
    """
    Retrieve file content from repository.
    """

    return GitHubService.get_file_contents(
        owner,
        repo,
        path
    )


def get_repository_tree(
    owner: str,
    repo: str,
    branch: str = "main",
    **kwargs
):
    """
    Return the full recursive file tree of a repository.

    Use this as a FALLBACK when ingest_repository fails.
    It lists all real source files without cloning the repo.

    Args:
        owner:  GitHub repo owner.
        repo:   Repository name.
        branch: Target branch (default 'main'; falls back to 'master').

    Returns:
        dict with keys: ref, truncated, files (list of paths), total_files
    """

    return GitHubService.get_repository_tree(owner, repo, branch)


def search_code(
    owner: str,
    repo: str,
    query: str,
    **kwargs
):
    """
    Search for exact class/function/identifier names inside a repository.

    Use this when RAG retrieval returns generic results and you need to
    locate the exact file that defines or uses a specific identifier
    (e.g. JSONAdapter, TypeAdapter, JsonValue).

    Args:
        owner: GitHub owner.
        repo:  Repository name.
        query: Identifier or code fragment to search for.

    Returns:
        List of dicts with keys: path, html_url, repository
    """

    return GitHubService.search_code(owner, repo, query)