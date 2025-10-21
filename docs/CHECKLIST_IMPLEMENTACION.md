# ✅ Checklist de Implementación - Sistema RAG con n8n y Azure

## Fase 1: Provisionar Servicios Azure ☁️

### 1.1 Azure OpenAI Service
- [ ] Crear recurso de Azure OpenAI
- [ ] Solicitar acceso (si no lo tienes) en https://aka.ms/oai/access
- [ ] Desplegar modelo `text-embedding-ada-002` para embeddings
- [ ] Desplegar modelo `gpt-4` o `gpt-4-turbo` para respuestas
- [ ] Copiar:
  - Endpoint: `https://<recurso>.openai.azure.com`
  - API Key
  - Nombres de los deployments

**Costos estimados:** $50-200/mes según uso

---

### 1.2 Azure AI Search (Cognitive Search)
- [ ] Crear servicio Azure AI Search (tier: Standard S1 recomendado)
- [ ] Habilitar "Vector Search" en el recurso
- [ ] Copiar:
  - Endpoint: `https://<search>.search.windows.net`
  - Admin API Key (en Keys)

**Costos estimados:** $250/mes (Standard S1)

#### 1.2.1 Crear Índice de Búsqueda

Ejecutar este script en Azure Portal > AI Search > Index > Add Index (JSON):

```json
{
  "name": "rag-documents",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "searchable": false,
      "filterable": false,
      "sortable": false
    },
    {
      "name": "chunk_id",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "sortable": false
    },
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true,
      "analyzer": "es.microsoft"
    },
    {
      "name": "content_vector",
      "type": "Collection(Edm.Single)",
      "searchable": true,
      "vectorSearchDimensions": 1536,
      "vectorSearchProfileName": "vector-profile"
    },
    {
      "name": "document_id",
      "type": "Edm.String",
      "filterable": true,
      "facetable": true
    },
    {
      "name": "filename",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true
    },
    {
      "name": "chunk_index",
      "type": "Edm.Int32",
      "filterable": true,
      "sortable": true
    },
    {
      "name": "created_at",
      "type": "Edm.DateTimeOffset",
      "filterable": true,
      "sortable": true
    },
    {
      "name": "metadata",
      "type": "Edm.String",
      "searchable": false
    }
  ],
  "vectorSearch": {
    "algorithms": [
      {
        "name": "vector-algorithm",
        "kind": "hnsw",
        "hnswParameters": {
          "metric": "cosine",
          "m": 4,
          "efConstruction": 400,
          "efSearch": 500
        }
      }
    ],
    "profiles": [
      {
        "name": "vector-profile",
        "algorithm": "vector-algorithm"
      }
    ]
  }
}
```

- [ ] Índice creado y activo

---

### 1.3 Azure Blob Storage
- [ ] Crear Storage Account (Standard LRS es suficiente)
- [ ] Crear 3 contenedores:
  - `raw-documents` (acceso privado)
  - `processed-documents` (acceso privado)
  - `deleted-documents` (acceso privado)
- [ ] Copiar Connection String (Settings > Access Keys)

**Costos estimados:** $5-20/mes

---

### 1.4 Azure Cosmos DB
- [ ] Crear cuenta Cosmos DB (API: Core SQL/NoSQL)
- [ ] Elegir modo **Serverless** (más económico para empezar)
- [ ] Crear base de datos: `rag-system`
- [ ] Crear contenedores:

#### Contenedor 1: `documents_metadata`
```json
{
  "id": "string (PK)",
  "document_id": "string",
  "filename": "string",
  "blob_url": "string",
  "upload_date": "datetime",
  "processed_date": "datetime",
  "status": "pending|processing|processed|failed",
  "hash": "string (índice único)",
  "chunks_count": "number",
  "chunk_ids": ["array"],
  "search_index_ids": ["array"],
  "metadata": {
    "department": "string",
    "document_type": "string",
    "tags": ["array"]
  }
}
```

#### Contenedor 2: `query_history`
```json
{
  "id": "string (PK)",
  "query_id": "string",
  "query": "string",
  "timestamp": "datetime",
  "user_id": "string",
  "answer": "string",
  "sources": ["array"],
  "execution_time_ms": "number"
}
```

- [ ] Copiar:
  - URI: `https://<cosmos>.documents.azure.com:443/`
  - Primary Key

**Costos estimados:** $10-50/mes (Serverless)

---

### 1.5 Azure Document Intelligence (Opcional pero recomendado)
- [ ] Crear recurso Form Recognizer
- [ ] Copiar:
  - Endpoint
  - API Key

**Costos estimados:** ~$25/mes (1000 páginas)

---

## Fase 2: Configurar n8n 🔧

### 2.1 Configurar Credenciales

Ir a Settings > Credentials en n8n y agregar:

#### Credencial 1: Azure OpenAI
- [ ] Tipo: `HTTP Header Auth`
- [ ] Nombre: `Azure OpenAI`
- [ ] Header Name: `api-key`
- [ ] Header Value: `<TU_AZURE_OPENAI_KEY>`

#### Credencial 2: Azure AI Search
- [ ] Tipo: `HTTP Header Auth`
- [ ] Nombre: `Azure AI Search`
- [ ] Header Name: `api-key`
- [ ] Header Value: `<TU_SEARCH_KEY>`

#### Credencial 3: Azure Blob Storage
- [ ] Tipo: `Generic Auth`
- [ ] Nombre: `Azure Blob`
- [ ] Connection String: `<TU_CONNECTION_STRING>`

#### Credencial 4: Azure Cosmos DB
- [ ] Tipo: `HTTP Header Auth`
- [ ] Nombre: `Cosmos DB`
- [ ] Configurar Authorization header con master key

---

### 2.2 Configurar Variables de Entorno

Editar archivo de configuración de n8n (docker-compose.yml o .env):

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<tu-recurso>.openai.azure.com
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_GPT_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2023-05-15

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://<tu-search>.search.windows.net
AZURE_SEARCH_INDEX=rag-documents
AZURE_SEARCH_API_VERSION=2023-11-01

# Cosmos DB
COSMOS_DB_ENDPOINT=https://<tu-cosmos>.documents.azure.com:443/
COSMOS_DB_DATABASE=rag-system
COSMOS_DB_CONTAINER_METADATA=documents_metadata
COSMOS_DB_CONTAINER_QUERIES=query_history

# Blob Storage
AZURE_STORAGE_CONNECTION_STRING=<tu-connection-string>

# Configuración RAG
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
```

- [ ] Variables configuradas
- [ ] n8n reiniciado para aplicar cambios

---

## Fase 3: Crear Workflows 🔄

### 3.1 Opción Automática (Recomendada)

Ejecutar desde Cursor/Terminal:

```bash
cd "/Users/macronald/Banco Caja Social/RAG Agent"
python3 setup_rag_workflows.py
```

- [ ] Ejecutado exitosamente
- [ ] 3 workflows creados en n8n

---

### 3.2 Opción Manual

Importar manualmente cada workflow desde archivos JSON:

1. Ir a n8n > Workflows > Import from File
2. Importar los 3 workflows creados

- [ ] Workflow 1: RAG - Ingesta Completa de Documentos
- [ ] Workflow 2: RAG - Sistema de Consultas Completo
- [ ] Workflow 3: RAG - Eliminar Documento

---

## Fase 4: Completar Integraciones Reales 🔌

Los workflows creados tienen **placeholders** que debes reemplazar:

### 4.1 Workflow de Ingesta

#### Nodo: "📄 Extraer Texto"
**Reemplazar con:**
- Tipo: `HTTP Request`
- Method: `POST`
- URL: `{{ $env.AZURE_FORM_RECOGNIZER_ENDPOINT }}/formrecognizer/documentModels/prebuilt-read:analyze?api-version=2023-07-31`
- Headers:
  - `Ocp-Apim-Subscription-Key`: `{{ $credentials.azureFormRecognizer.apiKey }}`
- Body:
```json
{
  "base64Source": "{{ $binary.data.data }}"
}
```

#### Nodo: "🧮 Generar Embeddings"
**Reemplazar con:**
- Tipo: `HTTP Request`
- Method: `POST`
- URL: `{{ $env.AZURE_OPENAI_ENDPOINT }}/openai/deployments/{{ $env.AZURE_OPENAI_EMBEDDING_DEPLOYMENT }}/embeddings?api-version={{ $env.AZURE_OPENAI_API_VERSION }}`
- Authentication: Usar credencial `Azure OpenAI`
- Body:
```json
{
  "input": "{{ $json.chunk_text }}"
}
```

#### Nodo: "💾 Indexar en AI Search"
**Reemplazar con:**
- Tipo: `HTTP Request`
- Method: `POST`
- URL: `{{ $env.AZURE_SEARCH_ENDPOINT }}/indexes/{{ $env.AZURE_SEARCH_INDEX }}/docs/index?api-version={{ $env.AZURE_SEARCH_API_VERSION }}`
- Authentication: Usar credencial `Azure AI Search`
- Body:
```json
{
  "value": [
    {
      "@search.action": "upload",
      "id": "{{ $json.chunk_id }}",
      "chunk_id": "{{ $json.chunk_id }}",
      "content": "{{ $json.chunk_text }}",
      "content_vector": {{ $json.embedding }},
      "document_id": "{{ $json.document_id }}",
      "filename": "{{ $json.filename }}",
      "chunk_index": {{ $json.chunk_index }},
      "created_at": "{{ $now }}",
      "metadata": "{{ JSON.stringify($json.metadata) }}"
    }
  ]
}
```

- [ ] Nodos actualizados en workflow de ingesta

---

### 4.2 Workflow de Consultas

#### Nodo: "🧮 Generar Embedding"
- [ ] Configurado igual que en ingesta

#### Nodo: "🔍 Búsqueda Vectorial"
**Reemplazar con:**
- Tipo: `HTTP Request`
- Method: `POST`
- URL: `{{ $env.AZURE_SEARCH_ENDPOINT }}/indexes/{{ $env.AZURE_SEARCH_INDEX }}/docs/search?api-version={{ $env.AZURE_SEARCH_API_VERSION }}`
- Body:
```json
{
  "search": "*",
  "vectorQueries": [
    {
      "kind": "vector",
      "vector": {{ $json.embedding }},
      "fields": "content_vector",
      "k": {{ $env.TOP_K_RESULTS || 5 }}
    }
  ],
  "select": "chunk_id,content,document_id,filename,metadata",
  "top": {{ $env.TOP_K_RESULTS || 5 }}
}
```

#### Nodo: "🤖 Generar Respuesta"
**Reemplazar con:**
- Tipo: `HTTP Request`
- Method: `POST`
- URL: `{{ $env.AZURE_OPENAI_ENDPOINT }}/openai/deployments/{{ $env.AZURE_OPENAI_GPT_DEPLOYMENT }}/chat/completions?api-version={{ $env.AZURE_OPENAI_API_VERSION }}`
- Body:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "Eres un asistente experto del Banco Caja Social. Responde basándote ÚNICAMENTE en el contexto proporcionado. Si no encuentras la información en el contexto, indica que no tienes esa información disponible."
    },
    {
      "role": "user",
      "content": "Contexto:\n{{ $json.context }}\n\nPregunta: {{ $json.query }}\n\nProporciona una respuesta clara y precisa basada únicamente en el contexto anterior."
    }
  ],
  "temperature": {{ $env.TEMPERATURE || 0.3 }},
  "max_tokens": {{ $env.MAX_TOKENS || 800 }},
  "top_p": 0.95
}
```

- [ ] Nodos actualizados en workflow de consultas

---

### 4.3 Workflow de Eliminación

#### Nodo: "📋 Obtener Metadata"
**Reemplazar con:**
- Tipo: `HTTP Request` a Cosmos DB
- Method: `GET` o `POST` (query)
- Consultar documento por `document_id`

#### Nodo: "🗑️ Eliminar del Índice"
**Reemplazar con:**
- Tipo: `HTTP Request`
- Method: `POST`
- URL: `{{ $env.AZURE_SEARCH_ENDPOINT }}/indexes/{{ $env.AZURE_SEARCH_INDEX }}/docs/index?api-version={{ $env.AZURE_SEARCH_API_VERSION }}`
- Body:
```json
{
  "value": [
    {{ $json.chunk_ids.map(id => ({ "@search.action": "delete", "id": id })) }}
  ]
}
```

- [ ] Nodos actualizados en workflow de eliminación

---

## Fase 5: Pruebas 🧪

### 5.1 Probar Workflow de Ingesta

**Método 1: Con curl**
```bash
curl -X POST http://159.203.149.247:5678/webhook/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test_document.txt",
    "file_base64": "RXN0ZSBlcyB1biBkb2N1bWVudG8gZGUgcHJ1ZWJhIGRlbCBCYW5jbyBDYWphIFNvY2lhbC4gQ29udGllbmUgaW5mb3JtYWNpw7NuIHNvYnJlIHByb2R1Y3RvcyBmaW5hbmNpZXJvcy4=",
    "department": "productos",
    "document_type": "manual",
    "uploaded_by": "test_user"
  }'
```

**Método 2: Desde Postman**
- URL: `http://159.203.149.247:5678/webhook/rag/ingest`
- Method: POST
- Body: JSON con los campos anteriores

**Verificar:**
- [ ] Respuesta exitosa con `document_id`
- [ ] Chunks generados correctamente
- [ ] No errores en n8n execution log

---

### 5.2 Probar Workflow de Consultas

```bash
curl -X POST http://159.203.149.247:5678/webhook/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué productos financieros ofrece el banco?"
  }'
```

**Verificar:**
- [ ] Respuesta con texto generado
- [ ] Fuentes incluidas
- [ ] Relevancia de la respuesta

---

### 5.3 Probar Workflow de Eliminación

```bash
curl -X DELETE http://159.203.149.247:5678/webhook/rag/document \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc_test_12345"
  }'
```

**Verificar:**
- [ ] Confirmación de eliminación
- [ ] Documento ya no aparece en búsquedas

---

## Fase 6: Activación y Monitoreo 📊

### 6.1 Activar Workflows
- [ ] Workflow de ingesta activado
- [ ] Workflow de consultas activado
- [ ] Workflow de eliminación activado (si es necesario)

### 6.2 Configurar Monitoreo
- [ ] Revisar logs de ejecución en n8n
- [ ] Configurar alertas de error (opcional)
- [ ] Establecer métricas de uso:
  - Documentos procesados/día
  - Consultas/día
  - Tiempo promedio de respuesta
  - Costos de API calls

### 6.3 Documentación de Endpoints

Documentar tus endpoints públicos:

```
POST http://159.203.149.247:5678/webhook/rag/ingest
  - Ingesta de documentos
  
POST http://159.203.149.247:5678/webhook/rag/query
  - Consultas al RAG
  
DELETE http://159.203.149.247:5678/webhook/rag/document
  - Eliminación de documentos
```

- [ ] Endpoints documentados
- [ ] Ejemplos de uso compartidos con el equipo

---

## Fase 7: Optimizaciones (Post-Lanzamiento) 🚀

### 7.1 Performance
- [ ] Implementar caché de embeddings frecuentes
- [ ] Optimizar tamaño de chunks (A/B testing)
- [ ] Ajustar parámetro `k` en búsqueda vectorial
- [ ] Implementar filtros por metadata

### 7.2 Seguridad
- [ ] Implementar autenticación en webhooks
- [ ] Rate limiting
- [ ] Validación de tipos de archivo permitidos
- [ ] Sanitización de inputs

### 7.3 Escalabilidad
- [ ] Considerar Azure Functions para procesamiento pesado
- [ ] Implementar cola de procesamiento para documentos grandes
- [ ] Particionamiento de Cosmos DB por tenant/departamento

---

## Resumen de Costos Mensuales 💰

| Servicio | Tier | Costo Aprox. |
|----------|------|--------------|
| Azure OpenAI | Pay-as-you-go | $50-200 |
| Azure AI Search | Standard S1 | $250 |
| Blob Storage | Standard LRS | $5-20 |
| Cosmos DB | Serverless | $10-50 |
| Document Intelligence | S0 | $25 |
| **Total** | | **$340-545/mes** |

---

## Contactos de Soporte 📞

- **Azure Support:** Portal de Azure > Support
- **n8n Community:** https://community.n8n.io
- **Documentación Azure OpenAI:** https://learn.microsoft.com/azure/ai-services/openai/

---

## Notas Finales 📝

✅ **Backup:** Exportar workflows regularmente desde n8n
✅ **Versioning:** Mantener versiones de workflows en Git
✅ **Testing:** Probar con datos reales antes de producción
✅ **Compliance:** Verificar políticas de privacidad del banco para datos sensibles

---

**Última actualización:** 2025-10-21

