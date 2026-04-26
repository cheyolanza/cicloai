# CicloAI RAG

Este módulo permite que CicloAI responda preguntas sobre la convocatoria de la carrera usando documentos internos y OpenAI.

## Alcance

El agente solo debe responder sobre convocatoria, lugar, fecha, hora, categorías, edades, modalidad, distancia, inscripciones, costos, reglas, uniformes, premiación, seguridad, requisitos y recojo de dorsales.

Si la pregunta está fuera del dominio responde:

```text
No tengo información sobre eso. Solo puedo responder preguntas relacionadas con la convocatoria de la carrera.
```

Si la información no está en el contexto responde:

```text
No tengo información sobre eso.
```

## Arquitectura

- `document_loader.py`: lee `.txt`, `.md` y `.pdf` desde `assets/documents/category_rules/`.
- `text_splitter.py`: divide documentos en chunks de 800 caracteres con overlap de 150 para conservar contexto entre cortes.
- `vector_store.py`: persiste embeddings en ChromaDB dentro de `storage/vector_store/`.
- `retriever.py`: recupera chunks relevantes con `top_k` y threshold.
- `prompt_builder.py`: construye el prompt restringido contra alucinación.
- `rag_service.py`: orquesta recuperación, prompt y llamada a OpenAI.
- `index_documents.py`: comando de indexación.

## Variables

```env
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.35
RAG_DOCUMENTS_DIR=assets/documents/category_rules
RAG_VECTOR_STORE_DIR=storage/vector_store
RAG_AUTO_INDEX=false
```

La API key va en `.env`; nunca debe hardcodearse.

## Documentos

Coloca la convocatoria limpia en:

```text
assets/documents/category_rules/
```

El archivo inicial esperado es:

```text
mtb_2026.txt
```

## Indexación

Opción recomendada con Docker Compose, desde la raíz del repositorio:

```bash
docker compose up -d --build
docker compose exec backend python -m cicloai.rag.index_documents
```

Si ejecutas el comando en tu máquina local, primero debes instalar las dependencias del backend. El error `ModuleNotFoundError: No module named 'pypdf'` significa que tu entorno local no tiene instalado `pypdf` desde `requirements.txt`.

```bash
cd cicloai-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m cicloai.rag.index_documents
```

Dentro de un contenedor o entorno backend ya preparado:

```bash
python -m cicloai.rag.index_documents
```

Si no existe índice, el endpoint responderá:

```json
{
  "detail": "La base de conocimiento no está indexada. Ejecute python -m cicloai.rag.index_documents"
}
```

## Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"¿Cuál es el costo de inscripción?"}'
```

## Limitaciones

- La detección de intención operativa es por reglas.
- El RAG depende de documentos previamente indexados.
- Las respuestas se restringen al contexto recuperado; no usa memoria conversacional persistente.

## Próximas mejoras

- Reindexación incremental.
- Métricas de recuperación.
- Evaluaciones automáticas de groundedness.
- Soporte de múltiples convocatorias activas.
