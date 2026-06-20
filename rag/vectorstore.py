# rag/vectorstore.py
from typing import List, Dict, Any, Optional

DEFAULT_RETRIEVAL_LIMIT = 5
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
)

COLLECTION_NAME = "repository_chunks"


class VectorStore:
    """
    Centralized Qdrant vector store service.
    """

    _client: Optional[QdrantClient] = None

    @classmethod
    def get_client(cls) -> QdrantClient:
        """
        Returns singleton Qdrant client.
        """

        if cls._client is None:
            try:
                cls._client = QdrantClient(
                    path="data/qdrant"
                )
            except Exception as e:
                print(f"[Warning] Qdrant client initialization error: {e}. Falling back to :memory: client.")
                cls._client = QdrantClient(":memory:")

        return cls._client

    @classmethod
    def create_collection(
        cls,
        vector_size: int
    ):
        """
        Creates collection if it doesn't exist.
        """

        client = cls.get_client()

        collections = [
            c.name
            for c in client.get_collections().collections
        ]

        if COLLECTION_NAME not in collections:

            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )

    @classmethod
    def add_documents(
        cls,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]]
    ):
        """
        Stores repository chunks.
        """

        client = cls.get_client()

        points = []

        for idx, embedding in enumerate(embeddings):

            payload = {
                "content": documents[idx],
                **metadatas[idx]
            }

            points.append(
                PointStruct(
                    id=idx,
                    vector=embedding,
                    payload=payload
                )
            )

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

    @classmethod
    def similarity_search(
        cls,
        query_embedding: List[float],
        limit: int = 5,
        query_filter: Optional[Filter] = None
    ):
        """
        Semantic retrieval.
        """

        client = cls.get_client()

        if not cls.collection_exists():
            return []

        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        ).points

        return results

    @classmethod
    def delete_collection(cls):
        """
        Deletes collection.
        """

        client = cls.get_client()

        try:

            client.delete_collection(
                collection_name=COLLECTION_NAME
            )

        except Exception:
            pass

    @classmethod
    def collection_exists(cls) -> bool:

        client = cls.get_client()

        collections = [
            c.name
            for c in client.get_collections().collections
        ]

        return COLLECTION_NAME in collections