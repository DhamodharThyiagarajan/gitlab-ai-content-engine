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

    # ---- approved knowledge (style guides, terminology, prior docs) ----------
    def ensure_static_knowledge(self) -> int:
        """Index data/sample_docs and data/style_guides once (idempotent upserts)."""
        from ai.prompts import _DATA_DIR

        count = 0
        for folder in ("sample_docs", "style_guides", "content_templates"):
            for path in sorted((_DATA_DIR / folder).glob("*.md")):
                text = path.read_text(encoding="utf-8").strip()
                if not text:
                    continue
                self.collection.upsert(
                    ids=[hashlib.sha256(f"kb:{folder}/{path.name}".encode()).hexdigest()],
                    documents=[f"[KB: {folder}/{path.name}]\n{text}"],
                    metadatas=[{"job_id": "kb", "chunk": 0, "source": f"{folder}/{path.name}"}],
                )
                count += 1
        return count

    def retrieve_static(self, query: str, limit: int = 3) -> list[str]:
        if not query.strip():
            return []
        result = self.collection.query(query_texts=[query], n_results=limit, where={"job_id": "kb"})
        documents = result.get("documents") or [[]]
        return [str(v) for v in documents[0] if v]
