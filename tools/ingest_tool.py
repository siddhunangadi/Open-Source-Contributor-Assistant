# tools/ingest_tool.py

import os
from pathlib import Path
from rag.ingest import RepositoryIngestor
from rag.vectorstore import VectorStore


def ingest_repository(
    repo_url: str,
    full_name: str,
    html_url: str,
) -> dict:
    """
    Clone a GitHub repository and index all its code files into Qdrant.
    Must be called BEFORE any retrieve_* tools — otherwise retrieval returns nothing.

    Args:
        repo_url: Git clone URL, e.g. https://github.com/org/repo.git
        full_name: GitHub repository name, e.g. org/repo
        html_url: GitHub repository page, e.g. https://github.com/org/repo

    Returns:
        dict with keys: status, repo_path, files_indexed, chunks_stored
    """

    repo_name = full_name.replace("/", "_")
    repo_path = str(Path("data/repos") / repo_name)

    # ── If already indexed, skip cloning + embedding ──────────────────────────
    try:
        if VectorStore.collection_exists():
            client = VectorStore.get_client()
            count  = client.count("repository_chunks").count
            if count > 0:
                return {
                    "status":         "already_indexed",
                    "repo_path":       repo_path,
                    "files_indexed":  "unknown",
                    "chunks_stored":   count,
                }
    except Exception:
        # Fallback if Qdrant is locked/unusable, but the repo is already cloned locally
        if Path(repo_path).exists():
            ingestor = RepositoryIngestor()
            files = ingestor.get_code_files(repo_path)
            return {
                "status":         "cloned_only",
                "repo_path":       repo_path,
                "files_indexed":  len(files),
                "chunks_stored":   "unknown",
            }

    status = "indexed"
    try:
        VectorStore.delete_collection()
    except Exception:
        pass

    ingestor  = RepositoryIngestor()
    clone_url = html_url.rstrip("/") + ".git"

    # Clone
    actual_path = ingestor.clone_repository(clone_url, repo_name)

    # Get file count before indexing
    files = ingestor.get_code_files(actual_path)

    # Index into Qdrant
    try:
        ingestor.ingest_repository(actual_path)
    except Exception:
        status = "cloned_only"

    # Count chunks stored
    try:
        chunks_stored = VectorStore.get_client().count("repository_chunks").count
    except Exception:
        chunks_stored = "unknown"

    return {
        "status":        status,
        "repo_path":      actual_path,
        "files_indexed":  len(files),
        "chunks_stored":  chunks_stored,
    }