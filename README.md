# 🤖 Sistema RAG Avanzado - Banco Caja Social

Sistema de Retrieval-Augmented Generation (RAG) implementado con n8n y Azure para el Banco Caja Social.

## 📋 Descripción

Este proyecto implementa un **sistema RAG avanzado** con capacidades multimodales que permite:
- ✅ **Ingesta de documentos**: Procesar PDFs, DOCX, imágenes y otros formatos
- ✅ **Consultas multimodales**: Texto + documentos temporales + imágenes en una misma consulta
- ✅ **Gestión de documentos**: Actualizar y eliminar documentos del índice
- ✅ **Búsqueda semántica**: Utilizar embeddings y búsqueda vectorial
- ✅ **Respuestas contextuales**: Generar respuestas con GPT-4 basadas en contexto relevante
- ⭐ **Sistema de feedback**: Validación y mejora automática de respuestas
- 📊 **Métricas avanzadas**: Captura automática de calidad, costos y tiempos

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         n8n Workflows                         │
├─────────────────────────────────────────────────────────────┤
│  Ingesta │ Consultas │ Actualización │ Eliminación          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Azure Services                          │
├─────────────────────────────────────────────────────────────┤
│  • Azure OpenAI (embeddings + GPT-4)                         │
│  • Azure AI Search (vector store)                            │
│  • Azure Blob Storage (documentos)                           │
│  • Azure Cosmos DB (metadata)                                │
│  • Azure Document Intelligence (OCR)                         │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

> 💡 **Ver estructura completa**: [`ESTRUCTURA.md`](ESTRUCTURA.md) - Mapa detallado del proyecto

```
RAG Agent/
├── 📄 README.md                      # Este archivo (documentación principal)
├── 📄 ESTRUCTURA.md                  # Mapa detallado del proyecto
│
├── 📂 docs/                          # 📚 Documentación completa
│   ├── README.md                     # Índice de documentación
│   ├── INICIO_RAPIDO.md              # ⚡ Guía de inicio rápido
│   ├── RESUMEN_SISTEMA_COMPLETO.md   # 📊 LEER PRIMERO - Overview completo
│   ├── ARQUITECTURA_RAG.md           # 🏗️ Arquitectura técnica detallada
│   ├── CHECKLIST_IMPLEMENTACION.md   # ✅ Pasos de implementación
│   ├── EJEMPLOS_USO.md               # 💻 Ejemplos de código
│   ├── RESUMEN_EJECUTIVO.md          # 📊 Presentación para stakeholders
│   ├── RAG_CON_DOCUMENTOS_TEMPORALES.md  # ⭐ RAG con docs temporales
│   ├── COMPARACION_FLUJOS_RAG.md     # 🔍 Comparativa de flujos
│   ├── FLUJO_DETALLADO_CON_RAG.md    # ⭐⭐⭐ Flujo detallado NODO 4
│   └── RAG_AVANZADO_CON_FEEDBACK.md  # 🎯 Sistema avanzado con feedback
│
├── 📂 scripts/                       # 🐍 Scripts Python
│   ├── README.md                     # Guía de scripts
│   ├── n8n_manager.py                # Cliente para gestionar n8n
│   ├── setup_rag_workflows.py        # Crear workflows automáticamente
│   ├── test_connection.py            # Pruebas del sistema
│   ├── rag_advanced_client.py        # ⭐ Cliente RAG avanzado multimodal
│   └── test_rag_with_document.py     # Pruebas con documentos temporales
│
├── 📂 config/                        # ⚙️ Configuración
│   ├── README.md                     # Guía de configuración
│   ├── requirements.txt              # Dependencias Python
│   └── config_template.env           # Template de variables de entorno
│
└── 📂 workflows/                     # 🔄 Workflows exportados de n8n
    └── README.md                     # Guía de workflows
```

## 🚀 Inicio Rápido

### 1. Configurar Servicios Azure

Consulta [`docs/CHECKLIST_IMPLEMENTACION.md`](docs/CHECKLIST_IMPLEMENTACION.md) para la configuración completa de:
- Azure OpenAI
- Azure AI Search
- Azure Blob Storage
- Azure Cosmos DB

### 2. Instalar Dependencias

```bash
pip install -r config/requirements.txt
```

### 3. Configurar Variables de Entorno

Copia `config/config_template.env` y actualiza con tus credenciales:

```bash
cp config/config_template.env .env
# Editar .env con tus credenciales de Azure
```

### 4. Crear Workflows en n8n

Ejecuta el script de configuración:

```bash
python3 scripts/setup_rag_workflows.py
```

Esto creará automáticamente 3 workflows en tu servidor n8n:
1. **RAG - Ingesta Completa de Documentos**
2. **RAG - Sistema de Consultas Completo**
3. **RAG - Eliminar Documento**

### 5. Probar el Sistema

#### Ingestar un documento:

```bash
curl -X POST http://159.203.149.247:5678/webhook/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "manual.pdf",
    "file_base64": "BASE64_DEL_ARCHIVO",
    "department": "productos",
    "document_type": "manual"
  }'
```

#### Hacer una consulta:

```bash
curl -X POST http://159.203.149.247:5678/webhook/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué productos financieros ofrece el banco?"
  }'
```

## 📚 Documentación Detallada

### 🌟 Documentos Principales
- **[RESUMEN_SISTEMA_COMPLETO.md](docs/RESUMEN_SISTEMA_COMPLETO.md)**: 📊 **LEER PRIMERO** - Resumen ejecutivo de todo el sistema
- **[INICIO_RAPIDO.md](docs/INICIO_RAPIDO.md)**: ⚡ Guía rápida para comenzar
- **[ARQUITECTURA_RAG.md](docs/ARQUITECTURA_RAG.md)**: 🏗️ Arquitectura completa, componentes de Azure, flujos de trabajo
- **[CHECKLIST_IMPLEMENTACION.md](docs/CHECKLIST_IMPLEMENTACION.md)**: ✅ Guía paso a paso para implementar el sistema
- **[EJEMPLOS_USO.md](docs/EJEMPLOS_USO.md)**: 💻 Ejemplos de código en Python, JavaScript, cURL, React
- **[RESUMEN_EJECUTIVO.md](docs/RESUMEN_EJECUTIVO.md)**: 📊 Presentación ejecutiva con ROI y casos de uso

### ⭐ Sistema RAG Avanzado (Nuevos)
- **[FLUJO_DETALLADO_CON_RAG.md](docs/FLUJO_DETALLADO_CON_RAG.md)**: ⭐⭐⭐ **ESENCIAL** - Dónde y cómo se consulta el RAG
- **[RAG_AVANZADO_CON_FEEDBACK.md](docs/RAG_AVANZADO_CON_FEEDBACK.md)**: 🎯 Sistema completo con multimodalidad y feedback
- **[RAG_CON_DOCUMENTOS_TEMPORALES.md](docs/RAG_CON_DOCUMENTOS_TEMPORALES.md)**: 📄 Consultas con documentos sin indexar
- **[COMPARACION_FLUJOS_RAG.md](docs/COMPARACION_FLUJOS_RAG.md)**: 🔍 Comparativa entre flujos tradicionales y avanzados

## 🔧 Gestión de Workflows

### Ver workflows actuales

```python
from scripts.n8n_manager import N8nManager

manager = N8nManager(
    base_url="http://159.203.149.247:5678",
    api_key="TU_API_KEY"
)

# Listar workflows
workflows = manager.list_workflows()
for wf in workflows:
    print(f"{wf['name']} - {'Activo' if wf['active'] else 'Inactivo'}")

# Ejecutar workflow
manager.execute_workflow("workflow_id", {"data": "test"})

# Exportar workflow a carpeta workflows/
manager.export_workflow("workflow_id", "workflows/mi_workflow.json")
```

## 🎯 Casos de Uso

### 1. 💬 Chat Corporativo Inteligente
Integra el RAG en un chatbot para que los empleados consulten políticas, manuales y procedimientos.

### 2. 📞 Atención al Cliente Avanzada
Proporciona a los agentes respuestas rápidas basadas en la base de conocimientos.

### 3. 🔍 Análisis de Documentos Temporales
Analiza contratos, facturas o propuestas sin indexarlas permanentemente.
- **Ejemplo**: "¿Este contrato cumple con nuestras políticas?" + adjuntar PDF

### 4. 📝 Refinamiento con Plantillas
Mejora documentos usando plantillas y ejemplos del RAG.
- **Ejemplo**: "Ayúdame a refinar esta historia de usuario" + adjuntar documento

### 5. 🖼️ Análisis Multimodal
Procesa imágenes, documentos escaneados y PDFs con tablas.
- **Ejemplo**: Verificar facturas con imágenes + datos del RAG

### 6. 🤖 Automatización con Feedback
Sistema que aprende y mejora automáticamente según feedback del usuario.

## 💰 Costos Estimados (Azure)

| Servicio | Tier | Costo Mensual |
|----------|------|---------------|
| Azure OpenAI | Pay-as-you-go | $50-200 |
| Azure AI Search | Standard S1 | $250 |
| Blob Storage | Standard LRS | $5-20 |
| Cosmos DB | Serverless | $10-50 |
| Document Intelligence | S0 | $25 |
| **Total** | | **$340-545/mes** |

## 🔐 Seguridad

- ✅ API Keys protegidas mediante credenciales de n8n
- ✅ Datos almacenados en Azure con encriptación
- ✅ Acceso controlado mediante Azure RBAC
- ⚠️ **Importante**: Implementar autenticación en webhooks para producción

## 🤝 Contribuciones

Este proyecto es interno del Banco Caja Social. Para contribuir:
1. Crea una rama con tu feature
2. Prueba exhaustivamente
3. Solicita revisión del equipo técnico
4. Merge después de aprobación

## 📞 Soporte

- **Equipo de Desarrollo**: [equipo-desarrollo@banco.com](mailto:equipo-desarrollo@banco.com)
- **Documentación Azure**: https://learn.microsoft.com/azure/
- **Comunidad n8n**: https://community.n8n.io

## 📝 Notas de Versión

### v2.0.0 (2025-10-23) ⭐ ACTUAL
- ✅ **Sistema RAG Avanzado** con multimodalidad
- ✅ **Consultas con documentos temporales** (sin indexación permanente)
- ✅ **Soporte de imágenes** con GPT-4 Vision
- ✅ **Sistema de feedback** automático
- ✅ **Métricas avanzadas** (calidad, costos, tiempos)
- ✅ **Complementación automática** de respuestas valiosas
- ✅ **Cliente Python avanzado** (`rag_advanced_client.py`)
- ✅ **Documentación completa** del flujo detallado

### v1.0.0 (2025-10-21)
- ✅ Arquitectura inicial implementada
- ✅ Workflows básicos de ingesta, consulta y eliminación
- ✅ Integración con Azure OpenAI y AI Search
- ✅ Scripts de gestión y ejemplos de uso

## 📄 Licencia

Este proyecto es propiedad del Banco Caja Social. Todos los derechos reservados.
