# tools/retrieval_tools.py

from typing import Dict, List

from rag.retriever import RepositoryRetriever


retriever = RepositoryRetriever()


def retrieve_code_chunks(
    query: str,
    top_k: int = 5,
    **kwargs
) -> List[Dict]:
    """
    Retrieve relevant code chunks.
    """

    return retriever.retrieve(
        query=query,
        top_k=top_k
    )


def retrieve_related_files(
    query: str,
    top_k: int = 10,
    **kwargs
) -> List[str]:
    """
    Retrieve relevant files.
    """

    return retriever.retrieve_related_files(
        query=query,
        top_k=top_k
    )


def retrieve_file_context(
    repo_path: str,
    file_path: str,
    query: str | None = None,
    top_k: int = 5,
    **kwargs
) -> dict:
    """
    Retrieve code context for one known file.
    """
    from pathlib import Path
    clean_path = str(file_path).replace("\\", "/")
    
    # Try semantic search if query is provided and Qdrant is unlocked
    chunks = []
    if query:
        file_name = Path(clean_path).name
        try:
            results = retriever.retrieve_by_file(
                query=query,
                file_name=file_name,
                top_k=top_k
            )
            for result in results:
                payload = getattr(result, "payload", {}) or {}
                chunks.append({
                    "content": payload.get("content", ""),
                    "score": getattr(result, "score", 0.8),
                    "file_path": clean_path
                })
        except Exception:
            pass

    # Fallback/Supplemental: read the actual file content from local disk
    local_path = Path(repo_path) / clean_path
    file_content = ""
    if local_path.exists():
        try:
            file_content = local_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass

    return {
        "file_path": clean_path,
        "repo_path": repo_path,
        "query": query,
        "content": file_content,
        "semantic_chunks": chunks
    }


def retrieve_issue_context(
    issue_title: str,
    issue_body: str,
    top_k: int = 8,
    **kwargs
):
    """
    Retrieve repository context relevant to an issue.
    """

    query = f"""
    {issue_title}

    {issue_body}
    """

    return retriever.retrieve(
        query=query,
        top_k=top_k
    )


def retrieve_architecture_context(
    repo_path: str,
    repository_description: str | None = None,
    top_k: int = 10,
    **kwargs
) -> dict:
    """
    Build a high-level architecture summary from a local repository.
    """
    from pathlib import Path
    
    rep_path = Path(repo_path)
    architecture_files = []
    summary_lines = []
    
    # Identify key configuration / doc files
    target_names = ["readme.md", "pyproject.toml", "requirements.txt", "setup.py", "package.json"]
    if rep_path.exists() and rep_path.is_dir():
        for item in rep_path.iterdir():
            if item.is_file() and item.name.lower() in target_names:
                architecture_files.append(item.name)
        
        # Read README.md if it exists to build a summary
        readme_path = rep_path / "README.md"
        if not readme_path.exists():
            readme_path = rep_path / "readme.md"
        
        if readme_path.exists():
            try:
                content = readme_path.read_text(encoding="utf-8", errors="ignore")
                lines = [line.strip() for line in content.splitlines() if line.strip()]
                summary_lines.extend(lines[:10])
            except Exception:
                pass
                
    summary = "\n".join(summary_lines)
    if not summary and repository_description:
        summary = repository_description
        
    return {
        "repo_path": repo_path,
        "repository_description": repository_description or "",
        "architecture_files": architecture_files,
        "summary": summary or "No high-level architectural summary found."
    }