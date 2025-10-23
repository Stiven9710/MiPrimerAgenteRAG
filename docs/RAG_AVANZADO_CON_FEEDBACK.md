# 🚀 RAG Avanzado con Sistema de Feedback y Validación

## 📋 Descripción

Sistema RAG mejorado que:
- ✅ Acepta **múltiples tipos de entrada** (texto, documentos, imágenes)
- ✅ Genera **respuestas de agente** contextualizadas
- ✅ **Valida con el usuario** si la respuesta fue útil
- ✅ **Captura métricas** de calidad
- ✅ **Complementa** respuestas valiosas automáticamente

---

## 🎯 Flujo Completo

```
┌─────────────────────────────────────────────────────────────┐
│  USUARIO                                                     │
│  Entrada: Texto + [Opcional: Docs/Imágenes]                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  FASE 1: PROCESAMIENTO DE ENTRADA                           │
├─────────────────────────────────────────────────────────────┤
│  1. Detectar tipo de entrada                                │
│     ├─ Solo texto                                           │
│     ├─ Texto + Documento(s)                                 │
│     └─ Texto + Imagen(es)                                   │
│                                                              │
│  2. Procesar cada tipo:                                     │
│     ├─ Documentos → OCR/Extracción de texto                │
│     ├─ Imágenes → GPT-4 Vision análisis                    │
│     └─ Texto → Embedding directo                           │
│                                                              │
│  3. Enriquecer contexto                                     │
│     └─ Buscar en docs indexados (opcional)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  FASE 2: GENERACIÓN DE RESPUESTA DE AGENTE                  │
├─────────────────────────────────────────────────────────────┤
│  1. Construir prompt avanzado con:                          │
│     ├─ Contexto de documentos                              │
│     ├─ Análisis de imágenes                                │
│     ├─ Información indexada                                │
│     └─ Instrucciones del agente                            │
│                                                              │
│  2. GPT-4 genera respuesta estructurada:                    │
│     ├─ answer: Respuesta principal                         │
│     ├─ confidence: Nivel de confianza (0-100)              │
│     ├─ sources: Fuentes utilizadas                         │
│     ├─ analysis: Análisis detallado                        │
│     └─ suggestions: Sugerencias de seguimiento             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  FASE 3: ENTREGA Y VALIDACIÓN                               │
├─────────────────────────────────────────────────────────────┤
│  1. Mostrar respuesta al usuario                            │
│                                                              │
│  2. Solicitar feedback:                                     │
│     ┌────────────────────────────────────┐                │
│     │ ¿Esta respuesta fue útil?          │                │
│     │ ⭐⭐⭐⭐⭐ [1-5 estrellas]        │                │
│     │ 👍 Sí  |  👎 No  |  💬 Comentario │                │
│     └────────────────────────────────────┘                │
│                                                              │
│  3. Capturar métricas:                                      │
│     ├─ Rating (1-5)                                        │
│     ├─ Fue útil (booleano)                                 │
│     ├─ Comentario del usuario                              │
│     ├─ Tiempo de respuesta                                 │
│     └─ Timestamp                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                ┌────────┴────────┐
                │                 │
         Rating ≥ 4?           Rating < 4?
                │                 │
                ▼                 ▼
┌─────────────────────────┐  ┌───────────────────────────┐
│ FASE 4A: COMPLEMENTAR   │  │ FASE 4B: MEJORAR          │
│ (Respuesta Valiosa)     │  │ (Respuesta Insuficiente)  │
├─────────────────────────┤  ├───────────────────────────┤
│ 1. Buscar info adicional│  │ 1. Analizar por qué falló │
│ 2. Generar complemento  │  │ 2. Buscar info alternativa│
│ 3. Ofrecer seguimiento  │  │ 3. Regenerar respuesta    │
│ 4. Guardar como ejemplo │  │ 4. Solicitar aclaración   │
└─────────────────────────┘  └───────────────────────────┘
```

---

## 🔧 Workflow en n8n: RAG Avanzado

### Webhook de Entrada

**Endpoint**: `POST /webhook/rag/advanced-query`

**Input Flexible**:
```json
{
  "query": "¿Este contrato cumple con las políticas de crédito?",
  "inputs": [
    {
      "type": "text",
      "content": "Información adicional sobre el cliente..."
    },
    {
      "type": "document",
      "filename": "contrato.pdf",
      "file_base64": "JVBERi0xLjQK..."
    },
    {
      "type": "image",
      "filename": "firma_contrato.jpg",
      "file_base64": "iVBORw0KGgoAAAANS..."
    }
  ],
  "options": {
    "use_indexed_docs": true,
    "require_high_confidence": true,
    "enable_feedback": true,
    "max_sources": 5
  }
}
```

---

## 📝 Nodos del Workflow Detallados

### NODO 1: Recibir y Validar Entrada

```javascript
// Validar y enriquecer input
const inputs = $json.inputs || [];
const query = $json.query;
const options = $json.options || {};

if (!query) {
  throw new Error('query es requerido');
}

// Clasificar inputs por tipo
const textInputs = inputs.filter(i => i.type === 'text');
const documentInputs = inputs.filter(i => i.type === 'document');
const imageInputs = inputs.filter(i => i.type === 'image');

// Generar ID único para esta consulta
const queryId = `query_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

return [{
  json: {
    query_id: queryId,
    query: query,
    text_inputs: textInputs,
    document_inputs: documentInputs,
    image_inputs: imageInputs,
    options: options,
    start_time: new Date().toISOString(),
    processing_stages: []
  }
}];
```

### NODO 2: Procesar Documentos

```javascript
// Procesar cada documento
const documentInputs = $json.document_inputs;
const processedDocs = [];

for (const doc of documentInputs) {
  // Extraer texto usando Azure Document Intelligence
  const extractedText = await extractTextFromDocument(doc.file_base64);
  
  // Dividir en chunks
  const chunks = splitIntoChunks(extractedText, 500, 50);
  
  // Generar embeddings
  const embeddings = await generateEmbeddings(chunks);
  
  processedDocs.push({
    filename: doc.filename,
    text: extractedText,
    chunks: chunks,
    embeddings: embeddings,
    source: 'user_provided_document'
  });
}

return [{
  json: {
    ...$json,
    processed_documents: processedDocs,
    processing_stages: [
      ...$json.processing_stages,
      { stage: 'document_processing', completed: true, timestamp: new Date().toISOString() }
    ]
  }
}];
```

### NODO 3: Analizar Imágenes con GPT-4 Vision

```javascript
// Procesar cada imagen
const imageInputs = $json.image_inputs;
const analyzedImages = [];

for (const img of imageInputs) {
  // Llamar a GPT-4 Vision
  const analysis = await analyzeImageWithGPT4Vision(
    img.file_base64,
    `Analiza esta imagen en el contexto de: ${$json.query}. 
     Describe todos los elementos relevantes, texto visible, 
     y cualquier información que pueda ayudar a responder la pregunta.`
  );
  
  analyzedImages.push({
    filename: img.filename,
    analysis: analysis,
    source: 'user_provided_image'
  });
}

return [{
  json: {
    ...$json,
    analyzed_images: analyzedImages,
    processing_stages: [
      ...$json.processing_stages,
      { stage: 'image_analysis', completed: true, timestamp: new Date().toISOString() }
    ]
  }
}];
```

**HTTP Request para GPT-4 Vision**:
```
POST https://<recurso>.openai.azure.com/openai/deployments/gpt-4-vision/chat/completions?api-version=2024-02-15-preview

Body:
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "{{ $json.analysis_prompt }}"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,{{ $json.image_base64 }}"
          }
        }
      ]
    }
  ],
  "max_tokens": 500
}
```

### NODO 4: Buscar en Índice Vectorial (Opcional)

```javascript
// Solo si use_indexed_docs = true
if ($json.options.use_indexed_docs) {
  // Generar embedding de la query
  const queryEmbedding = await generateEmbedding($json.query);
  
  // Buscar en Azure AI Search
  const indexedResults = await searchAzureAISearch(
    queryEmbedding,
    $json.options.max_sources || 5
  );
  
  return [{
    json: {
      ...$json,
      indexed_documents: indexedResults,
      processing_stages: [
        ...$json.processing_stages,
        { stage: 'indexed_search', completed: true, timestamp: new Date().toISOString() }
      ]
    }
  }];
}

return [$json];
```

### NODO 5: Construir Contexto Completo

```javascript
// Combinar todos los contextos
let fullContext = "";
let sources = [];

// 1. Documentos proporcionados
if ($json.processed_documents && $json.processed_documents.length > 0) {
  fullContext += "=== DOCUMENTOS PROPORCIONADOS POR EL USUARIO ===\n\n";
  
  $json.processed_documents.forEach((doc, i) => {
    fullContext += `[Documento ${i + 1}: ${doc.filename}]\n`;
    fullContext += `${doc.text.substring(0, 2000)}...\n\n`;
    sources.push({
      type: 'user_document',
      filename: doc.filename,
      relevance: 'high'
    });
  });
  
  fullContext += "---\n\n";
}

// 2. Análisis de imágenes
if ($json.analyzed_images && $json.analyzed_images.length > 0) {
  fullContext += "=== ANÁLISIS DE IMÁGENES PROPORCIONADAS ===\n\n";
  
  $json.analyzed_images.forEach((img, i) => {
    fullContext += `[Imagen ${i + 1}: ${img.filename}]\n`;
    fullContext += `${img.analysis}\n\n`;
    sources.push({
      type: 'user_image',
      filename: img.filename,
      relevance: 'high'
    });
  });
  
  fullContext += "---\n\n";
}

// 3. Información adicional de texto
if ($json.text_inputs && $json.text_inputs.length > 0) {
  fullContext += "=== INFORMACIÓN ADICIONAL ===\n\n";
  
  $json.text_inputs.forEach((txt, i) => {
    fullContext += `${txt.content}\n\n`;
  });
  
  fullContext += "---\n\n";
}

// 4. Documentos indexados
if ($json.indexed_documents && $json.indexed_documents.length > 0) {
  fullContext += "=== DOCUMENTOS DE REFERENCIA DEL BANCO ===\n\n";
  
  $json.indexed_documents.forEach((doc, i) => {
    fullContext += `[Referencia ${i + 1}: ${doc.filename}]\n`;
    fullContext += `${doc.content}\n\n`;
    sources.push({
      type: 'indexed_document',
      filename: doc.filename,
      relevance: doc.score || 'medium'
    });
  });
}

return [{
  json: {
    ...$json,
    full_context: fullContext,
    all_sources: sources,
    processing_stages: [
      ...$json.processing_stages,
      { stage: 'context_building', completed: true, timestamp: new Date().toISOString() }
    ]
  }
}];
```

### NODO 6: Generar Respuesta de Agente con GPT-4

```javascript
// Prompt avanzado para el agente
const systemPrompt = `Eres un asistente experto del Banco Caja Social con capacidades de análisis avanzadas.

Tu trabajo es:
1. Analizar toda la información proporcionada (documentos, imágenes, texto)
2. Contrastar con las políticas y procedimientos del banco
3. Generar una respuesta estructurada y accionable
4. Indicar tu nivel de confianza en la respuesta
5. Proporcionar sugerencias de seguimiento si es relevante

IMPORTANTE:
- Cita siempre tus fuentes
- Si no tienes suficiente información, di qué te falta
- Proporciona análisis, no solo resumen
- Se específico y práctico`;

const userPrompt = `${$json.full_context}

PREGUNTA DEL USUARIO:
${$json.query}

Por favor responde de forma estructurada con:
1. RESPUESTA PRINCIPAL (clara y directa)
2. ANÁLISIS DETALLADO (razonamiento)
3. CONFIANZA (0-100, qué tan seguro estás)
4. FUENTES UTILIZADAS
5. SUGERENCIAS DE SEGUIMIENTO (si aplica)
6. ADVERTENCIAS O CONSIDERACIONES (si aplica)`;

// Llamar a GPT-4
const response = await callGPT4(systemPrompt, userPrompt);

// Parsear respuesta estructurada
const structuredResponse = parseStructuredResponse(response);

return [{
  json: {
    query_id: $json.query_id,
    query: $json.query,
    answer: structuredResponse.answer,
    detailed_analysis: structuredResponse.analysis,
    confidence_score: structuredResponse.confidence,
    sources: $json.all_sources,
    follow_up_suggestions: structuredResponse.suggestions,
    warnings: structuredResponse.warnings,
    processing_time_ms: Date.now() - new Date($json.start_time).getTime(),
    timestamp: new Date().toISOString()
  }
}];
```

**HTTP Request a GPT-4**:
```
POST https://<recurso>.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2023-05-15

Body:
{
  "messages": [
    {
      "role": "system",
      "content": "{{ $json.system_prompt }}"
    },
    {
      "role": "user",
      "content": "{{ $json.user_prompt }}"
    }
  ],
  "temperature": 0.3,
  "max_tokens": 1500,
  "response_format": { "type": "json_object" }
}
```

### NODO 7: Responder al Usuario con Feedback Widget

```json
{
  "query_id": "query_1234567890_abc",
  "answer": {
    "main_response": "Basándome en el análisis del contrato proporcionado...",
    "detailed_analysis": "El contrato cumple con 8 de 10 requisitos de nuestras políticas...",
    "confidence": 85,
    "sources": [
      { "type": "user_document", "filename": "contrato.pdf" },
      { "type": "indexed_document", "filename": "politicas_credito_2025.pdf" }
    ],
    "follow_up_suggestions": [
      "Revisar cláusula de garantías adicionales",
      "Verificar historial crediticio del cliente"
    ],
    "warnings": [
      "El contrato no especifica penalizaciones por mora"
    ]
  },
  "processing_time_ms": 12543,
  "feedback_url": "http://159.203.149.247:5678/webhook/rag/feedback",
  "feedback_widget": {
    "query_id": "query_1234567890_abc",
    "question": "¿Esta respuesta te fue útil?",
    "options": [
      { "value": 5, "label": "⭐⭐⭐⭐⭐ Excelente" },
      { "value": 4, "label": "⭐⭐⭐⭐ Buena" },
      { "value": 3, "label": "⭐⭐⭐ Aceptable" },
      { "value": 2, "label": "⭐⭐ Insuficiente" },
      { "value": 1, "label": "⭐ No útil" }
    ],
    "allow_comment": true
  }
}
```

---

## 🔄 Workflow de Feedback

### Webhook de Feedback

**Endpoint**: `POST /webhook/rag/feedback`

**Input**:
```json
{
  "query_id": "query_1234567890_abc",
  "rating": 5,
  "was_helpful": true,
  "comment": "Excelente análisis, muy completo y claro",
  "user_id": "user@banco.com",
  "timestamp": "2025-10-21T10:30:00Z"
}
```

### NODO 1: Recibir y Guardar Feedback

```javascript
// Validar feedback
if (!$json.query_id || !$json.rating) {
  throw new Error('query_id y rating son requeridos');
}

// Enriquecer con metadata
const feedbackData = {
  ...$json,
  feedback_id: `feedback_${Date.now()}`,
  received_at: new Date().toISOString(),
  rating_category: $json.rating >= 4 ? 'positive' : $json.rating === 3 ? 'neutral' : 'negative'
};

// Guardar en Cosmos DB
await saveFeedbackToCosmosDB(feedbackData);

return [{
  json: feedbackData
}];
```

### NODO 2: Bifurcación por Rating

```javascript
// Decisión basada en rating
if ($json.rating >= 4) {
  // Rating alto → Complementar respuesta
  return [
    [{ json: { ...$json, action: 'complement' } }],
    []
  ];
} else {
  // Rating bajo → Mejorar respuesta
  return [
    [],
    [{ json: { ...$json, action: 'improve' } }]
  ];
}
```

### NODO 3A: Complementar Respuesta (Rating Alto)

```javascript
// La respuesta fue valiosa, vamos a complementarla
const originalQuery = await getOriginalQuery($json.query_id);

// Buscar información adicional relacionada
const additionalInfo = await searchRelatedInformation(
  originalQuery.query,
  originalQuery.answer,
  { 
    depth: 'detailed',
    include_examples: true,
    include_regulations: true 
  }
);

// Generar complemento
const complement = await generateComplement(
  originalQuery.answer,
  additionalInfo
);

// Guardar como caso de éxito
await saveasSuccessCase({
  query_id: $json.query_id,
  rating: $json.rating,
  comment: $json.comment,
  complement: complement
});

// Notificar al usuario (opcional)
return [{
  json: {
    query_id: $json.query_id,
    action_taken: 'complemented',
    complement: complement,
    notification: {
      type: 'complement_available',
      message: 'Hemos agregado información adicional basada en tu pregunta',
      url: `/query/${$json.query_id}/complement`
    }
  }
}];
```

**Prompt para Complemento**:
```
POST GPT-4

System: Eres un asistente experto. El usuario valoró positivamente una respuesta.
Ahora debes complementarla con información adicional valiosa.

User: 
RESPUESTA ORIGINAL:
{{ original_answer }}

INFORMACIÓN ADICIONAL ENCONTRADA:
{{ additional_info }}

TAREA:
Genera un complemento que:
1. Expanda puntos clave de la respuesta original
2. Añada ejemplos prácticos
3. Incluya referencias a regulaciones relevantes
4. Proporcione pasos accionables
5. Sea conciso pero valioso

No repitas información, solo complementa.
```

### NODO 3B: Mejorar Respuesta (Rating Bajo)

```javascript
// La respuesta no fue útil, analizar por qué y mejorar
const originalQuery = await getOriginalQuery($json.query_id);

// Analizar qué falló
const failureAnalysis = await analyzeFailure(
  originalQuery.query,
  originalQuery.answer,
  $json.rating,
  $json.comment
);

// Buscar información alternativa
const alternativeInfo = await searchAlternativeInformation(
  originalQuery.query,
  { 
    exclude_sources: originalQuery.sources,
    expand_search: true 
  }
);

// Regenerar respuesta mejorada
const improvedAnswer = await regenerateAnswer(
  originalQuery.query,
  alternativeInfo,
  failureAnalysis.insights
);

// Guardar para análisis
await saveFailureCase({
  query_id: $json.query_id,
  rating: $json.rating,
  comment: $json.comment,
  failure_reasons: failureAnalysis.reasons,
  improved_answer: improvedAnswer
});

// Notificar al usuario
return [{
  json: {
    query_id: $json.query_id,
    action_taken: 'improved',
    improved_answer: improvedAnswer,
    notification: {
      type: 'improved_answer_available',
      message: 'Hemos mejorado la respuesta basándonos en tu feedback',
      url: `/query/${$json.query_id}/improved`
    }
  }
}];
```

---

## 📊 Sistema de Métricas

### Estructura en Cosmos DB

#### Collection: `query_analytics`
```json
{
  "id": "analytics_query_1234567890_abc",
  "query_id": "query_1234567890_abc",
  "timestamp": "2025-10-21T10:15:00Z",
  "query": "¿Este contrato cumple políticas?",
  "user_id": "user@banco.com",
  
  "input_metrics": {
    "text_inputs": 1,
    "document_inputs": 1,
    "image_inputs": 0,
    "total_file_size_bytes": 2048576,
    "indexed_docs_used": true
  },
  
  "processing_metrics": {
    "start_time": "2025-10-21T10:15:00Z",
    "end_time": "2025-10-21T10:15:12Z",
    "total_time_ms": 12543,
    "stages": [
      { "stage": "document_processing", "time_ms": 3421 },
      { "stage": "image_analysis", "time_ms": 0 },
      { "stage": "indexed_search", "time_ms": 1234 },
      { "stage": "context_building", "time_ms": 234 },
      { "stage": "answer_generation", "time_ms": 7654 }
    ]
  },
  
  "output_metrics": {
    "answer_length_chars": 1234,
    "confidence_score": 85,
    "sources_count": 5,
    "sources_breakdown": {
      "user_documents": 1,
      "indexed_documents": 4,
      "user_images": 0
    }
  },
  
  "feedback": {
    "received": true,
    "received_at": "2025-10-21T10:30:00Z",
    "rating": 5,
    "was_helpful": true,
    "comment": "Excelente análisis",
    "time_to_feedback_seconds": 900
  },
  
  "actions_taken": {
    "complement_generated": true,
    "complement_at": "2025-10-21T10:31:00Z",
    "improved_answer": false,
    "saved_as_success_case": true
  },
  
  "cost_metrics": {
    "tokens_input": 3456,
    "tokens_output": 987,
    "estimated_cost_usd": 0.012
  }
}
```

### Dashboard de Métricas

```javascript
// Nodo para generar reporte de métricas
const analytics = await getAnalytics({
  period: 'last_7_days'
});

const report = {
  summary: {
    total_queries: analytics.length,
    avg_rating: calculateAverage(analytics.map(a => a.feedback.rating)),
    positive_feedback_rate: calculateRate(analytics, a => a.feedback.rating >= 4),
    avg_response_time_ms: calculateAverage(analytics.map(a => a.processing_metrics.total_time_ms)),
    total_cost_usd: calculateSum(analytics.map(a => a.cost_metrics.estimated_cost_usd))
  },
  
  input_breakdown: {
    text_only: countByType(analytics, 'text_only'),
    text_with_docs: countByType(analytics, 'text_with_docs'),
    text_with_images: countByType(analytics, 'text_with_images'),
    multimodal: countByType(analytics, 'multimodal')
  },
  
  quality_metrics: {
    high_confidence: countByConfidence(analytics, c => c >= 80),
    medium_confidence: countByConfidence(analytics, c => c >= 50 && c < 80),
    low_confidence: countByConfidence(analytics, c => c < 50)
  },
  
  top_use_cases: identifyTopUseCases(analytics),
  
  improvement_opportunities: identifyImprovements(analytics.filter(a => a.feedback.rating < 4))
};

return [{ json: report }];
```

---

## 💻 Script de Cliente Python

```python
"""
Cliente avanzado para RAG con múltiples tipos de entrada y feedback
"""

import base64
import requests
from typing import List, Dict, Optional, Union
from pathlib import Path

class AdvancedRAGClient:
    """Cliente para sistema RAG avanzado"""
    
    def __init__(self, base_url: str = "http://159.203.149.247:5678"):
        self.base_url = base_url.rstrip('/')
        self.query_endpoint = f"{self.base_url}/webhook/rag/advanced-query"
        self.feedback_endpoint = f"{self.base_url}/webhook/rag/feedback"
    
    def query(
        self,
        question: str,
        documents: List[str] = None,
        images: List[str] = None,
        additional_text: str = None,
        use_indexed: bool = True,
        require_high_confidence: bool = False
    ) -> Dict:
        """
        Realizar consulta avanzada con múltiples tipos de entrada
        
        Args:
            question: Pregunta principal
            documents: Lista de rutas a documentos
            images: Lista de rutas a imágenes
            additional_text: Texto adicional de contexto
            use_indexed: Buscar también en docs indexados
            require_high_confidence: Solo responder si confianza >80%
        
        Returns:
            Diccionario con respuesta y metadata
        """
        
        # Preparar inputs
        inputs = []
        
        # Agregar texto adicional
        if additional_text:
            inputs.append({
                "type": "text",
                "content": additional_text
            })
        
        # Agregar documentos
        if documents:
            for doc_path in documents:
                with open(doc_path, 'rb') as f:
                    file_content = base64.b64encode(f.read()).decode('utf-8')
                
                inputs.append({
                    "type": "document",
                    "filename": Path(doc_path).name,
                    "file_base64": file_content
                })
        
        # Agregar imágenes
        if images:
            for img_path in images:
                with open(img_path, 'rb') as f:
                    file_content = base64.b64encode(f.read()).decode('utf-8')
                
                inputs.append({
                    "type": "image",
                    "filename": Path(img_path).name,
                    "file_base64": file_content
                })
        
        # Preparar payload
        payload = {
            "query": question,
            "inputs": inputs,
            "options": {
                "use_indexed_docs": use_indexed,
                "require_high_confidence": require_high_confidence,
                "enable_feedback": True,
                "max_sources": 5
            }
        }
        
        # Enviar request
        response = requests.post(
            self.query_endpoint,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Guardar query_id para feedback posterior
        self.last_query_id = result.get('query_id')
        
        return result
    
    def send_feedback(
        self,
        query_id: str,
        rating: int,
        was_helpful: bool,
        comment: str = "",
        user_id: str = "anonymous"
    ) -> Dict:
        """
        Enviar feedback sobre una respuesta
        
        Args:
            query_id: ID de la consulta
            rating: Calificación 1-5
            was_helpful: Si fue útil
            comment: Comentario opcional
            user_id: ID del usuario
        """
        
        payload = {
            "query_id": query_id,
            "rating": rating,
            "was_helpful": was_helpful,
            "comment": comment,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            self.feedback_endpoint,
            json=payload
        )
        response.raise_for_status()
        
        return response.json()
    
    def query_with_feedback_loop(
        self,
        question: str,
        **kwargs
    ) -> Dict:
        """
        Consulta con loop de feedback interactivo
        """
        
        # Hacer consulta
        result = self.query(question, **kwargs)
        
        # Mostrar respuesta
        print("\n" + "="*80)
        print("RESPUESTA:")
        print("="*80)
        print(f"\n{result['answer']['main_response']}\n")
        
        if result['answer'].get('warnings'):
            print("⚠️  ADVERTENCIAS:")
            for warning in result['answer']['warnings']:
                print(f"   • {warning}")
        
        print(f"\n📊 Confianza: {result['answer']['confidence']}%")
        print(f"⏱️  Tiempo: {result['processing_time_ms']/1000:.2f}s")
        
        # Solicitar feedback
        print("\n" + "-"*80)
        print("¿Esta respuesta te fue útil? (1-5 estrellas)")
        rating = int(input("Rating: "))
        
        comment = input("Comentario (opcional): ")
        
        # Enviar feedback
        feedback_result = self.send_feedback(
            query_id=result['query_id'],
            rating=rating,
            was_helpful=rating >= 4,
            comment=comment
        )
        
        print(f"\n✅ Feedback enviado: {feedback_result['action_taken']}")
        
        if feedback_result.get('notification'):
            print(f"💡 {feedback_result['notification']['message']}")
        
        return {
            'query_result': result,
            'feedback_result': feedback_result
        }


# Ejemplo de uso
if __name__ == "__main__":
    client = AdvancedRAGClient()
    
    # Caso 1: Solo texto
    result1 = client.query(
        question="¿Cuáles son los requisitos para crédito de vivienda?",
        use_indexed=True
    )
    
    # Caso 2: Texto + Documento
    result2 = client.query(
        question="¿Este contrato cumple con nuestras políticas?",
        documents=["./contrato.pdf"],
        use_indexed=True
    )
    
    # Caso 3: Texto + Documento + Imagen
    result3 = client.query(
        question="¿La firma en este contrato es válida?",
        documents=["./contrato.pdf"],
        images=["./firma.jpg"],
        additional_text="El cliente es persona natural",
        use_indexed=True
    )
    
    # Enviar feedback
    client.send_feedback(
        query_id=result3['query_id'],
        rating=5,
        was_helpful=True,
        comment="Análisis muy completo"
    )
```

---

## 📈 Métricas Clave a Monitorear

### KPIs de Calidad
- **Tasa de feedback positivo** (rating ≥ 4): Objetivo >85%
- **Confianza promedio**: Objetivo >75%
- **Tasa de complemento** (respuestas mejoradas): Objetivo >20%

### KPIs de Performance
- **Tiempo de respuesta promedio**: Objetivo <15s
- **Tasa de error**: Objetivo <2%
- **Disponibilidad**: Objetivo >99.5%

### KPIs de Uso
- **Consultas/día** por tipo de entrada
- **Usuarios activos** que dan feedback
- **Casos de éxito** guardados

### KPIs de Costo
- **Costo por consulta**: Monitorear tendencia
- **ROI del sistema**: Costo vs. valor generado

---

## 🎯 Casos de Uso del Banco

### 1. Análisis de Contratos con Firma
```
Input:
  - Texto: "¿Este contrato está listo para firma?"
  - Documento: contrato.pdf
  - Imagen: firma_representante.jpg

Output:
  - Validación de completitud
  - Verificación de firma
  - Lista de pendientes
  - Confianza: 92%
```

### 2. Evaluación de Facturas
```
Input:
  - Texto: "¿Esta factura es válida?"
  - Documento: factura.pdf
  - Imagen: foto_factura_fisica.jpg

Output:
  - Validación de datos
  - Comparación con tarifario
  - Detección de inconsistencias
  - Confianza: 88%
```

### 3. Due Diligence Completo
```
Input:
  - Texto: "Analizar documentación del cliente X"
  - Documentos: [cedula.pdf, estados_cuenta.pdf, declaracion_renta.pdf]
  - Imágenes: [foto_negocio.jpg]

Output:
  - Análisis crediticio
  - Validación de documentos
  - Riesgos identificados
  - Recomendación
  - Confianza: 85%
```

---

**Última actualización**: 21 de Octubre, 2025  
**Versión**: 2.0 - Sistema Avanzado con Feedback

