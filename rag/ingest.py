# rag/ingest.py
import shutil
from pathlib import Path
from typing import List
from uuid import uuid4

from git import Repo
from sentence_transformers import SentenceTransformer

from rag.vectorstore import VectorStore


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class RepositoryIngestor:

    def __init__(self):

        self.embedding_model = (
            SentenceTransformer(
                EMBEDDING_MODEL
            )
        )

    def clone_repository(
        self,
        repo_url: str,
        repo_name: str
    ) -> str:
        """
        Clone repository locally.
        """

        repo_path = (
            Path("data/repos")
            / repo_name
        )

        if repo_path.exists():
            return str(repo_path)

        Repo.clone_from(
            repo_url,
            repo_path
        )

        return str(repo_path)

    def get_code_files(
        self,
        repo_path: str
    ) -> List[Path]:
        """
        Collect source files. Python files are returned first
        so embeddings prioritise implementation code.
        """

        repo = Path(repo_path)

        ignored_dirs = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            "node_modules",
            "dist",
            "build",
        }

        # .py and .pyi are highest priority — they contain the real implementation
        source_extensions = {".py", ".pyi"}
        # Secondary: config/docs indexed for context but de-prioritised
        secondary_extensions = {".toml", ".yaml", ".yml", ".json", ".md"}
        allowed_extensions = source_extensions | secondary_extensions

        source_files = []
        other_files = []

        for file in repo.rglob("*"):

            if not file.is_file():
                continue

            if any(
                ignored in file.parts
                for ignored in ignored_dirs
            ):
                continue

            if file.suffix.lower() not in allowed_extensions:
                continue

            if file.suffix.lower() in source_extensions:
                source_files.append(file)
            else:
                other_files.append(file)

        # Python source files first so chunking + embedding covers them first
        return source_files + other_files

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000
    ) -> List[str]:
        """
        Basic chunking strategy.
        """

        chunks = []

        for i in range(
            0,
            len(text),
            chunk_size
        ):
            chunks.append(
                text[i:i + chunk_size]
            )

        return chunks

    def ingest_repository(
        self,
        repo_path: str
    ):
        """
        Read files and push chunks to Qdrant.
        """

        files = self.get_code_files(
            repo_path
        )

        documents = []
        metadatas = []
        ids = []

        for file in files:

            try:

                content = file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                chunks = self.chunk_text(
                    content
                )

                for chunk in chunks:

                    documents.append(
                        chunk
                    )

                    metadatas.append(
                        {
                            "file_path": str(file),
                            "file_name": file.name,
                            "chunk_type": "code",
                            "is_source": file.suffix.lower() in {".py", ".pyi"},
                            "is_test": any(
                                part in str(file).lower()
                                for part in ("test", "tests", "spec")
                            ),
                        }
                    )

                    ids.append(
                        str(uuid4())
                    )

            except Exception:
                continue

        embeddings = (
            self.embedding_model.encode(
                documents
            ).tolist()
        )

        if not embeddings:
            return

        VectorStore.create_collection(
            vector_size=len(
                embeddings[0]
            )
        )

        VectorStore.add_documents(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def delete_local_repo(
        self,
        repo_path: str
    ):
        """
        Remove cloned repository.
        """

        try:
            shutil.rmtree(
                repo_path
            )
        except Exception:
            pass