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

La propuesta introduce un agente conversacional basado en modelos de lenguaje (LLM) capaz de guiar al usuario paso a paso durante la inscripción, validar datos en tiempo real, procesar archivos Excel y analizar comprobantes de pago mediante OCR. Esto permite automatizar completamente el flujo de inscripción, reducir significativamente la intervención manual y mejorar la experiencia del usuario.

Desde el punto de vista arquitectónico, el sistema se implementa mediante una API REST desacoplada, un motor de orquestación LLM, procesamiento de documentos y almacenamiento en la nube, asegurando escalabilidad, seguridad y alta disponibilidad. Además, incorpora un pipeline RAG para contextualizar respuestas con reglas de negocio y normativa de competencias.

Los resultados esperados incluyen una reducción de más del 70% en tiempos operativos, una disminución superior al 80% en errores de registro y una mejora sustancial en la trazabilidad del proceso. El sistema está diseñado para operar en español y preparado para futuras extensiones.

---

### 1.1 Propuesta de Valor y Problema que Resuelve

El problema principal radica en la gestión manual de inscripciones a competencias deportivas, lo cual genera errores en datos, inconsistencias en equipos, validaciones incorrectas de pagos y una alta carga operativa para los organizadores. En eventos con más de 100 participantes, estos problemas pueden traducirse en retrasos, conflictos y pérdida de confianza por parte de los competidores.

CicloAI propone una solución basada en inteligencia artificial que automatiza completamente este proceso. Mediante un agente conversacional, el sistema interactúa de forma natural con los usuarios, recolecta información, valida reglas de negocio y procesa documentos automáticamente. La incorporación de OCR permite validar comprobantes de pago sin intervención manual inicial, mientras que el uso de RAG garantiza respuestas contextualizadas y precisas basadas en reglas del dominio.

Esta solución es óptima frente a enfoques tradicionales porque combina automatización, inteligencia contextual y escalabilidad. Permite reducir costos operativos, mejorar la precisión de los datos y ofrecer una experiencia de usuario moderna y eficiente.

---

### 1.2 Alcance y Delimitación

| ✅ EN SCOPE | ❌ OUT OF SCOPE |
|------------|----------------|
| Interfaz conversacional con LLM para registro de usuarios | Entrenamiento de modelos desde cero (fine-tuning) |
| Procesamiento y validación de archivos Excel | Integración con sistemas bancarios externos |
| Validación de comprobantes de pago mediante OCR | Soporte multi-idioma (solo español) |
| Despliegue en entorno cloud (AWS/GCP) | Aplicaciones móviles nativas |
| Dashboard administrativo para aprobación/rechazo | Integración con sistemas externos |

---

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

El flujo propuesto (TO-BE) automatiza el proceso mediante un agente conversacional basado en LLM, que guía al usuario, valida datos en tiempo real, procesa archivos Excel y verifica comprobantes de pago mediante OCR. El sistema centraliza la información, aplica reglas de negocio automáticamente y reduce la carga operativa del administrador, quien solo interviene en la aprobación final.

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

---

### 2.4 Restricciones y Supuestos

| Restricciones | Supuestos |
|--------------|-----------|
| Presupuesto cloud máximo: USD $50/mes(revisar) | Los usuarios tienen acceso a internet estable |
| No integración con sistemas bancarios en esta versión | El modelo LLM está disponible vía API |
| Sistema operará únicamente en idioma español | Los usuarios proporcionan datos correctos |
| No se permite almacenamiento de datos sensibles en logs | Existencia de datos de prueba para validación |
| Dependencia de servicios externos (LLM, OCR) | Disponibilidad continua de servicios cloud |

---