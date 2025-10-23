# 🔄 RAG con Documentos Temporales

## 📋 Descripción

Sistema que permite subir documentos junto con la consulta para que el RAG genere respuestas basándose tanto en:
- 📚 Documentos pre-indexados en el sistema
- 📄 Documento temporal proporcionado en la consulta

## 🎯 Casos de Uso

### Caso 1: Análisis de Contrato
```
Usuario: "¿Este contrato cumple con nuestras políticas?"
+ Sube: contrato_cliente_nuevo.pdf

RAG:
1. Analiza el contrato subido
2. Busca políticas en documentos indexados
3. Compara y responde
```

### Caso 2: Comparación de Documentos
```
Usuario: "¿Qué diferencias hay entre este reporte y los anteriores?"
+ Sube: reporte_trimestre_actual.pdf

RAG:
1. Extrae datos del reporte actual
2. Busca reportes anteriores en el índice
3. Compara y lista diferencias
```

### Caso 3: Validación de Información
```
Usuario: "¿La información de esta factura es correcta?"
+ Sube: factura.pdf

RAG:
1. Extrae datos de la factura
2. Busca información de referencia (precios, políticas)
3. Valida y responde
```

---

## 🔧 Modificaciones Necesarias

### 1. Nuevo Workflow en n8n

**Nombre**: `RAG - Consulta con Documento Temporal`

**Webhook**: POST `/webhook/rag/query-with-document`

**Input esperado**:
```json
{
  "query": "¿Este contrato cumple con nuestras políticas?",
  "document": {
    "filename": "contrato.pdf",
    "file_base64": "JVBERi0xLjQK...",
    "use_indexed_docs": true,  // Si también buscar en docs indexados
    "top_k_indexed": 3          // Cuántos docs indexados traer
  }
}
```

---

## 📊 Workflow Detallado

### Nodos del Workflow

#### 1. Webhook - Recibir Consulta + Documento
```javascript
// Validar input
if (!$json.query || !$json.document || !$json.document.file_base64) {
  throw new Error('query y document.file_base64 son requeridos');
}
```

#### 2. Extraer Texto del Documento Temporal
```javascript
// Usando Azure Document Intelligence o librería local
const base64Content = $json.document.file_base64;
const buffer = Buffer.from(base64Content, 'base64');

// Llamar a Azure Form Recognizer
// O usar librería como pdf-parse, pdfplumber
```

**Configuración del nodo**:
- Tipo: HTTP Request o Code
- Destino: Azure Document Intelligence API
- Output: texto extraído

#### 3. Dividir Documento Temporal en Chunks
```javascript
const text = $json.extracted_text;
const CHUNK_SIZE = 500;
const OVERLAP = 50;

const chunks = [];
let start = 0;
let chunkIndex = 0;

while (start < text.length) {
  const end = Math.min(start + CHUNK_SIZE, text.length);
  chunks.push({
    chunk_index: chunkIndex++,
    content: text.substring(start, end),
    source: 'temporary_document',
    filename: $json.document.filename
  });
  start = end - OVERLAP;
}

return chunks.map(c => ({ json: c }));
```

#### 4. Generar Embeddings del Documento Temporal
```javascript
// Para cada chunk del documento temporal
const chunks = $input.all();
const embeddings = [];

for (const chunk of chunks) {
  // Llamar a Azure OpenAI Embeddings
  const embedding = await callAzureEmbeddings(chunk.json.content);
  embeddings.push({
    ...chunk.json,
    embedding: embedding
  });
}

return embeddings;
```

**Nodo HTTP Request a Azure OpenAI**:
```
POST https://<recurso>.openai.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15

Headers:
  api-key: {{ $credentials.azureOpenAI.key }}

Body:
{
  "input": "{{ $json.content }}"
}
```

#### 5. Generar Embedding de la Pregunta
```javascript
// Mismo proceso que en el workflow original
const query = $json.query;

// Llamar a Azure OpenAI Embeddings para la pregunta
```

#### 6. [OPCIONAL] Buscar en Índice Vectorial
**Solo si `use_indexed_docs: true`**

```javascript
if ($json.document.use_indexed_docs) {
  // Buscar en Azure AI Search
  const indexedDocs = await searchAzureAISearch(
    $json.query_embedding,
    $json.document.top_k_indexed || 3
  );
  
  return [{
    json: {
      ...$json,
      indexed_context: indexedDocs
    }
  }];
}
```

**Nodo HTTP Request a Azure AI Search**:
```
POST https://<search>.search.windows.net/indexes/rag-documents/docs/search?api-version=2023-11-01

Body:
{
  "search": "*",
  "vectorQueries": [{
    "kind": "vector",
    "vector": {{ $json.query_embedding }},
    "fields": "content_vector",
    "k": {{ $json.document.top_k_indexed || 3 }}
  }],
  "select": "content,filename,metadata"
}
```

#### 7. Calcular Similitud con Chunks del Documento Temporal
```javascript
// Calcular similitud coseno entre query embedding y chunks temporales
function cosineSimilarity(vec1, vec2) {
  const dotProduct = vec1.reduce((sum, val, i) => sum + val * vec2[i], 0);
  const mag1 = Math.sqrt(vec1.reduce((sum, val) => sum + val * val, 0));
  const mag2 = Math.sqrt(vec2.reduce((sum, val) => sum + val * val, 0));
  return dotProduct / (mag1 * mag2);
}

const queryEmbedding = $json.query_embedding;
const tempDocChunks = $json.temp_doc_chunks;

const rankedChunks = tempDocChunks.map(chunk => ({
  ...chunk,
  similarity: cosineSimilarity(queryEmbedding, chunk.embedding)
})).sort((a, b) => b.similarity - a.similarity);

// Tomar top-K
const topK = 3;
const selectedChunks = rankedChunks.slice(0, topK);

return [{
  json: {
    ...$json,
    selected_temp_chunks: selectedChunks
  }
}];
```

#### 8. Construir Contexto Combinado
```javascript
const tempChunks = $json.selected_temp_chunks;
const indexedChunks = $json.indexed_context || [];

let context = "";

// Contexto del documento temporal
if (tempChunks.length > 0) {
  context += "=== DOCUMENTO PROPORCIONADO ===\n\n";
  tempChunks.forEach((chunk, i) => {
    context += `[Sección ${i + 1} - ${chunk.filename}]\n${chunk.content}\n\n`;
  });
  context += "---\n\n";
}

// Contexto de documentos indexados
if (indexedChunks.length > 0) {
  context += "=== DOCUMENTOS DE REFERENCIA ===\n\n";
  indexedChunks.forEach((doc, i) => {
    context += `[Referencia ${i + 1} - ${doc.filename}]\n${doc.content}\n\n`;
  });
}

return [{
  json: {
    query: $json.query,
    context: context,
    sources: {
      temporary: tempChunks.map(c => ({ filename: c.filename, source: 'temporal' })),
      indexed: indexedChunks.map(d => ({ filename: d.filename, source: 'indexado' }))
    }
  }
}];
```

#### 9. Generar Respuesta con GPT-4
```javascript
// Llamar a Azure OpenAI GPT-4 con prompt especializado
```

**Nodo HTTP Request a Azure OpenAI**:
```
POST https://<recurso>.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2023-05-15

Body:
{
  "messages": [
    {
      "role": "system",
      "content": "Eres un asistente experto del Banco Caja Social. Analiza el documento proporcionado por el usuario Y compáralo con los documentos de referencia del sistema. Responde basándote en AMBAS fuentes. Cita claramente si la información viene del documento proporcionado o de los documentos de referencia."
    },
    {
      "role": "user",
      "content": "{{ $json.context }}\n\nPregunta del usuario: {{ $json.query }}\n\nAnaliza el documento proporcionado y responde la pregunta, comparando con la información de referencia cuando sea relevante."
    }
  ],
  "temperature": 0.3,
  "max_tokens": 1000
}
```

#### 10. Responder al Usuario
```json
{
  "answer": "Respuesta generada...",
  "sources": {
    "temporary_document": ["contrato.pdf"],
    "indexed_documents": ["politicas_v2.pdf", "manual_contratos.pdf"]
  },
  "analysis": {
    "document_provided": true,
    "indexed_docs_used": true,
    "comparison_made": true
  }
}
```

---

## 💻 Ejemplo de Uso

### Con Python

```python
import base64
import requests

def query_with_document(question, document_path, use_indexed=True):
    """
    Consultar RAG con documento temporal
    
    Args:
        question: Pregunta del usuario
        document_path: Ruta al documento temporal
        use_indexed: Si también buscar en docs indexados
    """
    # Leer y codificar documento
    with open(document_path, 'rb') as f:
        file_content = base64.b64encode(f.read()).decode('utf-8')
    
    # Preparar payload
    payload = {
        "query": question,
        "document": {
            "filename": document_path.split('/')[-1],
            "file_base64": file_content,
            "use_indexed_docs": use_indexed,
            "top_k_indexed": 3
        }
    }
    
    # Enviar request
    response = requests.post(
        'http://159.203.149.247:5678/webhook/rag/query-with-document',
        json=payload,
        timeout=60  # Puede tardar más con documento temporal
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Respuesta: {result['answer']}\n")
        print(f"📄 Documento temporal: {result['sources']['temporary_document']}")
        print(f"📚 Docs indexados: {result['sources']['indexed_documents']}")
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        return None

# Ejemplo de uso
result = query_with_document(
    question="¿Este contrato cumple con nuestras políticas de crédito?",
    document_path="./contratos/nuevo_contrato.pdf",
    use_indexed=True
)
```

### Con cURL

```bash
# Convertir documento a base64
BASE64_DOC=$(base64 -i documento.pdf)

# Hacer consulta
curl -X POST http://159.203.149.247:5678/webhook/rag/query-with-document \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"¿Este documento cumple con las políticas?\",
    \"document\": {
      \"filename\": \"documento.pdf\",
      \"file_base64\": \"$BASE64_DOC\",
      \"use_indexed_docs\": true,
      \"top_k_indexed\": 3
    }
  }"
```

---

## ⚙️ Configuración en n8n

### Variables de Entorno Adicionales

Agregar a `.env`:
```env
# Procesamiento de documentos temporales
TEMP_DOC_MAX_SIZE=10485760        # 10MB máximo
TEMP_DOC_CHUNK_SIZE=500            # Mismo que docs permanentes
TEMP_DOC_TOP_K=3                   # Top chunks del doc temporal
ENABLE_INDEXED_SEARCH=true         # Permitir búsqueda combinada
```

### Credenciales Necesarias

Las mismas que el workflow de consultas normal:
- ✅ Azure OpenAI (embeddings + GPT-4)
- ✅ Azure AI Search (opcional, si `use_indexed_docs: true`)
- ✅ Azure Document Intelligence (para extraer texto)

---

## 🎨 Variantes del Workflow

### Variante 1: Solo Documento Temporal (Sin índice)
```json
{
  "query": "Resume este documento",
  "document": {
    "filename": "reporte.pdf",
    "file_base64": "...",
    "use_indexed_docs": false  // No buscar en índice
  }
}
```
**Caso de uso**: Análisis de documento independiente

---

### Variante 2: Múltiples Documentos Temporales
```json
{
  "query": "Compara estos dos contratos",
  "documents": [
    {
      "filename": "contrato_a.pdf",
      "file_base64": "...",
      "label": "Contrato A"
    },
    {
      "filename": "contrato_b.pdf",
      "file_base64": "...",
      "label": "Contrato B"
    }
  ],
  "use_indexed_docs": true
}
```
**Caso de uso**: Comparación de documentos

---

### Variante 3: Documento + Filtros en Índice
```json
{
  "query": "¿Este documento cumple con políticas de 2025?",
  "document": {
    "filename": "documento.pdf",
    "file_base64": "..."
  },
  "filters": {
    "document_type": "policy",
    "year": 2025
  },
  "use_indexed_docs": true
}
```
**Caso de uso**: Búsqueda contextual específica

---

## 📊 Ventajas vs. Desventajas

### ✅ Ventajas

1. **Flexibilidad**: Analizar documentos sin indexarlos permanentemente
2. **Rapidez**: No esperar a que se indexe el documento
3. **Contexto combinado**: Mejor calidad de respuestas
4. **Privacidad**: Documentos sensibles no se guardan
5. **Comparación**: Contrastar documento nuevo con base de conocimiento

### ⚠️ Desventajas

1. **Latencia**: Procesamiento en tiempo real más lento
2. **Límite de tamaño**: Documentos muy grandes pueden fallar
3. **Sin persistencia**: El documento no queda en el sistema
4. **Mayor costo**: Más tokens de GPT-4 por el contexto adicional
5. **Complejidad**: Workflow más complejo de mantener

---

## 🔍 Optimizaciones

### 1. Caché de Documentos Temporales
```javascript
// En nodo de Code
const documentHash = crypto.createHash('sha256')
  .update($json.document.file_base64)
  .digest('hex');

// Verificar si ya procesamos este doc recientemente (últimos 10 min)
const cached = await checkCache(documentHash);
if (cached) {
  return cached.chunks; // Reutilizar chunks y embeddings
}
```

### 2. Procesamiento Asíncrono
```javascript
// Para documentos grandes
if ($json.document.file_size > 5000000) { // 5MB
  // Procesar en background
  await triggerBackgroundProcessing($json);
  
  return [{
    json: {
      status: 'processing',
      job_id: 'job_123',
      check_url: '/webhook/rag/job-status/job_123'
    }
  }];
}
```

### 3. Priorización Inteligente
```javascript
// Dar más peso al documento temporal si es muy relevante
const tempChunkAvgSimilarity = tempChunks.reduce((sum, c) => sum + c.similarity, 0) / tempChunks.length;

if (tempChunkAvgSimilarity > 0.8) {
  // El documento temporal es muy relevante, priorizar
  topKTemp = 5;
  topKIndexed = 2;
} else {
  // Equilibrar entre ambos
  topKTemp = 3;
  topKIndexed = 3;
}
```

---

## 🧪 Testing

```bash
# Test 1: Solo documento temporal
python3 -c "
from scripts.test_rag_with_doc import query_with_document
query_with_document(
    'Resume este documento',
    'test_doc.pdf',
    use_indexed=False
)
"

# Test 2: Documento + índice
python3 -c "
from scripts.test_rag_with_doc import query_with_document
query_with_document(
    '¿Este contrato cumple políticas?',
    'contrato.pdf',
    use_indexed=True
)
"
```

---

## 📝 Próximos Pasos para Implementar

### Paso 1: Crear el Workflow
```bash
# Usar script base y modificar
python3 scripts/setup_rag_workflows.py
# Luego modificar en n8n UI el workflow de consultas
```

### Paso 2: Agregar Nodos de Procesamiento
1. Extraer texto del documento temporal
2. Chunking del documento
3. Generar embeddings temporales
4. Calcular similitud
5. Combinar con búsqueda en índice
6. Generar respuesta

### Paso 3: Configurar Variables
```bash
# Editar .env
nano .env
# Agregar variables de documentos temporales
```

### Paso 4: Probar
```bash
# Ejecutar test
python3 scripts/test_rag_with_document.py
```

---

## 💡 Casos de Uso Reales en Banco

1. **Análisis de contratos nuevos**: Subir contrato y validar con políticas
2. **Revisión de facturas**: Verificar datos contra tarifas indexadas
3. **Evaluación de reportes**: Comparar con reportes históricos
4. **Validación de formularios**: Verificar completitud con requisitos
5. **Due diligence**: Analizar documentos de terceros con políticas internas

---

**Última actualización**: 21 de Octubre, 2025  
**Complejidad**: ⭐⭐⭐ Alta  
**Tiempo de implementación**: 1-2 semanas

