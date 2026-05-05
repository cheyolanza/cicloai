from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import warnings

from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError


@dataclass(frozen=True)
class LoadedDocument:
    text: str
    metadata: dict[str, str]


class DocumentLoader:
    """Loads convocatoria documents from txt, md and pdf files."""

    def __init__(self, documents_dir: Path) -> None:
        self._documents_dir = documents_dir

    def load(self) -> list[LoadedDocument]:
        if not self._documents_dir.exists():
            return []

        documents: list[LoadedDocument] = []
        for path in sorted(self._documents_dir.iterdir()):
            if path.suffix.lower() in {".txt", ".md"}:
                documents.append(
                    LoadedDocument(
                        text=path.read_text(encoding="utf-8"),
                        metadata={
                            "source_file": path.name,
                            "document_type": path.suffix.lower().lstrip("."),
                        },
                    )
                )
            elif path.suffix.lower() == ".pdf":
                try:
                    reader = PdfReader(str(path))
                except (PdfReadError, PdfStreamError, OSError) as exc:
                    warnings.warn(
                        f"El documento PDF '{path.name}' no pudo leerse y será omitido durante la indexación: {exc}",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                    continue
                for index, page in enumerate(reader.pages, start=1):
                    text = page.extract_text() or ""
                    if text.strip():
                        documents.append(
                            LoadedDocument(
                                text=text,
                                metadata={
                                    "source_file": path.name,
                                    "document_type": "pdf",
                                    "page": str(index),
                                },
                            )
                        )

        return documents
