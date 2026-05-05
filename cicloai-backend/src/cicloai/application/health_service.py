from __future__ import annotations

from cicloai.domain.ports import DocumentRepository, VectorIndex


class HealthService:
    def __init__(
        self, repository: DocumentRepository, vector_index: VectorIndex
    ) -> None:
        self.repository = repository
        self.vector_index = vector_index

    def check(self) -> dict:
        documents = self.repository.list()
        chunks = self.vector_index.count()
        status = "healthy" if chunks >= 0 else "degraded"
        return {
            "status": status,
            "components": {
                "documents": {"status": "healthy", "count": len(documents)},
                "vector_index": {"status": "healthy", "chunks": chunks},
            },
        }
