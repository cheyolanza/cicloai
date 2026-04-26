# CicloAI Frontend - Fase 1

CicloAI es una aplicación para guiar inscripciones a competencias de ciclismo. Esta fase implementa la primera experiencia funcional del usuario con React, TypeScript, Material UI, React Router y Vite, manteniendo una arquitectura modular preparada para conectarse luego con FastAPI.

## Estructura Actual del Repositorio

El código ejecutable está empaquetado en dos proyectos:

```text
cicloai-frontend/   React + TypeScript + Vite + Material UI
cicloai-backend/    FastAPI + RAG + JWT + PostgreSQL + Alembic
docker-compose.yml  Orquesta frontend, backend y PostgreSQL
```

Para desplegar todo localmente:

```bash
docker compose up --build
```

Servicios:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

Endpoints base del backend:

- `GET /health`: estado del servicio y componentes locales.
- `POST /ingest`: carga texto en la base de conocimiento local.
- `POST /query`: consulta la base de conocimiento local.

Estos endpoints están documentados con request y response en `cicloai-backend/README.md`. No usan prefijo `/api/v1`.

## Experiencia Conversacional

La pantalla `/agent` dejó de presentarse como wizard visual y ahora funciona como un agente conversacional:

- `useAgentConversation` conserva la máquina de estados interna.
- `agentService` simula respuestas del agente con el contrato `reply`, `state` y `ui_action`.
- `agentChatService` conecta el chat libre con `POST /api/v1/agent/chat`.
- `ChatMessageList` y `ChatMessageBubble` renderizan la conversación.
- `RichMessageRenderer` convierte acciones del agente en tarjetas embebidas.
- Las opciones, formularios, pago y agradecimiento aparecen como mensajes ricos del agente.

Componentes principales:

```text
cicloai-frontend/src/features/agent/components/AgentChatPage.tsx
cicloai-frontend/src/features/agent/components/chat/
cicloai-frontend/src/features/agent/hooks/useAgentConversation.ts
cicloai-frontend/src/features/agent/services/agentService.ts
cicloai-frontend/src/features/registration/components/
cicloai-frontend/src/features/payment/components/PaymentCard.tsx
```

El usuario ya no ve pasos ni barra de progreso; el flujo se guía por conversación, opciones sugeridas y tarjetas de acción.

Opciones visibles en esta fase:

- Inscripción unitaria.
- Inscripción masiva.
- Charlar con el Agente.

La opción “Buscar mis datos” permanece en el código para retomarla más adelante, pero queda oculta visualmente durante la fase RAG.

## Alcance de esta fase

- Pantalla inicial con validación humana mediante reCAPTCHA Enterprise.
- Generación y almacenamiento de token temporal en `sessionStorage`.
- Redirección protegida a `/agent`.
- Consulta real de carrera habilitada desde FastAPI/PostgreSQL.
- Interfaz de agente conversacional sin stepper visible.
- Flujos para primera carrera, búsqueda de datos existentes e inscripción masiva.
- Paso de pago con QR estático desde `public/images/qr_payment.png`.
- Revisión backend de primera carrera con comprobante, OCR mock y validación mock de categoría.
- Confirmación Human-in-the-Loop antes de insertar en `competition_bikers`.
- Pantalla final de agradecimiento editable.

## Flujo implementado

1. El usuario entra a `/`.
2. Presiona validar y la app ejecuta reCAPTCHA Enterprise con la acción `LOGIN`.
3. La app genera un token temporal y navega a `/agent`.
4. El agente verifica el token y consulta la carrera habilitada.
5. El usuario elige tipo de inscripción.
6. Completa el formulario correspondiente.
7. Revisa monto estimado, ve el QR estático y sube comprobante.
8. El backend recibe datos + comprobante, simula OCR y valida la categoría contra reglas mock versionadas como PDF.
9. El agente muestra un resumen de revisión para confirmación humana.
10. Al confirmar, FastAPI registra al ciclista en `competition_bikers`.
11. El flujo termina con el mensaje de agradecimiento.

## Tecnologías utilizadas

- React 18
- TypeScript
- Vite
- Material UI
- React Router
- Hooks y servicios desacoplados
- Contexto preparado para integración futura sin Redux

## Estructura de carpetas frontend

```text
src/
  app/                 Configuración de App y rutas.
  components/
    common/            Componentes reutilizables de bajo acoplamiento.
    layout/            Layouts de pantalla completa y reglas de flujo visual.
  features/
    access/            reCAPTCHA Enterprise, token temporal y pantalla de acceso.
    agent/             Wizard, slides, estado del flujo y servicios del agente.
    payment/           UI y servicio mock de pago/QR.
    race/              Tipos y servicio mock de carreras habilitadas.
  services/
    http/              Cliente HTTP preparado para FastAPI.
    storage/           Adaptadores de persistencia local.
  config/              Lectura centralizada de variables de entorno.
  theme/               Tema base de Material UI.
  types/               Tipos transversales.
  utils/               Reservado para helpers puros.
```

El backend Python existente permanece bajo `cicloai-backend/src/cicloai/`.

## Requisitos previos

- Node.js `>=18.18.0`
- npm compatible con la versión de Node instalada

El entorno local actual tiene Node `v12.19.0`; para ejecutar Vite necesitas actualizar Node antes de instalar dependencias.

## Instalación

```bash
cd cicloai-frontend
npm install
```

## Variables de entorno

Copia los `.env.example` dentro de cada proyecto si deseas ajustar valores:

```bash
cd cicloai-frontend
VITE_APP_NAME=CicloAI
VITE_ENABLE_MOCKS=true
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_RECAPTCHA_ENTERPRISE_SITE_KEY=6LcYJMcsAAAAANnSzsP1VP4bJ86DKcGQzhVbZNO2

cd ../cicloai-backend
DATABASE_URL=postgresql+psycopg2://cicloai_user:cicloai_pass@postgres:5432/cicloai
JWT_SECRET_KEY=change-me-local-secret
ENABLE_CAPTCHA_MOCK=true
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.35
RAG_AUTO_INDEX=false
```

## Scripts disponibles

```bash
cd cicloai-frontend
npm run dev
npm run build
npm run preview
npm run lint
```

## Cómo correr la app

```bash
cd cicloai-frontend
npm install
npm run dev
```

Luego abre la URL que imprima Vite, normalmente `http://localhost:5173`.

Para levantar el backend existente con PostgreSQL, migraciones y seed de la carrera activa:

```bash
docker compose up --build
```

El contenedor ejecuta `alembic upgrade head`, luego `python -m cicloai.infrastructure.database.seed` y finalmente FastAPI en `http://localhost:8000`.

Para validar reCAPTCHA contra backend real, instala dependencias Python, configura credenciales y ejecuta FastAPI:

```bash
cd cicloai-backend
pip install -r requirements.txt
ENABLE_CAPTCHA_MOCK=false \
GOOGLE_RECAPTCHA_SECRET_KEY=<secret-key> \
PYTHONPATH=src uvicorn cicloai.interfaces.api.main:app --reload
```

El frontend enviará el token del widget a `POST /api/v1/security/captcha/verify`. La respuesta incluye el `access_token` Bearer que luego se usa para consultar `GET /api/v1/bike-races/active`.

## Probar carrera habilitada

1. Entra a `/`.
2. Valida con reCAPTCHA Enterprise.
3. Serás redirigido a `/agent`.
4. El frontend consultará `GET /api/v1/bike-races/active` y verás la carrera activa sembrada en PostgreSQL.

## Actualizar Base de Datos

Después de estos cambios, aplica la migración de equipos y vuelve a ejecutar el seed:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m cicloai.infrastructure.database.seed
```

El seed agrega, sin duplicar, estos equipos activos: `INDEPENDIENTE`, `Team Gladiadores`, `Team Domadores`, `Evolution`, `Bikers SCZ`, `Bikerz`, `Team Keance`.
También actualiza la carrera activa con `race_cost=60`, `currency=BOB` y carga el QR desde `cicloai-backend/assets/payment_qr_2_2026_apertura.jpeg`.

El combo del frontend consume:

```bash
GET /api/v1/bike-teams/active
```

Este endpoint requiere `Authorization: Bearer <token>` y devuelve solo equipos activos, ordenados ascendentemente y con `name` en mayúsculas.

El endpoint de carrera activa ahora incluye:

```json
{
  "cost": 60,
  "currency": "BOB",
  "qr_image": "data:image/jpeg;base64,..."
}
```

## Primera carrera: revisión y registro

La inscripción de primera carrera usa dos endpoints protegidos:

```bash
POST /api/v1/registrations/first-race/review
POST /api/v1/registrations/first-race/confirm
```

`review` recibe `multipart/form-data` con datos personales y `payment_proof`. El backend:

- valida DNI, EXT, equipo activo y carrera activa.
- simula OCR del comprobante.
- valida la categoría con reglas mock ubicadas en `cicloai-backend/assets/documents/category_rules_2026_mock.pdf`.
- devuelve un resumen y un `review_token` firmado.

`confirm` recibe ese `review_token` y recién ahí inserta en:

```text
competition_bikers
```

La migración nueva es:

```text
cicloai-backend/alembic/versions/202604240004_create_competition_bikers_table.py
```

Comandos:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m cicloai.infrastructure.database.seed
```

## Inscripción Masiva

La opción “Inscribir varios ciclistas” descarga una plantilla CSV compatible con Excel y la sube al backend protegido:

```bash
GET /api/v1/registrations/bulk/template
POST /api/v1/registrations/bulk/upload
```

Columnas requeridas:

```text
DNI, Nombre Completo, Categoria, Fecha Nacimiento
```

Por ahora el backend valida CSV con la librería estándar de Python. La lectura de `.xlsx` queda preparada para una fase posterior con OpenPyXL/Pandas. La categoría se valida mediante `CategoryRulesService`, apuntando a:

```text
cicloai-backend/assets/documents/category_rules/
```

Si la plantilla es válida, se insertan los competidores en `competition_bikers` con estado de pago `pending_bulk_payment` y el endpoint devuelve:

```json
{
  "inserted_competitors": 2,
  "unit_cost": 60,
  "currency": "BOB",
  "total_amount": 120
}
```

La tabla `bike_races` incluye `cost NUMERIC(10,2)` para el cálculo de montos masivos. Se mantiene `race_cost` por compatibilidad con fases anteriores.

## Chat RAG con OpenAI

El agente CicloAI puede responder preguntas libres únicamente sobre la convocatoria de la carrera: lugar, fecha, hora, categorías, edades, modalidad, distancia, inscripciones, costos, reglas, uniformes, premiación, seguridad, requisitos de participación y recojo de dorsales.

Documentos fuente:

```text
cicloai-backend/assets/documents/category_rules/
```

Vector store persistente:

```text
cicloai-backend/storage/vector_store/
```

Configura la API key en `.env` en la raíz del repositorio o en el entorno del contenedor:

```bash
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.35
```

Indexar documentos:

```bash
docker compose exec backend python -m cicloai.rag.index_documents
```

También puede activarse auto-indexación al iniciar:

```bash
RAG_AUTO_INDEX=true
```

Endpoint protegido:

```bash
POST /api/v1/agent/chat
```

Ejemplo:

```bash
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"¿Cuál es el costo de inscripción?"}'
```

Si el usuario pregunta algo fuera de la convocatoria, el agente responde:

```text
No tengo información sobre eso. Solo puedo responder preguntas relacionadas con la convocatoria de la carrera.
```

Si el mensaje detecta intención operativa, el backend no usa RAG y devuelve una acción de UI:

- `start_single_registration` con `SHOW_SINGLE_REGISTRATION`.
- `start_bulk_registration` con `SHOW_BULK_REGISTRATION`.

La documentación técnica del módulo vive en:

```text
cicloai-backend/src/cicloai/rag/README.md
```

## OCR con Google Vision API

El backend procesa comprobantes de pago mediante una fachada reusable `PaymentProofOcrService`. En desarrollo puede usar mock y en entornos reales usa Google Vision API:

```text
https://vision.googleapis.com/v1/images:annotate
```

Configuración requerida en `.env`:

```env
ENABLE_OCR_MOCK=false
GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/google-service-account.json
GOOGLE_CLOUD_PROJECT_ID=ciclo-ai
GOOGLE_VISION_OCR_ENDPOINT=https://vision.googleapis.com/v1/images:annotate
PAYMENT_PROOFS_STORAGE_DIR=storage/payment_proofs
```

Coloca el JSON real de la cuenta de servicio en:

```text
secrets/google-service-account.json
```

Ese archivo no debe subirse al repositorio. Docker monta `./secrets` como `/app/secrets:ro`.

Para desarrollo sin Google Vision:

```env
ENABLE_OCR_MOCK=true
```

El flujo protegido de primera carrera guarda temporalmente el comprobante en `storage/payment_proofs/`, ejecuta OCR y devuelve en la revisión:

```json
{
  "payment_status": "ocr_validated",
  "payment_provider": "google_vision",
  "payment_message": "Comprobante procesado correctamente con Google Vision OCR",
  "payment_extracted_text": "..."
}
```

Si Google Vision no encuentra texto, la revisión queda con `payment_status=ocr_rejected` y la confirmación final no permite registrar al ciclista.

Ejemplo curl:

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

Limitación actual: solo se valida si existe texto OCR. Todavía no se valida monto, banco, fecha, cuenta, QR ni coincidencia contra el costo de carrera.

## Category Detection with RAG

La categoría detectada del ciclista ahora se calcula con `CategoryDetectionService`, usando la convocatoria configurada en:

```text
cicloai-backend/assets/documents/category_rules/convocatoria.txt
```

La ruta se controla con:

```env
CATEGORY_RULES_PDF_PATH=assets/documents/category_rules/convocatoria.txt
```

Aunque la variable conserva el nombre `pdf_path` por compatibilidad, en esta fase apunta al archivo `.txt`. El servicio calcula la edad con `date_of_race` si existe, o con la fecha actual como fallback, y envía al RAG: fecha de nacimiento, edad, categoría declarada y género si está disponible.

El prompt exige que OpenAI responda solo el nombre exacto de la categoría, sin explicación. Cualquier respuesta con prefijos, texto largo, `:` o una categoría fuera de la lista permitida se convierte en:

```text
NO_DETERMINADA
```

Configuración:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.70
ENABLE_RAG_MOCK=false
CATEGORY_RULES_PDF_PATH=assets/documents/category_rules/convocatoria.txt
```

El flujo `POST /api/v1/registrations/first-race/validate` devuelve `detected_category`, y el frontend lo muestra en la misma tarjeta de revisión antes de la confirmación Human-in-the-Loop.

Tests:

```bash
cd cicloai-backend
pytest
pytest --cov=cicloai --cov-report=term-missing
```

En Docker, si la imagen no incluye `tests/`, puedes montarlos temporalmente:

```bash
docker compose run --rm -e PYTHONDONTWRITEBYTECODE=1 \
  -v "$PWD/cicloai-backend/tests:/app/tests:ro" \
  backend pytest
```

Limitaciones:

- Depende de la calidad de `convocatoria.txt`.
- Los tests mockean `CategoryRulesRagService`; no llaman a OpenAI real.
- Respuestas inválidas del modelo se normalizan a `NO_DETERMINADA`.

## Búsqueda de Ciclista Existente

La opción “Buscar mis datos” queda desactivada visualmente en esta fase para priorizar el chat RAG. El backend y componentes anteriores se conservan porque el flujo será retomado luego para revisar un ciclista previamente registrado por nombre y actualizar únicamente su equipo.

Endpoints protegidos:

```bash
GET /api/v1/bikers/search?name=<nombre>
GET /api/v1/cycling-teams/active
POST /api/v1/bikers/{biker_id}/lookup-action
```

Tablas nuevas:

```text
cycling_teams
biker_lookup_actions
```

El seed agrega equipos activos de prueba:

```text
Independiente
Team Santa Cruz
Cotoca Bike Team
MTB Bolivia
```

Restricciones del flujo:

- No inscribe automáticamente al ciclista en la carrera activa.
- No permite editar DNI, nombre, fecha de nacimiento ni categoría.
- Solo permite modificar el equipo.
- Registra la acción en `biker_lookup_actions`.
- Deja preparada la siguiente acción `CONTINUE_TO_PAYMENT_LATER`.

Probar con curl:

```bash
curl "http://localhost:8000/api/v1/bikers/search?name=Juan" \
  -H "Authorization: Bearer $TOKEN"

curl "http://localhost:8000/api/v1/cycling-teams/active" \
  -H "Authorization: Bearer $TOKEN"

curl -X POST "http://localhost:8000/api/v1/bikers/<BIKER_ID>/lookup-action" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bike_race_id": "<ACTIVE_RACE_ID>",
    "searched_name": "Juan",
    "new_team_name": "MTB Bolivia",
    "confirm_action": true
  }'
```

Desde el frontend esta opción no se muestra temporalmente. Para pruebas técnicas se pueden usar los `curl` anteriores con un Bearer Token válido.

## Probar sin carrera habilitada

1. Completa la validación reCAPTCHA Enterprise en `/`.
2. Cambia el estado de la carrera en base de datos a `deactive`.
3. Vuelve a `/agent`.
4. La app mostrará: “No hay carreras habilitadas actualmente.”

## Qué está mockeado

- `captchaService`: renderiza el widget reCAPTCHA Enterprise en cliente y canjea el token por un Bearer Token en `/api/v1/security/captcha/verify`.
- `tokenService`: genera token temporal local.
- `raceService`: consume `GET /api/v1/bike-races/active`.
- `userLookupService`: busca usuarios mock por nombre.
- `excelService`: descarga plantilla CSV y simula validación de archivo.
- `paymentService`: calcula monto y hace validación inmediata mínima en UI.
- `PaymentProofOcrService` backend: usa Google Vision OCR si `ENABLE_OCR_MOCK=false`; con `ENABLE_OCR_MOCK=true` usa fallback mock local.
- `CategoryRulesService` backend: usa reglas mock versionadas como PDF para validar categoría.
- `IntentDetectionService` backend: detecta intención de inscripción con reglas simples antes de enviar una pregunta al RAG.

## Futuras fases

- Reemplazar la verificación mock de reCAPTCHA por validación server-side real en FastAPI.
- Emitir token temporal desde FastAPI.
- Obtener carreras, precios y disponibilidad desde backend/base de datos.
- Procesar Excel real con validaciones por fila.
- Generar QR dinámico desde backend o proveedor de pagos.
- Extender `PaymentProofOcrService` para validar monto, banco, fecha, cuenta y QR.
- Ampliar el RAG con más documentos de convocatoria y evaluaciones automáticas.
- Reemplazar `CategoryRulesService` por extracción real desde PDF usando parser/RAG.
- Enviar correo de verificación.
- Agregar panel administrativo y revisión humana.

## Notas de arquitectura

Los componentes no llaman directamente a `fetch` ni conocen detalles de almacenamiento. Las páginas consumen hooks y servicios tipados, de modo que los mocks pueden reemplazarse por clientes FastAPI sin rediseñar el flujo. El wizard funciona como una pequeña máquina de estados local; si el agente LLM o backend pasan a controlar el flujo, el cambio natural es adaptar `useAgentWizard` o sustituirlo por un servicio de sesión.

## QR de pago estático

Agrega el archivo real en:

```text
public/images/qr_payment.png
```

Si el archivo no existe, la pantalla de pago muestra un placeholder claro. En fases futuras, `paymentService.getStaticQrUrl()` debe reemplazarse por una consulta al backend para obtener el QR dinámico asociado a la inscripción.

---

# 🤖 Plantilla Oficial de Documentación — Proyecto Final AI/LLM

**Programa:** AI-LLM Solution Architect  
**Curso:** 5 — Proyecto Final de Arquitectura e Integración AI/LLM  
**Documento:** Plantilla Oficial de Documentación del Proyecto

---

## 📋 Información General del Proyecto

| Campo | Valor |
|-------|-------|
| **Nombre del Proyecto** | *CicloAI* |
| **Participante(s)** | *Jose Miguel Lanza Caceres* |
| **Instructor** | *Andres Rojas* |
| **Cohorte / Edición** | *2025-2026* |
| **Fecha de Inicio** | *20/03/2026* |
| **Fecha de Entrega Final** | *DD/MM/AAAA* |
| **Versión del Documento** | *v0.1.03202026* |
| **Estado del Proyecto** | * **En Planificación** / En Desarrollo / Completado* |
| **Repositorio GitHub/GitLab** | *https://github.com/cheyolanza/cicloai* |
| **Entorno Cloud** | * AWS  |
| **Stack Tecnológico Principal** | Python, Docker, FastAPI |

---

## Tabla de Contenidos

- [1. Resumen Ejecutivo](#1-resumen-ejecutivo)
- [2. Análisis y Especificación de Requerimientos](#2-análisis-y-especificación-de-requerimientos)
- [3. Diseño de Arquitectura AI/LLM](#3-diseño-de-arquitectura-aillm)
- [4. Diseño de APIs y Conectores](#4-diseño-de-apis-y-conectores)
- [5. Seguridad, Cumplimiento y Ética](#5-seguridad-cumplimiento-y-ética)
- [6. Implementación y Configuración de Infraestructura](#6-implementación-y-configuración-de-infraestructura)
- [7. Estrategia de Pruebas y Resultados](#7-estrategia-de-pruebas-y-resultados)
- [8. Despliegue, Escalabilidad y Costos](#8-despliegue-escalabilidad-y-costos)
- [9. Observabilidad y Monitoreo](#9-observabilidad-y-monitoreo)
- [10. Resultados, Conclusiones y Trabajo Futuro](#10-resultados-conclusiones-y-trabajo-futuro)
- [11. Rúbrica de Evaluación](#11-rúbrica-de-evaluación)
- [12. Referencias y Bibliografía](#12-referencias-y-bibliografía)
- [Anexos](#anexos)

---

## 1. Resumen Ejecutivo

CicloAI es una solución basada en inteligencia artificial diseñada para automatizar el proceso de inscripción de ciclistas en competencias en Santa Cruz de la Sierra, Bolivia. Actualmente, los procesos de inscripción son manuales, propensos a errores, lentos y difíciles de auditar, especialmente cuando se manejan grandes volúmenes de participantes mediante formularios o archivos Excel. Esta situación genera inconsistencias en los datos, validaciones incorrectas y una carga operativa significativa para los organizadores.

La propuesta introduce un agente conversacional basado en modelos de lenguaje (LLM) que guía al usuario de forma estructurada desde el inicio del proceso de inscripción. El flujo inicia con una validación obligatoria de humanidad (anti-bots) y verificación de correo electrónico, asegurando que las interacciones provienen de usuarios reales. Posteriormente, el agente consulta y presenta las competencias disponibles, ofreciendo tres caminos principales: inscripción por primera vez, búsqueda de usuario existente o inscripción masiva mediante archivo Excel.

El sistema permite la recolección de datos personales, validación en tiempo real, procesamiento de archivos Excel, y análisis de comprobantes de pago mediante OCR. Además, integra un mecanismo de validación de pagos contra montos esperados y número de participantes, así como el envío automático de correos de verificación al finalizar cada flujo.

Desde el punto de vista arquitectónico, el sistema se implementa mediante una API REST desacoplada, un motor de orquestación basado en LLM que actúa como agente central del flujo, procesamiento de documentos y almacenamiento en la nube, asegurando escalabilidad, seguridad y alta disponibilidad. Asimismo, incorpora un pipeline RAG para contextualizar respuestas con reglas de negocio, categorías de competencia y validaciones específicas del dominio.

Los resultados esperados incluyen una reducción de más del 70% en tiempos operativos, una disminución superior al 80% en errores de registro, una mejora significativa en la validación de pagos y una mayor trazabilidad del proceso. El sistema está diseñado para operar en español y preparado para futuras extensiones.

---

### 1.1 Propuesta de Valor y Problema que Resuelve

El problema principal radica en la gestión manual de inscripciones a competencias deportivas, lo cual genera errores en datos, inconsistencias en equipos, validaciones incorrectas de pagos y una alta carga operativa para los organizadores. En eventos con más de 100 participantes, estos problemas pueden traducirse en retrasos, conflictos y pérdida de confianza por parte de los competidores.

Adicionalmente, los procesos actuales carecen de mecanismos robustos de validación de usuarios (anti-bots), verificación de identidad básica (correo electrónico) y control automatizado de pagos en función del número de inscritos, lo que incrementa el riesgo de fraude o inconsistencias financieras.

CicloAI propone una solución basada en inteligencia artificial que automatiza completamente este proceso mediante un agente conversacional que orquesta el flujo de inscripción. El sistema valida desde el inicio que el usuario sea humano y cuente con un correo válido, luego guía al usuario a través de diferentes caminos según su necesidad: registro nuevo, reutilización de datos existentes o inscripción masiva.

Mediante este enfoque, el sistema recolecta información, valida reglas de negocio, controla la coherencia de datos (como equipos y categorías), y procesa documentos automáticamente. La incorporación de OCR permite validar comprobantes de pago sin intervención manual inicial, mientras que el sistema también valida que el monto pagado corresponda correctamente al número de participantes registrados.

El uso de RAG garantiza respuestas contextualizadas y precisas basadas en reglas del dominio, competencias habilitadas y criterios de validación.

Esta solución es óptima frente a enfoques tradicionales porque combina automatización, validación inteligente, control de fraude y escalabilidad. Permite reducir costos operativos, mejorar la precisión de los datos, asegurar la integridad del proceso y ofrecer una experiencia de usuario moderna y guiada.

---

### 1.2 Alcance y Delimitación

| ✅ EN SCOPE | ❌ OUT OF SCOPE |
|------------|----------------|
| Validación de usuario humano (anti-bots) y verificación de email al inicio del flujo | Entrenamiento de modelos desde cero (fine-tuning) |
| Interfaz conversacional con LLM para guiar el flujo completo de inscripción | Integración con sistemas bancarios externos |
| Inscripción individual (nuevo usuario) con validación de datos y pago | Soporte multi-idioma (solo español) |
| Búsqueda de usuarios previamente registrados y reutilización de datos | Aplicaciones móviles nativas |
| Inscripción masiva mediante carga de archivos Excel | Integración con sistemas externos |
| Validación de comprobantes de pago mediante OCR | |
| Validación automática de montos de pago según número de inscritos | |
| Envío de correos de verificación al finalizar el proceso | |
| Despliegue en entorno cloud (AWS/GCP) | |
| Dashboard administrativo para aprobación/rechazo (HITL) | |

### 1.3 Indicadores Clave de Éxito (KPIs del Proyecto)

| KPI / Métrica | Línea Base | Meta Objetivo | Resultado Obtenido |
|---------------|-----------|---------------|-------------------|
| Latencia promedio (p95) | N/A | < 2 segundos | *[Completar al final]* |
| Tasa de éxito de respuestas | N/A | > 92% | *[Completar al final]* |
| Costo por 1,000 consultas (USD) | N/A | < 1 USD | *[Completar al final]* |
| Cobertura de pruebas (%) | 0% | > 80% | *[Completar al final]* |
| Precisión OCR | N/A | > 85% | *[Completar al final]* |

---
## 2. Análisis y Especificación de Requerimientos

### 2.1 Contexto del Caso de Uso Empresarial

El sistema CicloAI se enmarca en el sector de eventos deportivos, específicamente en la gestión de inscripciones para competencias de ciclismo en Santa Cruz de la Sierra, Bolivia. Actualmente, el proceso de inscripción (AS-IS) es manual, basado en formularios, correos electrónicos y archivos Excel, lo que genera errores en los datos, duplicidad de registros, inconsistencias en equipos y validaciones manuales de pagos. Este proceso es lento, poco escalable y depende fuertemente de la intervención humana.

Los actores involucrados son: ciclistas (usuarios finales), organizadores del evento y administradores del sistema. Los usuarios utilizan el sistema principalmente durante periodos de inscripción, con una frecuencia intensiva en ventanas cortas de tiempo (picos de uso). Se estima un volumen de entre 100 y 500 inscripciones por evento.

El flujo propuesto (TO-BE) automatiza el proceso mediante un agente conversacional basado en LLM que actúa como orquestador central del sistema. El flujo inicia con una validación obligatoria de humanidad (anti-bots) y verificación de correo electrónico, garantizando que solo usuarios reales puedan iniciar el proceso.

Posteriormente, el agente consulta las competencias habilitadas y guía al usuario a través de tres caminos principales:
1. Inscripción por primera vez
2. Búsqueda de usuario existente
3. Inscripción masiva mediante archivo Excel

El sistema realiza validaciones en múltiples capas:
- Validación inicial (humano + email)
- Validaciones de datos en tiempo real
- Validaciones de reglas de negocio (categorías, equipos)
- Validación de pagos (monto vs número de inscritos)

El procesamiento de comprobantes de pago se realiza mediante OCR, y el sistema verifica automáticamente la consistencia del monto pagado. Además, se envían correos de verificación como cierre del flujo, garantizando trazabilidad.

El administrador interviene únicamente en casos excepcionales o procesos de revisión, reduciendo significativamente la carga operativa.

---

### 2.2 Requerimientos Funcionales

| ID | Descripción del Requerimiento | Prioridad | Criterio de Aceptación |
|----|-------------------------------|-----------|------------------------|
| RF-001 | El sistema debe recibir consultas en lenguaje natural y retornar respuestas coherentes con el contexto empresarial. | Alta | Respuesta generada en < 3s con coherencia > 90% |
| RF-002 | El sistema debe integrar fuentes de datos estructuradas y no estructuradas como contexto (RAG). | Alta | Recuperación correcta en > 85% de consultas de prueba |
| RF-003 | El sistema debe permitir la inscripción individual guiada paso a paso mediante el agente LLM. | Alta | Flujo completo sin errores en > 95% de pruebas |
| RF-004 | El sistema debe permitir la carga y validación de archivos Excel con múltiples participantes. | Alta | Procesamiento exitoso de archivos con ≥100 registros en < 5s |
| RF-005 | El sistema debe validar que todos los participantes del Excel pertenezcan al mismo equipo. | Alta | Rechazo automático si existe inconsistencia |
| RF-006 | El sistema debe clasificar automáticamente a los participantes según categoría (edad y tipo). | Alta | Clasificación correcta en > 90% de casos |
| RF-007 | El sistema debe procesar comprobantes de pago mediante OCR. | Alta | Extracción correcta de datos en > 85% de casos |
| RF-008 | El sistema debe enviar notificaciones por correo al administrador para aprobación. | Media | Email enviado en < 10 segundos |
| RF-009 | El sistema debe proveer un dashboard para aprobación/rechazo de inscripciones. | Alta | Visualización y acción en tiempo real |
| RF-010 | El sistema debe validar que el usuario es humano antes de iniciar el flujo (CAPTCHA o mecanismo equivalente). | Alta | Validación exitosa en > 95% de intentos |
| RF-011 | El sistema debe requerir y validar un correo electrónico antes de iniciar el proceso de inscripción. | Alta | Email válido verificado antes de continuar |
| RF-012 | El sistema debe permitir la selección guiada de competencias disponibles. | Alta | Listado correcto de eventos habilitados |
| RF-013 | El sistema debe permitir la búsqueda de usuarios previamente registrados por nombre. | Alta | Recuperación correcta en > 90% |
| RF-014 | El sistema debe permitir reutilizar datos de usuarios existentes con edición limitada (equipo). | Alta | Edición restringida correctamente aplicada |
| RF-015 | El sistema debe validar que el monto del pago corresponda al número de participantes inscritos. | Alta | Validación correcta en > 95% |
| RF-016 | El sistema debe generar y mostrar un medio de pago (QR) al usuario. | Alta | QR generado correctamente en < 2s |
| RF-017 | El sistema debe enviar un correo de confirmación al finalizar el flujo de inscripción. | Alta | Email enviado correctamente en < 10s |
| RF-018 | El sistema debe validar que los participantes del Excel pertenezcan a categorías válidas. | Alta | Rechazo automático si hay inconsistencias |

---

### 2.3 Requerimientos No Funcionales

| ID | Categoría | Descripción | Métrica / Umbral |
|----|-----------|-------------|-----------------|
| RNF-001 | Rendimiento | Latencia de respuesta extremo a extremo | p95 < 2s bajo carga normal |
| RNF-002 | Escalabilidad | Capacidad de manejar picos de tráfico durante inscripciones | Auto-scaling hasta 1000 usuarios concurrentes |
| RNF-003 | Seguridad | Autenticación y autorización de usuarios | OAuth 2.0 / JWT, cifrado HTTPS |
| RNF-004 | Disponibilidad | Uptime del servicio | >= 99.5% mensual (SLA) |
| RNF-005 | Cumplimiento | Protección de datos personales | Cumplimiento de buenas prácticas (PII masking) |
| RNF-006 | Observabilidad | Monitoreo y trazabilidad del sistema | Logs estructurados + dashboards en tiempo real |
| RNF-007 | Usabilidad | Interfaz intuitiva y flujo conversacional claro | ≥ 90% satisfacción en pruebas de usuario |
| RNF-008 | Precisión AI | Calidad de respuestas del LLM | > 92% de respuestas correctas |
| RNF-009 | Procesamiento OCR | Exactitud en extracción de datos de pago | ≥ 85% precisión |
| RNF-010 | Mantenibilidad | Facilidad de evolución del sistema | Arquitectura modular desacoplada |
| RNF-011 | Portabilidad | Despliegue en entornos cloud | Compatible con AWS/GCP |
| RNF-012 | Tiempo de procesamiento batch | Procesamiento de archivos Excel | ≤ 5 segundos para 100 registros |
| RNF-013 | Seguridad | Prevención de bots mediante validación de humanidad (CAPTCHA o equivalente) | > 95% efectividad |
| RNF-014 | Integridad de pagos | Validación automática de consistencia entre monto pagado y número de inscritos | > 95% precisión |
| RNF-015 | Confiabilidad del flujo | Garantizar finalización completa del flujo con confirmación por email | > 98% éxito |

---

### 2.4 Restricciones y Supuestos

| Restricciones | Supuestos |
|--------------|-----------|
| Presupuesto cloud máximo: USD $50/mes (revisar) | Los usuarios tienen acceso a internet estable |
| No integración con sistemas bancarios en esta versión (solo validación por comprobante) | El modelo LLM está disponible vía API |
| Sistema operará únicamente en idioma español | Los usuarios proporcionan datos correctos |
| No se permite almacenamiento de datos sensibles en logs | Existencia de datos de prueba para validación |
| Dependencia de servicios externos (LLM, OCR, CAPTCHA) | Disponibilidad continua de servicios cloud |
| Validación de pagos basada en OCR, no en confirmación bancaria directa | Los comprobantes de pago son legibles y contienen información relevante |

## 3. Diseño de Arquitectura AI/LLM

### 3.1 Diagrama de Arquitectura General (Nivel C4 — Contexto y Contenedor)

> 📌 **Descripción:** El siguiente diagrama representa la arquitectura de alto nivel del sistema CicloAI bajo el modelo C4 (Contexto y Contenedores). Se incluyen los actores principales, la capa de API, el orquestador LLM, servicios de validación (CAPTCHA, reglas de negocio), procesamiento OCR, almacenamiento de datos y componentes cloud.

![Diagrama de Arquitectura CicloAI](img/cicloai-architecture.drawio.png)

**Figura 1. Diagrama de Arquitectura General — CicloAI v0.2**

---

### 3.2 Descripción de Componentes Arquitectónicos

| Componente | Tecnología / Servicio | Responsabilidad Principal | Justificación de Selección |
|------------|----------------------|--------------------------|---------------------------|
| API Gateway | FastAPI + Nginx | Exposición de endpoints, routing, rate limiting |Ligero, rápido, ideal para microservicios
| Orquestador LLM | LangChain | Manejo de prompts, RAG, chains | Ecosistema maduro, integración nativa con LLMs |
| Modelo LLM Base | GPT-4o  | Procesamiento de lenguaje, interpretación de formularios | Alta precisión, multimodal (clave para OCR + texto) |
| Vector Store |  ChromaDB  | Búsqueda semántica para RAG | Open source, fácil integración local |
| Capa de Datos | PostgreSQL | Persistencia de metadata | Escalable  estándar en backend
| Observabilidad | Prometheus + Grafana | Monitore y metricas | Open source y robusto |
| Seguridad / IAM | Okta | Autenticación y autorización | Integración enterprise |
| OCR Service | Tesseract / AWS Textract | Extraccion de text de documentos| Necesario para inscripciones, verificacion de pagos por comprobantes

### 3.3 Diagrama de Flujo de Datos e Integración

#### 3.3.1 Flujo General + Decisión Inicial
![Diagrama Flujo General CicloAI](img/3.3.1.diagrama-flujo-general.png)
*Figura 2. Flujo de Datos General + Decisión Inicial — CicloAI*


#### 3.3.2 Flujo Nuevo Usuario (Primer Carrera)
![Diagrama Flujo Nuevo Usuario - CicloAI](img/3.3.2.diagrama-flujo-nuevo-usuario.png)
*Figura 3. Flujo Nuevo Usuario (Primer Carrera) — CicloAI*

#### 3.3.3 Flujo Usuario Existente
![Diagrama Flujo Usuario Existente - CicloAI](img/3.3.3.diagrama-flujo-usuario-existente.png)
*Figura 4. Flujo Usuario Existente  — CicloAI*

#### 3.3.4 Flujo Inscripción Masiva
![Diagrama Flujo Inscripción Masiva - CicloAI](img/3.3.4.diagrama-flujo-inscripcion-masiva.png)
*Figura 5. Flujo Usuario Existente  — CicloAI*

#### 3.3.5 Flujo State Machine
![Diagrama Flujo State Machine - CicloAI](img/3.3.5.diagrama-flujo-state-machine.png)
*Figura 6. Flujo State Machine  — CicloAI*

#### 3.3.5 Arquitectura
![Diagrama Arquitectura - CicloAI](img/c4-diagram-cicloai.drawio.png)
*Figura 7. Arquitectura — CicloAI*


### 3.4 Estrategia de Diseño de Prompts y RAG

**System Prompt Base:**

*Documente el system prompt que guía el comportamiento del modelo. Incluya: rol, restricciones, formato de respuesta esperado, y manejo de casos fuera de alcance.*

```
Eres un asistente experto en gestión de inscripciones a competencias de ciclismo.

Tu función es analizar requisitos, validar documentos y asistir en el proceso de registro.

RESTRICCIONES:
- Solo responde en base al contexto proporcionado.
- Si no tienes información suficiente, responde: "No tengo información sobre eso."
- No inventes datos.
- No generes contenido fuera del dominio de ciclismo o inscripciones.

FORMATO DE RESPUESTA:
{
  "status": "ok | error",
  "analysis": "...",
  "required_documents": [],
  "recommendations": []
} 
```

## 3.4 Arquitectura física (equivalencias por nube)

| Capa | AWS | GCP | Azure |
|---|---|---|---|
| Ingesta | Lambda / API Gateway | Cloud Functions / Cloud Run | Azure Functions |
| Raw (Bronze) | S3 (raw docs) | GCS | ADLS Gen2 |
| Transform | Glue / Lambda | Dataflow | Synapse / Databricks |
| Curated (Silver) | S3 (cleaned JSON / text) | GCS | ADLS |
| Serving (Gold) | RDS / Aurora + pgvector | BigQuery | Synapse SQL |
| Vector Layer | OpenSearch / pgvector / Pinecone | Vertex AI Vector Search | Azure AI Search |
| Orquestación | Step Functions | Workflows | ADF |
| Observabilidad | CloudWatch + X-Ray | Cloud Monitoring | Azure Monitor |

---

## Estrategia de Recuperación (RAG)

### Tipo de chunking
Hybrid chunking (semántico + tamaño fijo)

**Justificación:**
Permite preservar contexto semántico en documentos no estructurados (formularios, reglas de competencia) mientras mantiene control sobre el tamaño de entrada al modelo.

---

### Tamaño de chunks
500 tokens

**Justificación:**
Balance adecuado entre contexto suficiente y precisión en la recuperación.

---

### Overlap
100 tokens

**Justificación:**
Evita pérdida de contexto entre segmentos consecutivos.

---

### Modelo de embeddings
text-embedding-3-small (OpenAI)

**Alternativa:**
all-MiniLM-L6-v2 (open source)

**Justificación:**
Buen balance entre costo, rendimiento y facilidad de integración.

---

### Función de similitud
Cosine similarity

**Justificación:**
Estándar en NLP, eficiente y compatible con embeddings normalizados.

---

### Top-K
5

**Justificación:**
Reduce ruido manteniendo suficiente contexto relevante.

---

### Threshold
0.75

**Justificación:**
Filtra resultados de baja relevancia, mejorando la precisión del sistema.

---

### Re-ranking
Sí — Cross-encoder re-ranking

**Implementación:**
- Modelo sugerido: bge-reranker-base
- Flujo:
  1. Recuperación inicial top-10
  2. Re-ranking
  3. Selección final top-3

**Beneficios:**
- Mejora precisión
- Reduce alucinaciones
- Mejora relevancia del contexto enviado al LLM

---

### Pipeline RAG completo

1. Usuario envía query
2. Se genera embedding del query
3. Se consulta vector store
4. Se recuperan documentos (top-k)
5. Se aplica re-ranking
6. Se construye prompt:
   - system prompt
   - contexto relevante
   - query del usuario
7. Se envía al LLM
8. Se genera respuesta final

---

### Resumen ejecutivo

Se implementa un enfoque RAG híbrido con chunking semántico y tamaño fijo (500 tokens, overlap 100). Se utiliza el modelo de embeddings text-embedding-3-small con similitud coseno. Se recuperan los top-5 documentos relevantes con un threshold de 0.75.

Se incorpora una capa de re-ranking mediante cross-encoder, donde inicialmente se recuperan 10 documentos y se seleccionan los 3 más relevantes antes de enviar el contexto al LLM.

Este enfoque mejora la precisión, reduce alucinaciones y permite actualización dinámica de la base de conocimiento sin necesidad de fine-tuning.---


## 4. Diseño de APIs y Conectores

### 4.1 Especificación de Endpoints (API REST)

*Los endpoints quedan alineados al flujo definido en la sección 3.3: validación inicial obligatoria, apertura de sesión conversacional, selección de competencia y ramificación hacia inscripción nueva, usuario existente o carga masiva.*

| Endpoint | Método | Etapa del flujo | Descripción | Request / Params | Response |
|----------|--------|-----------------|-------------|------------------|----------|
| `/api/v1/health` | GET | Operación | Health check del sistema | N/A | `{"status": "healthy\|degraded", "components": object}` |
| `/api/v1/security/human-verifications` | POST | Preflujo | Valida CAPTCHA o mecanismo anti-bots | `{ "captcha_token": string }` | `{ "verification_id": string, "valid": boolean }` |
| `/api/v1/security/email-verifications` | POST | Preflujo | Valida formato y envía/verifica correo | `{ "email": string }` | `{ "verification_id": string, "valid": boolean }` |
| `/api/v1/sessions` | POST | Inicio | Crea sesión conversacional solo si humanidad y email están validados | `{ "email": string, "human_verification_id": string, "email_verification_id": string }` | `{ "session_id": string, "state": "AWAITING_EVENT" }` |
| `/api/v1/events` | GET | Selección de carrera | Lista competencias habilitadas | `status=open` | `[{ "event_id": string, "name": string, "price": number }]` |
| `/api/v1/sessions/{session_id}/event` | PATCH | Selección de carrera | Asocia la carrera elegida a la sesión | `{ "event_id": string }` | `{ "session_id": string, "state": "AWAITING_REGISTRATION_TYPE" }` |
| `/api/v1/sessions/{session_id}/registration-type` | PATCH | Decisión inicial | Define el camino del usuario | `{ "type": "new_user\|existing_user\|massive" }` | `{ "session_id": string, "state": string, "next_action": string }` |
| `/api/v1/sessions/{session_id}/messages` | POST | Orquestación | Avanza el diálogo guiado por el agente LLM | `{ "message": string, "context": object }` | `{ "reply": string, "state": string, "next_action": string, "data": object }` |
| `/api/v1/users` | GET | Usuario existente | Busca usuarios previamente registrados | `name`, `email?` | `{ "results": [object] }` |
| `/api/v1/inscriptions` | POST | Inscripción | Crea la inscripción vinculada a sesión, evento y tipo de flujo | `{ "session_id": string, "event_id": string, "type": "new_user\|existing_user\|massive" }` | `{ "inscription_id": string, "status": "draft" }` |
| `/api/v1/inscriptions/{inscription_id}/participants` | POST | Inscripción individual | Registra participante nuevo o reutiliza usuario existente | `{ "source": "manual\|existing_user", "user_id": string?, "participant_data": object }` | `{ "participant_id": string, "validation_status": string }` |
| `/api/v1/inscriptions/{inscription_id}/participants/{participant_id}` | PATCH | Usuario existente | Permite edición limitada de datos permitidos, por ejemplo equipo | `{ "team": string }` | `{ "participant_id": string, "validation_status": string }` |
| `/api/v1/inscriptions/{inscription_id}/bulk-files` | POST | Inscripción masiva | Carga Excel de participantes | `multipart/form-data (file)` | `{ "file_id": string, "rows_received": int }` |
| `/api/v1/inscriptions/{inscription_id}/bulk-validation` | POST | Inscripción masiva | Valida Excel, equipo único y categorías | `{ "file_id": string }` | `{ "valid": boolean, "rows_processed": int, "errors": [object] }` |
| `/api/v1/inscriptions/{inscription_id}/validation` | POST | Reglas de negocio | Ejecuta validaciones de datos, categoría, equipo y monto esperado | N/A | `{ "valid": boolean, "expected_amount": number, "participants": int, "errors": [object] }` |
| `/api/v1/inscriptions/{inscription_id}/payment-qr` | POST | Pago | Genera QR según monto esperado y número de participantes | N/A | `{ "qr_code": string, "amount": number, "expires_at": string }` |
| `/api/v1/inscriptions/{inscription_id}/payment-receipts` | POST | Pago | Carga comprobante de pago | `multipart/form-data (image)` | `{ "receipt_id": string, "status": "uploaded" }` |
| `/api/v1/inscriptions/{inscription_id}/payment-analysis` | POST | OCR | Extrae monto, fecha e identificador de transacción | `{ "receipt_id": string }` | `{ "amount": number?, "transaction_date": string?, "transaction_id": string?, "confidence_notes": [string] }` |
| `/api/v1/inscriptions/{inscription_id}/payment-validation` | POST | Pago | Compara monto OCR contra monto esperado | `{ "receipt_id": string }` | `{ "valid": boolean, "expected_amount": number, "detected_amount": number? }` |
| `/api/v1/inscriptions/{inscription_id}/submit` | POST | Cierre | Ejecuta decisión final con reglas, RAG/LLM y criterio HITL | N/A | `{ "status": "approved\|review\|rejected", "reason": string? }` |
| `/api/v1/inscriptions/{inscription_id}` | GET | Consulta | Obtiene estado de la inscripción | N/A | `{ "status": string, "details": object }` |

---

### 4.2 Endpoints Administrativos y de Sistema

| Endpoint | Método | Descripción | Request / Params | Response |
|----------|--------|-------------|------------------|----------|
| `/api/v1/auth/login` | POST | Autenticación de administradores u operadores | `{ "email": string, "password": string }` | `{ "access_token": string, "expires_in": int }` |
| `/api/v1/admin/review-queue` | GET | Lista inscripciones escaladas a revisión humana | `status=review` | `[{ "inscription_id": string, "reason": string }]` |
| `/api/v1/admin/inscriptions/{inscription_id}/approval` | POST | Aprueba manualmente una inscripción | `{ "admin_id": string, "notes": string? }` | `{ "status": "approved" }` |
| `/api/v1/admin/inscriptions/{inscription_id}/rejection` | POST | Rechaza manualmente una inscripción | `{ "admin_id": string, "reason": string }` | `{ "status": "rejected" }` |
| `/api/v1/inscriptions/{inscription_id}/confirmation-email` | POST | Envía correo de confirmación al cierre del flujo | N/A | `{ "status": "sent" }` |

---

## 4.3 Autenticación y Autorización

| Campo | Descripción |
|-------|-------------|
| **Mecanismo Auth** | JWT Bearer Token con OAuth 2.0 para dashboard administrativo y endpoints internos |
| **Proveedor de Identidad** | Okta |
| **Gestión de Secrets** | AWS Secrets Manager |
| **Rate Limiting** | 100 req/min por sesión, 1000 req/min global |
| **Roles definidos** | `user`, `admin`, `system` |

---

## 4.4 Modelo de Roles (RBAC)

| Rol | Permisos |
|-----|---------|
| **user** | Validarse, iniciar sesión de inscripción, seleccionar carrera, registrar participantes, subir comprobantes y consultar estado |
| **admin** | Revisar cola HITL, aprobar/rechazar inscripciones y consultar pagos |
| **system** | Orquestación LLM, OCR, validaciones, cálculo de montos y envío de notificaciones |

---

## 4.5 Flujo General End-to-End

1. Usuario accede al sistema.
2. Valida humanidad con `POST /api/v1/security/human-verifications`.
3. Valida correo con `POST /api/v1/security/email-verifications`.
4. Inicia sesión con `POST /api/v1/sessions`.
5. Consulta carreras con `GET /api/v1/events`.
6. Selecciona carrera con `PATCH /api/v1/sessions/{session_id}/event`.
7. Elige camino con `PATCH /api/v1/sessions/{session_id}/registration-type`.
8. El agente guía el flujo con `POST /api/v1/sessions/{session_id}/messages`.
9. Se crea inscripción con `POST /api/v1/inscriptions`.
10. Se registran participantes por formulario, usuario existente o Excel.
11. Se valida la inscripción con `POST /api/v1/inscriptions/{inscription_id}/validation`.
12. Se genera QR con `POST /api/v1/inscriptions/{inscription_id}/payment-qr`.
13. Se carga comprobante con `POST /api/v1/inscriptions/{inscription_id}/payment-receipts`.
14. OCR analiza el comprobante con `POST /api/v1/inscriptions/{inscription_id}/payment-analysis`.
15. Se valida el pago con `POST /api/v1/inscriptions/{inscription_id}/payment-validation`.
16. Se cierra el flujo con `POST /api/v1/inscriptions/{inscription_id}/submit`.
17. Si queda en revisión, el administrador usa `/api/v1/admin/...`.
18. Se envía confirmación con `POST /api/v1/inscriptions/{inscription_id}/confirmation-email`.

---

## 4.6 Flujos Específicos

### Flujo Nuevo Usuario

1. Preflujo: humanidad, email, sesión y carrera.
2. Selección `new_user` en `/sessions/{session_id}/registration-type`.
3. Creación de inscripción en estado `draft`.
4. Registro manual en `/inscriptions/{inscription_id}/participants`.
5. Validación de categoría, datos y monto esperado.
6. QR, comprobante, OCR, validación de pago y cierre.

### Flujo Usuario Existente

1. Preflujo: humanidad, email, sesión y carrera.
2. Selección `existing_user` en `/sessions/{session_id}/registration-type`.
3. Búsqueda con `GET /api/v1/users`.
4. Reutilización del usuario en `/inscriptions/{inscription_id}/participants`.
5. Edición limitada, como equipo, con `PATCH /inscriptions/{inscription_id}/participants/{participant_id}`.
6. Validación, pago y cierre.

### Flujo Masivo (Excel)

1. Preflujo: humanidad, email, sesión y carrera.
2. Selección `massive` en `/sessions/{session_id}/registration-type`.
3. Carga Excel en `/inscriptions/{inscription_id}/bulk-files`.
4. Validación masiva en `/inscriptions/{inscription_id}/bulk-validation`.
5. Validación de monto total según participantes aceptados.
6. QR, comprobante, OCR, validación de pago y cierre.

---

## 4.7 Consideraciones de Diseño

- Versionado: `/api/v1/`.
- La sesión (`session_id`) gobierna el estado conversacional.
- La inscripción (`inscription_id`) gobierna participantes, documentos, pagos y cierre.
- Los endpoints de pago cuelgan de la inscripción para evitar validar montos sin contexto.
- El agente LLM no reemplaza las validaciones determinísticas; las orquesta y explica.
- La arquitectura queda preparada para procesos async en OCR, validación masiva y notificaciones.
- Formato estándar de entrada y salida: JSON, excepto cargas `multipart/form-data`.

### Manejo de errores

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Descripción del error",
    "details": {}
  }
}
```

---

## 6. Implementación Inicial Funcional

La primera versión ejecutable implementa un MVP RAG end-to-end con arquitectura limpia en `src/` y tres endpoints base:

| Endpoint | Método | Uso |
|----------|--------|-----|
| `/health` | GET | Verifica estado de API, documentos e índice vectorial |
| `/ingest` | POST | Ingresa texto a la base de conocimiento y lo indexa |
| `/query` | POST | Ejecuta recuperación semántica local y genera respuesta fundamentada |

### Estructura de Código

| Carpeta | Responsabilidad |
|---------|-----------------|
| `cicloai-backend/src/cicloai/domain` | Entidades y puertos de dominio |
| `cicloai-backend/src/cicloai/application` | Casos de uso: ingesta, consulta, health y chunking |
| `cicloai-backend/src/cicloai/infrastructure` | Persistencia JSON, vector store local y cliente LLM extractivo |
| `cicloai-backend/src/cicloai/interfaces/api` | API FastAPI y schemas HTTP |
| `cicloai-backend/tests` | Pruebas unitarias y de integración ligera |
| `cicloai-backend/scripts` | Evaluación RAG/LLM y prueba de carga |
| `reports` | Reportes generados por evaluación y carga |

### Ejecución Local

```bash
cd cicloai-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src uvicorn cicloai.interfaces.api.main:app --reload
```

### Prueba Manual del RAG

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"text":"CicloAI valida pagos con OCR y compara el monto contra el numero de participantes.","metadata":{"source":"demo"}}'

curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Como valida pagos CicloAI?","top_k":3}'
```

### Docker

```bash
docker compose up --build
curl http://127.0.0.1:8000/health
```

La imagen usa Dockerfile multi-stage, usuario no-root y healthcheck interno. `docker-compose.yml` monta un volumen para persistir la base local en `/app/data`.

### Pruebas y Reportes

```bash
cd cicloai-backend
pytest
python scripts/evaluate_llm.py
python scripts/load_test.py --base-url http://127.0.0.1:8000 --requests 50 --concurrency 5
```

El reporte de evaluación LLM/RAG mide:

- `term_recall`: cobertura de términos esperados en la respuesta.
- `context_precision_at_1`: si el primer contexto recuperado corresponde a la fuente esperada.
- `groundedness`: proporción de términos de la respuesta presentes en los contextos recuperados.
- `latency_ms`: latencia del pipeline RAG.

### CI/CD GitHub

El workflow `.github/workflows/ci-cd.yml` ejecuta:

1. Instalación de dependencias.
2. Pruebas unitarias.
3. Evaluación RAG y publicación del reporte como artifact.
4. Build Docker.
5. Push opcional a Amazon ECR en `main`.

Para activar el push a AWS se deben configurar estos secrets en GitHub:

- Variable de repositorio `ENABLE_AWS_DEPLOY=true`
- `AWS_ROLE_TO_ASSUME`
- `AWS_REGION`
- `ECR_REPOSITORY`

Este pipeline deja listo el artefacto containerizado para desplegar luego en ECS Fargate, App Runner o EKS.
