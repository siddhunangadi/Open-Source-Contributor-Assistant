# rag/retriever.py

from huggingface_hub.inference._generated.types import zero_shot_image_classification
from typing import List, Dict, Any

from sentence_transformers import SentenceTransformer

from rag.vectorstore import VectorStore


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class RepositoryRetriever:

    def __init__(self):
        self.embedding_model = (
            SentenceTransformer(
                EMBEDDING_MODEL
            )
        )
        self.vectorstore = VectorStore()

    def create_query_embedding(
        self,
        query: str
    ) -> List[float]:
        """
        Convert query into embedding.
        """

        return (
            self.embedding_model
            .encode(query)
            .tolist()
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant repository chunks.
        """

        query_embedding = (
            self.create_query_embedding(
                query
            )
        )

        results = (
            self.vectorstore.similarity_search(
                query_embedding=query_embedding,
                limit=top_k
            )
        )

        chunks = []

        for result in results:

            chunks.append(
                {
                    "score": result.score,
                    "content": result.payload.get(
                        "content",
                        ""
                    ),
                    "file_path": result.payload.get(
                        "file_path",
                        ""
                    ),
                    "file_name": result.payload.get(
                        "file_name",
                        ""
                    ),
                    "chunk_type": result.payload.get(
                        "chunk_type",
                        ""
                    )
                }
            )

        return chunks

    def retrieve_by_file(
        self,
        query: str,
        file_name: str,
        top_k: int = 5
    ):
        """
        Retrieve chunks from a specific file.
        """

        from qdrant_client.models import (
            Filter,
            FieldCondition,
            MatchValue
        )

        query_embedding = (
            self.create_query_embedding(
                query
            )
        )

        file_filter = Filter(
            must=[
                FieldCondition(
                    key="file_name",
                    match=MatchValue(
                        value=file_name
                    )
                )
            ]
        )

        return self.vectorstore.similarity_search(
            query_embedding=query_embedding,
            limit=top_k,
            query_filter=file_filter
        )

    def retrieve_related_files(
        self,
        query: str,
        top_k: int = 10
    ) -> List[str]:
        """
        Retrieve unique relevant files.
        """

        chunks = self.retrieve(
            query=query,
            top_k=top_k
        )

        files = {
            chunk["file_path"]
            for chunk in chunks
        }

        return sorted(
            list(files)
        )