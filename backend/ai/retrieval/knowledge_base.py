from __future__ import annotations

import hashlib
import re
from pathlib import Path

from app.config import settings


class _HashEmbedding:
    """Small deterministic local embeddings; avoids remote embedding services."""

    def _encode(self, text: str) -> list[float]:
        import math

        vector = [0.0] * 256
        for token in re.findall(r"[\w./:-]+", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % len(vector)
            vector[index] += 1.0 if digest[2] & 1 else -1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def __call__(self, input: list[str] | str) -> list[list[float]] | list[float]:
        if isinstance(input, str):
            return self._encode(input)
        return [self._encode(str(text)) for text in input]

    def embed_query(self, input: str | list[str]) -> list[float] | list[list[float]]:
        if isinstance(input, list):
            return [self._encode(str(text)) for text in input]
        return self._encode(str(input))

    def embed_documents(self, input: list[str]) -> list[list[float]]:
        return [self._encode(str(text)) for text in input]

    @staticmethod
    def name() -> str:
        return "local-hash-v1"


class KnowledgeBase:
    """Persistent Chroma store scoped by job to prevent cross-job retrieval."""

    def __init__(self) -> None:
        import chromadb

        persist_dir = Path(settings.chroma_persist_directory)
        persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection,
            embedding_function=_HashEmbedding(),
            metadata={"hnsw:space": "cosine"},
        )

    def add_source(self, job_id: int | str, source: str) -> None:
        chunks = [part.strip() for part in re.split(r"\n\s*\n", source) if part.strip()]
        if not chunks:
            return
        ids = [
            hashlib.sha256(f"{job_id}:{i}:{chunk}".encode("utf-8")).hexdigest()
            for i, chunk in enumerate(chunks)
        ]
        self.collection.upsert(
            ids=ids,
            documents=chunks,
            metadatas=[{"job_id": str(job_id), "chunk": i} for i in range(len(chunks))],
        )

    def retrieve(self, job_id: int | str, query: str, limit: int = 6) -> list[str]:
        if not query.strip() or self.collection.count() == 0:
            return []
        result = self.collection.query(
            query_texts=[query],
            n_results=min(limit, self.collection.count()),
            where={"job_id": str(job_id)},
        )
        documents = result.get("documents") or [[]]
        return [str(value) for value in documents[0] if value]
