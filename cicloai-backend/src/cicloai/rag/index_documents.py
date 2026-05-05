from __future__ import annotations

from cicloai.infrastructure.config import get_settings
from cicloai.rag.config import build_rag_config
from cicloai.rag.document_loader import DocumentLoader
from cicloai.rag.text_splitter import TextSplitter
from cicloai.rag.vector_store import VectorStore


def main() -> None:
    config = build_rag_config(get_settings())
    if not config.openai_api_key:
        raise SystemExit(
            "OPENAI_API_KEY no está configurada. Agrega la variable en .env y vuelve a ejecutar la indexación."
        )

    documents = DocumentLoader(config.documents_dir).load()
    chunks = TextSplitter(config.chunk_size, config.chunk_overlap).split(documents)
    VectorStore(config).rebuild(chunks)
    print(
        f"Indexed {len(chunks)} chunks from {len(documents)} documents into {config.vector_store_dir}"
    )


if __name__ == "__main__":
    main()
