# 🤖 Sistema RAG - Banco Caja Social

Sistema de Retrieval-Augmented Generation (RAG) implementado con n8n y Azure para el Banco Caja Social.

## 📋 Descripción

Este proyecto implementa un sistema RAG completo que permite:
- ✅ **Ingesta de documentos**: Procesar PDFs, DOCX, y otros formatos
- ✅ **Consultas inteligentes**: Responder preguntas basadas en documentos corporativos
- ✅ **Gestión de documentos**: Actualizar y eliminar documentos del índice
- ✅ **Búsqueda semántica**: Utilizar embeddings y búsqueda vectorial
- ✅ **Respuestas contextuales**: Generar respuestas con GPT-4 basadas en contexto relevante

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
│   ├── ARQUITECTURA_RAG.md           # 🏗️ Arquitectura técnica detallada
│   ├── CHECKLIST_IMPLEMENTACION.md   # ✅ Pasos de implementación
│   ├── EJEMPLOS_USO.md               # 💻 Ejemplos de código
│   └── RESUMEN_EJECUTIVO.md          # 📊 Presentación para stakeholders
│
├── 📂 scripts/                       # 🐍 Scripts Python
│   ├── README.md                     # Guía de scripts
│   ├── n8n_manager.py                # Cliente para gestionar n8n
│   ├── setup_rag_workflows.py        # Crear workflows automáticamente
│   └── test_connection.py            # Pruebas del sistema
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

- **[INICIO_RAPIDO.md](docs/INICIO_RAPIDO.md)**: ⚡ Guía rápida para comenzar
- **[ARQUITECTURA_RAG.md](docs/ARQUITECTURA_RAG.md)**: 🏗️ Arquitectura completa, componentes de Azure, flujos de trabajo
- **[CHECKLIST_IMPLEMENTACION.md](docs/CHECKLIST_IMPLEMENTACION.md)**: ✅ Guía paso a paso para implementar el sistema
- **[EJEMPLOS_USO.md](docs/EJEMPLOS_USO.md)**: 💻 Ejemplos de código en Python, JavaScript, cURL, React
- **[RESUMEN_EJECUTIVO.md](docs/RESUMEN_EJECUTIVO.md)**: 📊 Presentación ejecutiva con ROI y casos de uso

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

### 1. Chat Corporativo
Integra el RAG en un chatbot para que los empleados consulten políticas, manuales y procedimientos.

### 2. Atención al Cliente
Proporciona a los agentes respuestas rápidas basadas en la base de conocimientos.

### 3. Búsqueda Inteligente
Permite a los usuarios buscar en documentos corporativos usando lenguaje natural.

### 4. Automatización de Respuestas
Responde automáticamente a preguntas frecuentes basándose en documentación oficial.

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

### v1.0.0 (2025-10-21)
- ✅ Arquitectura inicial implementada
- ✅ Workflows básicos de ingesta, consulta y eliminación
- ✅ Integración con Azure OpenAI y AI Search
- ✅ Scripts de gestión y ejemplos de uso
- 🔄 Pendiente: Implementar autenticación y rate limiting

## 📄 Licencia

Este proyecto es propiedad del Banco Caja Social. Todos los derechos reservados.
