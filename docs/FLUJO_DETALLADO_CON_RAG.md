# 🔍 Flujo Detallado: Cómo se Usa el RAG en el Proceso

## ❓ Tu Pregunta
> "¿En qué punto hace la validación contra el RAG?"

**Ejemplo concreto**:
```
Entrada: historia_usuario.docx + "Ayúdame a refinar la historia de usuario"
RAG tiene: Formato y ejemplos de historias de usuario indexados
Salida esperada: Historia refinada usando AMBOS
```

---

## 🎯 Respuesta: La Búsqueda en el RAG Ocurre en el NODO 4

```
┌─────────────────────────────────────────────────────────────┐
│  FLUJO COMPLETO CON BÚSQUEDA EN RAG                         │
└─────────────────────────────────────────────────────────────┘

NODO 1: Recibir Entrada
   ↓
   • Pregunta: "Ayúdame a refinar la historia de usuario"
   • Documento: historia_usuario.docx

NODO 2: Procesar Documento del Usuario
   ↓
   • Extraer texto de historia_usuario.docx
   • Dividir en chunks
   • Generar embeddings
   • Resultado: Historia actual del usuario procesada

NODO 3: Generar Embedding de la Pregunta
   ↓
   • Embedding de: "Ayúdame a refinar la historia de usuario"

NODO 4: ⭐ BUSCAR EN EL RAG (AQUÍ SE USA LA INFO INDEXADA) ⭐
   ↓
   • Buscar en Azure AI Search con el embedding de la pregunta
   • Query al índice: "formato historias de usuario", "ejemplos"
   • Resultado del RAG:
     ├─ plantilla_historias_usuario.pdf (indexado)
     ├─ ejemplos_historias_buenas.pdf (indexado)
     └─ guia_scrum.pdf (indexado)

NODO 5: Construir Contexto COMBINADO
   ↓
   • PARTE 1: Historia actual del usuario (del documento subido)
   • PARTE 2: Formato y ejemplos del RAG (docs indexados)
   • = CONTEXTO COMPLETO

NODO 6: GPT-4 Genera Respuesta
   ↓
   • Usa AMBOS contextos
   • Compara historia actual con formato correcto
   • Aplica ejemplos del RAG
   • Genera historia refinada

NODO 7: Entregar Resultado
   ↓
   • Historia de usuario refinada
   • Explicación de cambios
   • Referencias al formato/ejemplos usados
```

---

## 📝 Ejemplo Específico: Refinar Historia de Usuario

### Entrada del Usuario

**Documento subido** (`historia_usuario.docx`):
```
Como usuario quiero poder loguearme para usar el sistema
```

**Pregunta**:
```
"Ayúdame a refinar esta historia de usuario según las mejores prácticas"
```

---

### NODO 2: Procesar Documento del Usuario

```javascript
// Extraer texto del documento subido
const userDocument = extractText(historia_usuario.docx);

// Resultado:
{
  filename: "historia_usuario.docx",
  content: "Como usuario quiero poder loguearme para usar el sistema",
  source: "user_provided"
}
```

---

### NODO 3: Generar Embedding de la Pregunta

```javascript
// Crear embedding de la pregunta
const queryEmbedding = await generateEmbedding(
  "Ayúdame a refinar esta historia de usuario según las mejores prácticas"
);

// Este embedding se usa para buscar en el RAG
```

---

### NODO 4: ⭐ BUSCAR EN EL RAG ⭐

**Este es el MOMENTO CLAVE donde se consulta la información indexada**

```javascript
// Buscar en Azure AI Search usando el embedding
const ragResults = await searchAzureAISearch({
  query_embedding: queryEmbedding,
  index: "rag-documents",
  filters: {
    // Opcional: filtrar por tipo de documento
    document_type: ["template", "guide", "example"]
  },
  top_k: 5
});

// RESULTADO DEL RAG (documentos indexados previamente):
[
  {
    filename: "plantilla_historias_usuario.pdf",
    content: `FORMATO DE HISTORIA DE USUARIO:
    
    Como [tipo de usuario]
    Quiero [objetivo/acción]
    Para [beneficio/razón]
    
    Criterios de Aceptación:
    - Dado [contexto inicial]
    - Cuando [acción]
    - Entonces [resultado esperado]`,
    score: 0.92,
    source: "indexed_document"
  },
  {
    filename: "ejemplos_historias_buenas.pdf",
    content: `EJEMPLO 1:
    Como usuario registrado
    Quiero autenticarme mediante correo y contraseña
    Para acceder de forma segura a mi cuenta
    
    Criterios de Aceptación:
    - Dado que soy un usuario registrado
    - Cuando ingreso credenciales correctas
    - Entonces accedo al dashboard principal
    - Y veo un mensaje de bienvenida
    
    - Dado que ingreso credenciales incorrectas
    - Cuando intento autenticarme
    - Entonces veo un mensaje de error
    - Y puedo intentar de nuevo`,
    score: 0.88,
    source: "indexed_document"
  },
  {
    filename: "guia_scrum_banco.pdf",
    content: `Todas las historias de usuario deben:
    1. Ser específicas y medibles
    2. Incluir criterios de aceptación claros
    3. Definir el valor para el usuario
    4. Ser estimables en puntos de historia`,
    score: 0.85,
    source: "indexed_document"
  }
]
```

**HTTP Request Real al RAG**:
```http
POST https://bancosocial.search.windows.net/indexes/rag-documents/docs/search?api-version=2023-11-01

Headers:
  api-key: <AZURE_SEARCH_KEY>

Body:
{
  "search": "*",
  "vectorQueries": [
    {
      "kind": "vector",
      "vector": [0.123, 0.456, ...],  // embedding de la pregunta
      "fields": "content_vector",
      "k": 5
    }
  ],
  "select": "content, filename, metadata, document_type",
  "filter": "document_type eq 'template' or document_type eq 'guide'",
  "top": 5
}
```

---

### NODO 5: Construir Contexto COMBINADO

**Este nodo combina TODO**:

```javascript
// Combinar documento del usuario + resultados del RAG
const fullContext = buildContext({
  userDocument: userDocument,
  ragResults: ragResults,
  query: query
});

// CONTEXTO COMPLETO PARA GPT-4:
const context = `
=== HISTORIA DE USUARIO ACTUAL (Proporcionada por el usuario) ===

Archivo: historia_usuario.docx
Contenido:
"Como usuario quiero poder loguearme para usar el sistema"

---

=== FORMATO CORRECTO (Del RAG - plantilla_historias_usuario.pdf) ===

FORMATO DE HISTORIA DE USUARIO:

Como [tipo de usuario]
Quiero [objetivo/acción]
Para [beneficio/razón]

Criterios de Aceptación:
- Dado [contexto inicial]
- Cuando [acción]
- Entonces [resultado esperado]

---

=== EJEMPLO DE BUENA PRÁCTICA (Del RAG - ejemplos_historias_buenas.pdf) ===

EJEMPLO 1:
Como usuario registrado
Quiero autenticarme mediante correo y contraseña
Para acceder de forma segura a mi cuenta

Criterios de Aceptación:
- Dado que soy un usuario registrado
- Cuando ingreso credenciales correctas
- Entonces accedo al dashboard principal
- Y veo un mensaje de bienvenida

- Dado que ingreso credenciales incorrectas
- Cuando intento autenticarme
- Entonces veo un mensaje de error
- Y puedo intentar de nuevo

---

=== GUÍA DEL BANCO (Del RAG - guia_scrum_banco.pdf) ===

Todas las historias de usuario deben:
1. Ser específicas y medibles
2. Incluir criterios de aceptación claros
3. Definir el valor para el usuario
4. Ser estimables en puntos de historia
`;
```

---

### NODO 6: GPT-4 Genera Respuesta

**Prompt completo a GPT-4**:

```javascript
const systemPrompt = `Eres un experto en Scrum y refinamiento de historias de usuario del Banco Caja Social.

Tu tarea es:
1. Analizar la historia de usuario proporcionada
2. Compararla con el formato correcto y ejemplos
3. Refinarla siguiendo las mejores prácticas
4. Explicar los cambios realizados

Debes usar:
- El FORMATO correcto del RAG
- Los EJEMPLOS del RAG como referencia
- Las GUÍAS del banco`;

const userPrompt = `${context}

TAREA:
Refina la historia de usuario actual siguiendo el formato correcto, 
los ejemplos y las guías del banco. Explica cada cambio.

RESPONDE EN FORMATO JSON:
{
  "historia_original": "...",
  "historia_refinada": "...",
  "cambios_realizados": ["cambio 1", "cambio 2", ...],
  "justificacion": "...",
  "fuentes_usadas": ["plantilla X", "ejemplo Y", ...]
}`;

// Llamar a GPT-4
const response = await callGPT4(systemPrompt, userPrompt);
```

---

### NODO 7: Resultado Final

**Salida para el usuario**:

```json
{
  "query_id": "query_123456",
  "answer": {
    "main_response": "He refinado tu historia de usuario siguiendo el formato estándar del banco y las mejores prácticas de Scrum.",
    
    "historia_original": "Como usuario quiero poder loguearme para usar el sistema",
    
    "historia_refinada": `
    Como usuario registrado del Banco Caja Social
    Quiero autenticarme mediante correo electrónico y contraseña
    Para acceder de forma segura a mi cuenta y realizar operaciones bancarias
    
    Criterios de Aceptación:
    
    Escenario 1: Autenticación exitosa
    - Dado que soy un usuario registrado con cuenta activa
    - Cuando ingreso mi correo y contraseña correctos
    - Entonces accedo al dashboard principal
    - Y veo un mensaje de bienvenida con mi nombre
    - Y puedo ver el resumen de mis productos bancarios
    
    Escenario 2: Autenticación fallida
    - Dado que soy un usuario registrado
    - Cuando ingreso credenciales incorrectas
    - Entonces veo un mensaje de error claro
    - Y tengo la opción de recuperar mi contraseña
    - Y se registra el intento fallido por seguridad
    
    Escenario 3: Bloqueo por seguridad
    - Dado que he fallado 3 intentos de autenticación
    - Cuando intento ingresar nuevamente
    - Entonces mi cuenta se bloquea temporalmente
    - Y recibo un correo de notificación
    
    Definición de Terminado (DoD):
    - Código revisado por pares
    - Pruebas unitarias implementadas (cobertura >80%)
    - Pruebas de seguridad realizadas
    - Documentación actualizada
    
    Estimación: 5 puntos de historia
    `,
    
    "cambios_realizados": [
      "✅ Especificado tipo de usuario: 'usuario registrado del Banco Caja Social'",
      "✅ Detallado el objetivo: 'autenticarme mediante correo electrónico y contraseña'",
      "✅ Agregado el beneficio: 'Para acceder de forma segura y realizar operaciones'",
      "✅ Incluidos Criterios de Aceptación con formato Dado-Cuando-Entonces",
      "✅ Agregados múltiples escenarios (éxito, fallo, bloqueo)",
      "✅ Incluida Definición de Terminado",
      "✅ Agregada estimación en puntos"
    ],
    
    "justificacion": `Los cambios se realizaron siguiendo:
    
    1. FORMATO del documento 'plantilla_historias_usuario.pdf' (RAG)
       → Estructura Como-Quiero-Para completa
    
    2. EJEMPLOS del documento 'ejemplos_historias_buenas.pdf' (RAG)
       → Múltiples escenarios con Dado-Cuando-Entonces
    
    3. GUÍAS del documento 'guia_scrum_banco.pdf' (RAG)
       → Específica, medible, con criterios claros
    
    La historia original era muy vaga. La refinada es:
    - Más específica (usuario registrado, no solo 'usuario')
    - Medible (criterios de aceptación claros)
    - Con valor claro (seguridad y operaciones bancarias)
    - Estimable (5 puntos)`,
    
    "fuentes_usadas": [
      {
        "filename": "plantilla_historias_usuario.pdf",
        "tipo": "formato",
        "relevancia": "alta",
        "source": "rag_indexado"
      },
      {
        "filename": "ejemplos_historias_buenas.pdf",
        "tipo": "ejemplos",
        "relevancia": "alta",
        "source": "rag_indexado"
      },
      {
        "filename": "guia_scrum_banco.pdf",
        "tipo": "guía",
        "relevancia": "media",
        "source": "rag_indexado"
      }
    ],
    
    "confidence": 95,
    "processing_time_ms": 8543
  }
}
```

---

## 🔑 Puntos Clave

### 1. El RAG se Consulta en el NODO 4

```javascript
// NODO 4: Búsqueda Vectorial en el RAG
const ragResults = await searchInRAG(queryEmbedding);
```

### 2. Se Combinan AMBAS Fuentes

```
Documento del Usuario (subido)
         +
Documentos del RAG (indexados)
         =
CONTEXTO COMPLETO para GPT-4
```

### 3. GPT-4 Usa AMBOS

```
GPT-4 ve:
• Historia actual (del doc subido)
• Formato correcto (del RAG)
• Ejemplos (del RAG)
• Guías (del RAG)

→ Genera historia refinada
```

---

## 📊 Diagrama Visual Completo

```
┌──────────────────────────────────────────────────────────────┐
│ USUARIO                                                       │
│ Sube: historia_usuario.docx                                  │
│ Pregunta: "Refina esta historia de usuario"                 │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│ NODO 2: PROCESAR DOCUMENTO DEL USUARIO                       │
├───────────────────────────────────────────────────────────────┤
│ • Extraer: "Como usuario quiero loguearme..."                │
│ • Chunks: [chunk1, chunk2, ...]                              │
│ • Embeddings: [emb1, emb2, ...]                              │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│ NODO 3: EMBEDDING DE LA PREGUNTA                             │
├───────────────────────────────────────────────────────────────┤
│ • "Refina esta historia..." → [0.123, 0.456, ...]           │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│ ⭐ NODO 4: BUSCAR EN EL RAG (DOCUMENTOS INDEXADOS) ⭐       │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Azure AI Search Query:                                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Búsqueda vectorial con embedding de pregunta          │  │
│  │ Índice: "rag-documents"                                │  │
│  │ Top K: 5                                               │  │
│  └────────────────────────────────────────────────────────┘  │
│                         ↓                                     │
│  Resultados del RAG (docs indexados):                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 1. plantilla_historias_usuario.pdf (score: 0.92)      │  │
│  │    "FORMATO: Como [usuario] Quiero [acción]..."      │  │
│  │                                                         │  │
│  │ 2. ejemplos_historias_buenas.pdf (score: 0.88)       │  │
│  │    "EJEMPLO: Como usuario registrado..."              │  │
│  │                                                         │  │
│  │ 3. guia_scrum_banco.pdf (score: 0.85)                │  │
│  │    "Deben incluir criterios de aceptación..."         │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│ NODO 5: CONSTRUIR CONTEXTO COMBINADO                         │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  CONTEXTO = {                                                 │
│    "historia_usuario_actual": {                               │
│       content: "Como usuario quiero loguearme...",           │
│       source: "user_document"                                 │
│    },                                                         │
│    "formato_correcto": {                                      │
│       content: "Como [tipo] Quiero [acción] Para...",       │
│       source: "rag_indexado",                                │
│       filename: "plantilla_historias_usuario.pdf"            │
│    },                                                         │
│    "ejemplos": {                                              │
│       content: "Como usuario registrado...",                 │
│       source: "rag_indexado",                                │
│       filename: "ejemplos_historias_buenas.pdf"              │
│    },                                                         │
│    "guias": {                                                 │
│       content: "Deben ser específicas...",                   │
│       source: "rag_indexado",                                │
│       filename: "guia_scrum_banco.pdf"                       │
│    }                                                          │
│  }                                                            │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│ NODO 6: GPT-4 GENERA RESPUESTA                               │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Prompt a GPT-4:                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ System: "Eres experto en refinar historias de usuario"│  │
│  │                                                         │  │
│  │ User: "HISTORIA ACTUAL:                                │  │
│  │        Como usuario quiero loguearme...                │  │
│  │                                                         │  │
│  │        FORMATO CORRECTO (del RAG):                     │  │
│  │        Como [tipo] Quiero [acción] Para [beneficio]   │  │
│  │                                                         │  │
│  │        EJEMPLOS (del RAG):                             │  │
│  │        Como usuario registrado quiero...               │  │
│  │                                                         │  │
│  │        GUÍAS (del RAG):                                │  │
│  │        Debe ser específica y medible...                │  │
│  │                                                         │  │
│  │        TAREA: Refina la historia usando todo esto"     │  │
│  └────────────────────────────────────────────────────────┘  │
│                         ↓                                     │
│  GPT-4 Responde:                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Historia refinada:                                      │  │
│  │ "Como usuario registrado del Banco                      │  │
│  │  Quiero autenticarme mediante correo y contraseña      │  │
│  │  Para acceder de forma segura...                       │  │
│  │                                                         │  │
│  │  Criterios de Aceptación:                              │  │
│  │  - Dado que soy usuario registrado...                  │  │
│  │  - Cuando ingreso credenciales...                      │  │
│  │  - Entonces accedo al dashboard..."                    │  │
│  │                                                         │  │
│  │ Fuentes usadas:                                         │  │
│  │  - plantilla_historias_usuario.pdf (formato)           │  │
│  │  - ejemplos_historias_buenas.pdf (referencia)          │  │
│  │  - guia_scrum_banco.pdf (validación)                   │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│ SALIDA AL USUARIO                                             │
├───────────────────────────────────────────────────────────────┤
│ • Historia refinada                                           │
│ • Explicación de cambios                                      │
│ • Fuentes del RAG usadas                                      │
│ • Confianza: 95%                                              │
└───────────────────────────────────────────────────────────────┘
```

---

## 💡 Otros Ejemplos con RAG

### Ejemplo 2: Revisar Contrato

```
Entrada:
  • Documento: contrato_cliente.pdf
  • Pregunta: "¿Este contrato cumple con nuestras políticas?"

NODO 4 busca en RAG:
  → politicas_contratos_2025.pdf
  → requisitos_legales.pdf
  → clausulas_obligatorias.pdf

GPT-4 compara:
  • Contrato del cliente (documento subido)
  • VS Políticas del banco (del RAG)
  
Salida:
  • ✅ Cumple con 8 de 10 requisitos
  • ❌ Falta cláusula de garantías
  • ⚠️  Plazo excede el límite (60 vs 36 meses)
```

### Ejemplo 3: Validar Factura

```
Entrada:
  • Documento: factura.pdf
  • Pregunta: "¿Esta factura es correcta?"

NODO 4 busca en RAG:
  → tarifario_servicios_2025.pdf
  → formato_facturas_validas.pdf
  → impuestos_aplicables.pdf

GPT-4 compara:
  • Factura actual (documento subido)
  • VS Tarifas correctas (del RAG)
  
Salida:
  • ✅ Formato correcto
  • ❌ Tarifa incorrecta: $150 vs $120 (del tarifario)
  • ✅ Impuestos bien calculados
```

---

## 🔧 Código del Nodo 4 Completo

```javascript
/**
 * NODO 4: Búsqueda en el RAG
 * Este es el nodo donde se consultan los documentos indexados
 */

// Input del nodo anterior
const queryEmbedding = $json.query_embedding;  // Del NODO 3
const query = $json.query;                     // Pregunta original
const options = $json.options;                 // Opciones

// Solo buscar en RAG si está habilitado
if (!options.use_indexed_docs) {
  return [$json];  // Skip, no usar RAG
}

// BÚSQUEDA EN AZURE AI SEARCH (EL RAG)
const searchUrl = `${process.env.AZURE_SEARCH_ENDPOINT}/indexes/${process.env.AZURE_SEARCH_INDEX}/docs/search?api-version=2023-11-01`;

const searchPayload = {
  "search": "*",
  "vectorQueries": [
    {
      "kind": "vector",
      "vector": queryEmbedding,  // Embedding de la pregunta
      "fields": "content_vector",
      "k": options.max_sources || 5
    }
  ],
  "select": "id, content, filename, metadata, document_type",
  "top": options.max_sources || 5
};

// Hacer request a Azure AI Search
const response = await fetch(searchUrl, {
  method: 'POST',
  headers: {
    'api-key': process.env.AZURE_SEARCH_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(searchPayload)
});

const searchResults = await response.json();

// RESULTADO: Documentos del RAG encontrados
const ragDocuments = searchResults.value.map(doc => ({
  id: doc.id,
  filename: doc.filename,
  content: doc.content,
  score: doc['@search.score'],
  metadata: doc.metadata,
  document_type: doc.document_type,
  source: 'rag_indexado'  // Importante: marcar como del RAG
}));

// Pasar al siguiente nodo con los resultados del RAG
return [{
  json: {
    ...$json,
    rag_documents: ragDocuments,  // ← Aquí están los docs del RAG
    rag_search_completed: true,
    rag_documents_count: ragDocuments.length
  }
}];
```

---

## ✅ Resumen de Tu Pregunta

**Tu pregunta**: ¿Dónde se valida contra el RAG?

**Respuesta**:
1. ⭐ **NODO 4**: Se busca en el RAG (Azure AI Search)
2. **NODO 5**: Se combina documento subido + resultados del RAG
3. **NODO 6**: GPT-4 usa AMBOS para generar la respuesta

**En tu ejemplo**:
- Subes: `historia_usuario.docx`
- RAG tiene: Formato y ejemplos indexados
- **NODO 4** busca en el RAG: "formato historias", "ejemplos"
- **NODO 5** combina: historia actual + formato/ejemplos del RAG
- **NODO 6** GPT-4 genera: Historia refinada usando ambos

**Clave**: El RAG NO se usa para "validar", se usa para **ENRIQUECER** el contexto. GPT-4 recibe:
- Lo que el usuario subió
- +
- Lo que el RAG tiene indexado
- =
- Respuesta que usa AMBAS fuentes

---

**¿Quedó claro? El punto clave es el NODO 4 donde se hace la búsqueda vectorial en Azure AI Search (el RAG).**

