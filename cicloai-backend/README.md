# CicloAI Backend

Backend FastAPI para CicloAI. Incluye seguridad con Bearer Token, PostgreSQL, migraciones Alembic, flujos de inscripción y el módulo conversacional RAG con OpenAI.

## Endpoints Operativos Base

Estos endpoints viven en la raíz del backend, no bajo `/api/v1`. Sirven para health check y para el RAG local histórico basado en ingest/query.

### `GET /health`

Verifica que el backend y sus componentes básicos estén disponibles.

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy",
  "components": {
    "documents": {
      "status": "healthy",
      "count": 1
    },
    "vector_index": {
      "status": "healthy",
      "chunks": 1
    }
  }
}
```

### `POST /ingest`

Inserta texto en la base de conocimiento local. Es útil para pruebas técnicas del motor RAG extractivo.

Request:

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Documento de prueba CicloAI",
    "metadata": {
      "source": "smoke-test"
    },
    "document_id": "smoke-test"
  }'
```

Response:

```json
{
  "document_id": "smoke-test",
  "chunks_indexed": 1,
  "metadata": {
    "source": "smoke-test"
  }
}
```

Errores comunes:

```json
{
  "detail": "El texto no puede estar vacío."
}
```

### `POST /query`

Consulta la base de conocimiento local cargada por `/ingest`.

Request:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Documento de prueba",
    "top_k": 1
  }'
```

Response:

```json
{
  "answer": "Segun la base de conocimiento de CicloAI: cicloai valida inscripciones archivos excel categorias y pagos con ocr para carreras de ciclismo",
  "sources": [
    {
      "document_id": "doc_1447ab338174d9e0",
      "chunk_id": "chk_964f3efba3285072",
      "score": 0.239,
      "text": "cicloai valida inscripciones archivos excel categorias y pagos con ocr para carreras de ciclismo",
      "metadata": {
        "source": "load-test",
        "chunk_index": "0"
      }
    }
  ],
  "model": "local-extractive-rag",
  "latency_ms": 27.65
}
```

Errores comunes:

```json
{
  "detail": "No hay documentos indexados para consultar."
}
```

## RAG Conversacional

El endpoint protegido `POST /api/v1/agent/chat` responde preguntas sobre la convocatoria de la carrera usando documentos locales, embeddings de OpenAI y ChromaDB como vector store persistente.

Variables principales:

```env
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.35
RAG_AUTO_INDEX=false
```

Los documentos fuente se colocan en:

```text
assets/documents/category_rules/
```

Indexar documentos:

```bash
docker compose exec backend python -m cicloai.rag.index_documents
```

Probar chat:

```bash
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"¿Cuál es el costo de inscripción?"}'
```

El agente solo responde sobre la convocatoria. Para temas fuera de dominio devuelve:

```text
No tengo información sobre eso. Solo puedo responder preguntas relacionadas con la convocatoria de la carrera.
```

La documentación detallada del módulo está en:

```text
src/cicloai/rag/README.md
```

## OCR con Google Vision API

El servicio `PaymentProofOcrService` analiza comprobantes de pago sin mezclar seguridad ni reglas de negocio. El endpoint ya está protegido con Bearer Token; OCR no recibe ni valida `recaptcha_token`.

Variables:

```env
ENABLE_OCR_MOCK=false
GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/google-service-account.json
GOOGLE_CLOUD_PROJECT_ID=ciclo-ai
GOOGLE_VISION_OCR_ENDPOINT=https://vision.googleapis.com/v1/images:annotate
PAYMENT_PROOFS_STORAGE_DIR=assets/payments
```

Credenciales:

```text
secrets/google-service-account.json
```

Docker monta `./secrets` en `/app/secrets:ro`. El JSON real no debe subirse al repositorio.

Para usar mock local:

```env
ENABLE_OCR_MOCK=true
```

Endpoint integrado:

```bash
curl -X POST http://localhost:8000/api/v1/registrations/first-race/validate \
  -H "Authorization: Bearer $TOKEN" \
  -F "dni=1234567" \
  -F "dni_extension=SC" \
  -F "full_name=Juan Perez" \
  -F "email=juan@example.com" \
  -F "birth_date=1986-05-10" \
  -F "requested_category=AFICIONADO" \
  -F "bike_team_name=INDEPENDIENTE" \
  -F "payment_proof=@/path/to/payment-proof.png"
```

Errores controlados:

- Credenciales faltantes: `Google OCR no está configurado correctamente. Verifique GOOGLE_APPLICATION_CREDENTIALS.`
- Formato no soportado: `Formato de archivo no soportado para OCR.`
- Error Vision API: `No se pudo procesar el comprobante con Google Vision OCR.`

Los comprobantes subidos se guardan en:

```text
assets/payments/
```

La validación de pago ya extrae y controla:

- `monto`: debe coincidir exactamente con el costo de la carrera activa.
- `id_transaction`: no puede existir previamente en `race_qr_payments`.
- `fecha`: debe ser una fecha válida y corresponder al día actual.
- `bank_name`: debe poder identificarse desde el texto OCR.

Si una validación falla, la inscripción no se inserta todavía. El agente mantiene los datos capturados y permite subir otro comprobante.

Tabla creada:

```text
race_qr_payments
```

Campos principales: carrera, ciclista asociado opcional, monto esperado, monto detectado, moneda, id de transacción, fecha, banco, ruta del comprobante, proveedor OCR, texto OCR, estado y motivo de rechazo.

Ejecutar migración:

```bash
docker compose exec backend alembic upgrade head
```

El contenedor backend también ejecuta automáticamente al iniciar:

```bash
alembic upgrade head
python -m cicloai.infrastructure.database.seed
```

Esto aplica cambios de esquema en cada despliegue Docker/Cloud Run antes de iniciar FastAPI. Puede desactivarse solo para casos especiales con:

```env
RUN_DB_MIGRATIONS=false
RUN_DB_SEED=false
```

## Category Detection with RAG

La detección de categoría usa `CategoryDetectionService` y `CategoryRulesRagService` sobre:

```text
assets/documents/category_rules/convocatoria.txt
```

Variable:

```env
CATEGORY_RULES_PDF_PATH=assets/documents/category_rules/convocatoria.txt
ENABLE_RAG_MOCK=false
OPENAI_MODEL=gpt-4o-mini
```

El RAG debe responder únicamente el nombre de la categoría. La capa de aplicación valida la respuesta contra categorías permitidas; si hay explicación, prefijo, texto largo o categoría desconocida, devuelve `NO_DETERMINADA`.

Pruebas:

```bash
pytest
pytest --cov=cicloai --cov-report=term-missing
```
