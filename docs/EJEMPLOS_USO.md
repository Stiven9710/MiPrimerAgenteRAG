# 📚 Ejemplos de Uso - Sistema RAG

## Tabla de Contenidos
1. [Ingesta de Documentos](#ingesta-de-documentos)
2. [Consultas RAG](#consultas-rag)
3. [Eliminación de Documentos](#eliminación-de-documentos)
4. [Integración con Aplicaciones](#integración-con-aplicaciones)

---

## 1. Ingesta de Documentos

### 🔹 Con cURL

```bash
# Ingestar un documento desde archivo
curl -X POST http://159.203.149.247:5678/webhook/rag/ingest \
  -H "Content-Type: application/json" \
  -d @- << EOF
{
  "filename": "manual_productos.pdf",
  "file_base64": "$(base64 -i manual_productos.pdf)",
  "department": "productos",
  "document_type": "manual",
  "tags": ["productos", "creditos", "tarjetas"],
  "uploaded_by": "juan.perez@banco.com"
}
EOF
```

### 🔹 Con Python

```python
import base64
import requests

def ingest_document(filepath, metadata=None):
    """
    Ingestar un documento en el sistema RAG
    
    Args:
        filepath: Ruta al archivo
        metadata: Diccionario con metadata adicional
    """
    # Leer y codificar archivo
    with open(filepath, 'rb') as f:
        file_content = base64.b64encode(f.read()).decode('utf-8')
    
    # Preparar payload
    payload = {
        "filename": filepath.split('/')[-1],
        "file_base64": file_content,
        "department": metadata.get('department', 'general'),
        "document_type": metadata.get('document_type', 'document'),
        "tags": metadata.get('tags', []),
        "uploaded_by": metadata.get('uploaded_by', 'system')
    }
    
    # Enviar request
    response = requests.post(
        'http://159.203.149.247:5678/webhook/rag/ingest',
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Documento ingresado exitosamente")
        print(f"   Document ID: {result['document_id']}")
        print(f"   Chunks generados: {result['chunks_generated']}")
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

# Ejemplo de uso
if __name__ == "__main__":
    result = ingest_document(
        filepath="./documentos/manual_productos.pdf",
        metadata={
            "department": "productos",
            "document_type": "manual",
            "tags": ["productos", "creditos"],
            "uploaded_by": "admin@banco.com"
        }
    )
```

### 🔹 Con JavaScript/Node.js

```javascript
const fs = require('fs');
const axios = require('axios');

async function ingestDocument(filepath, metadata = {}) {
    // Leer y codificar archivo
    const fileBuffer = fs.readFileSync(filepath);
    const base64File = fileBuffer.toString('base64');
    
    // Preparar payload
    const payload = {
        filename: filepath.split('/').pop(),
        file_base64: base64File,
        department: metadata.department || 'general',
        document_type: metadata.document_type || 'document',
        tags: metadata.tags || [],
        uploaded_by: metadata.uploaded_by || 'system'
    };
    
    try {
        const response = await axios.post(
            'http://159.203.149.247:5678/webhook/rag/ingest',
            payload
        );
        
        console.log('✅ Documento ingresado exitosamente');
        console.log(`   Document ID: ${response.data.document_id}`);
        console.log(`   Chunks generados: ${response.data.chunks_generated}`);
        
        return response.data;
    } catch (error) {
        console.error('❌ Error:', error.message);
        return null;
    }
}

// Ejemplo de uso
ingestDocument('./documentos/manual_productos.pdf', {
    department: 'productos',
    document_type: 'manual',
    tags: ['productos', 'creditos'],
    uploaded_by: 'admin@banco.com'
});
```

---

## 2. Consultas RAG

### 🔹 Con cURL

```bash
# Consulta simple
curl -X POST http://159.203.149.247:5678/webhook/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuáles son los requisitos para abrir una cuenta de ahorros?"
  }'

# Consulta con filtros (cuando estén implementados)
curl -X POST http://159.203.149.247:5678/webhook/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué tipos de crédito ofrecen?",
    "filters": {
      "department": "productos",
      "document_type": "catalog"
    },
    "top_k": 3
  }'
```

### 🔹 Con Python

```python
import requests

def query_rag(question, filters=None, top_k=5):
    """
    Consultar el sistema RAG
    
    Args:
        question: Pregunta a responder
        filters: Filtros opcionales
        top_k: Número de resultados a considerar
    """
    payload = {
        "query": question,
        "filters": filters or {},
        "top_k": top_k
    }
    
    response = requests.post(
        'http://159.203.149.247:5678/webhook/rag/query',
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n{'='*80}")
        print(f"Pregunta: {question}")
        print(f"{'='*80}\n")
        print(f"Respuesta:\n{result['answer']}\n")
        print(f"{'='*80}")
        print(f"Fuentes consultadas:")
        for i, source in enumerate(result['sources'], 1):
            print(f"  {i}. {source['filename']} (score: {source.get('score', 'N/A')})")
        print(f"{'='*80}\n")
        
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        return None

# Ejemplos de uso
if __name__ == "__main__":
    # Consulta sobre productos
    query_rag("¿Qué requisitos necesito para solicitar un crédito de vivienda?")
    
    # Consulta sobre servicios
    query_rag("¿Cómo puedo activar mi tarjeta de crédito?")
    
    # Consulta sobre sucursales
    query_rag("¿Cuál es el horario de atención de las oficinas?")
```

### 🔹 Con JavaScript/Node.js

```javascript
const axios = require('axios');

async function queryRAG(question, filters = {}, topK = 5) {
    const payload = {
        query: question,
        filters: filters,
        top_k: topK
    };
    
    try {
        const response = await axios.post(
            'http://159.203.149.247:5678/webhook/rag/query',
            payload
        );
        
        const result = response.data;
        
        console.log('\n' + '='.repeat(80));
        console.log(`Pregunta: ${question}`);
        console.log('='.repeat(80) + '\n');
        console.log(`Respuesta:\n${result.answer}\n`);
        console.log('='.repeat(80));
        console.log('Fuentes consultadas:');
        result.sources.forEach((source, i) => {
            console.log(`  ${i+1}. ${source.filename} (score: ${source.score || 'N/A'})`);
        });
        console.log('='.repeat(80) + '\n');
        
        return result;
    } catch (error) {
        console.error('❌ Error:', error.message);
        return null;
    }
}

// Ejemplos de uso
async function main() {
    await queryRAG('¿Qué productos financieros ofrece el banco?');
    await queryRAG('¿Cuáles son las tasas de interés actuales?');
}

main();
```

### 🔹 Interfaz de Chat Interactiva (Python)

```python
import requests

def chat_rag():
    """Interfaz de chat interactiva con el RAG"""
    print("\n" + "="*80)
    print("💬 CHAT RAG - Banco Caja Social")
    print("="*80)
    print("Escribe 'salir' para terminar\n")
    
    while True:
        # Leer pregunta del usuario
        question = input("🙋 Tu pregunta: ").strip()
        
        if question.lower() in ['salir', 'exit', 'quit']:
            print("\n👋 ¡Hasta luego!")
            break
        
        if not question:
            continue
        
        # Consultar RAG
        try:
            response = requests.post(
                'http://159.203.149.247:5678/webhook/rag/query',
                json={"query": question},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n🤖 Respuesta:\n{result['answer']}\n")
                print(f"📚 Fuentes: {', '.join([s['filename'] for s in result['sources']])}\n")
            else:
                print(f"\n❌ Error {response.status_code}: {response.text}\n")
                
        except Exception as e:
            print(f"\n❌ Error de conexión: {e}\n")

if __name__ == "__main__":
    chat_rag()
```

---

## 3. Eliminación de Documentos

### 🔹 Con cURL

```bash
# Eliminar un documento por ID
curl -X DELETE http://159.203.149.247:5678/webhook/rag/document \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc_abc123def456"
  }'
```

### 🔹 Con Python

```python
import requests

def delete_document(document_id):
    """Eliminar un documento del sistema RAG"""
    response = requests.delete(
        'http://159.203.149.247:5678/webhook/rag/document',
        json={"document_id": document_id}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Documento eliminado exitosamente")
        print(f"   Document ID: {result['document_id']}")
        print(f"   Chunks eliminados: {result['chunks_deleted']}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

# Ejemplo de uso
delete_document("doc_abc123def456")
```

---

## 4. Integración con Aplicaciones

### 🔹 Clase Python Completa

```python
"""
RAG Client - Cliente para interactuar con el sistema RAG
"""

import base64
import requests
from typing import Dict, List, Optional
from pathlib import Path

class RAGClient:
    """Cliente para el sistema RAG del Banco Caja Social"""
    
    def __init__(self, base_url: str = "http://159.203.149.247:5678"):
        self.base_url = base_url.rstrip('/')
        self.ingest_endpoint = f"{self.base_url}/webhook/rag/ingest"
        self.query_endpoint = f"{self.base_url}/webhook/rag/query"
        self.delete_endpoint = f"{self.base_url}/webhook/rag/document"
    
    def ingest_document(
        self, 
        filepath: str, 
        department: str = "general",
        document_type: str = "document",
        tags: List[str] = None,
        uploaded_by: str = "system"
    ) -> Optional[Dict]:
        """Ingestar un documento"""
        
        # Validar que el archivo existe
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")
        
        # Leer y codificar
        with open(filepath, 'rb') as f:
            file_content = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {
            "filename": path.name,
            "file_base64": file_content,
            "department": department,
            "document_type": document_type,
            "tags": tags or [],
            "uploaded_by": uploaded_by
        }
        
        response = requests.post(self.ingest_endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    
    def query(
        self, 
        question: str, 
        filters: Dict = None,
        top_k: int = 5
    ) -> Optional[Dict]:
        """Realizar una consulta"""
        
        payload = {
            "query": question,
            "filters": filters or {},
            "top_k": top_k
        }
        
        response = requests.post(self.query_endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    
    def delete_document(self, document_id: str) -> bool:
        """Eliminar un documento"""
        
        response = requests.delete(
            self.delete_endpoint,
            json={"document_id": document_id}
        )
        response.raise_for_status()
        return True
    
    def batch_ingest(self, directory: str, pattern: str = "*.pdf") -> List[Dict]:
        """Ingestar múltiples documentos desde un directorio"""
        
        results = []
        path = Path(directory)
        
        for file in path.glob(pattern):
            try:
                result = self.ingest_document(str(file))
                results.append({"file": file.name, "status": "success", "data": result})
                print(f"✅ {file.name}")
            except Exception as e:
                results.append({"file": file.name, "status": "error", "error": str(e)})
                print(f"❌ {file.name}: {e}")
        
        return results


# Ejemplo de uso
if __name__ == "__main__":
    client = RAGClient()
    
    # Ingestar documento
    result = client.ingest_document(
        "./documentos/manual.pdf",
        department="productos",
        document_type="manual",
        tags=["productos", "manual"],
        uploaded_by="admin@banco.com"
    )
    print(f"Document ID: {result['document_id']}")
    
    # Hacer consulta
    answer = client.query("¿Qué productos ofrece el banco?")
    print(f"Respuesta: {answer['answer']}")
    
    # Ingestión por lotes
    results = client.batch_ingest("./documentos", "*.pdf")
    print(f"Procesados: {len(results)} archivos")
```

### 🔹 Integración con FastAPI

```python
"""
API REST que expone el sistema RAG
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import base64
import requests

app = FastAPI(title="RAG API - Banco Caja Social")

RAG_BASE_URL = "http://159.203.149.247:5678"

class QueryRequest(BaseModel):
    query: str
    filters: Optional[dict] = {}
    top_k: int = 5

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[dict]
    timestamp: str

@app.post("/api/v1/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    department: str = "general",
    document_type: str = "document",
    uploaded_by: str = "api_user"
):
    """Endpoint para ingestar documentos"""
    
    # Leer archivo
    content = await file.read()
    base64_content = base64.b64encode(content).decode('utf-8')
    
    # Enviar a n8n
    payload = {
        "filename": file.filename,
        "file_base64": base64_content,
        "department": department,
        "document_type": document_type,
        "uploaded_by": uploaded_by
    }
    
    response = requests.post(
        f"{RAG_BASE_URL}/webhook/rag/ingest",
        json=payload
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error procesando documento")
    
    return response.json()

@app.post("/api/v1/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Endpoint para consultas RAG"""
    
    response = requests.post(
        f"{RAG_BASE_URL}/webhook/rag/query",
        json=request.dict()
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error en consulta")
    
    return response.json()

@app.delete("/api/v1/documents/{document_id}")
async def delete_document(document_id: str):
    """Endpoint para eliminar documentos"""
    
    response = requests.delete(
        f"{RAG_BASE_URL}/webhook/rag/document",
        json={"document_id": document_id}
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error eliminando documento")
    
    return {"message": "Documento eliminado exitosamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 🔹 Widget de Chat para Sitio Web (React)

```javascript
import React, { useState } from 'react';
import axios from 'axios';

const RAGChatWidget = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const sendMessage = async () => {
        if (!input.trim()) return;

        // Agregar mensaje del usuario
        const userMessage = { role: 'user', content: input };
        setMessages([...messages, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await axios.post(
                'http://159.203.149.247:5678/webhook/rag/query',
                { query: input }
            );

            // Agregar respuesta del bot
            const botMessage = {
                role: 'assistant',
                content: response.data.answer,
                sources: response.data.sources
            };
            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            console.error('Error:', error);
            const errorMessage = {
                role: 'error',
                content: 'Lo siento, hubo un error procesando tu pregunta.'
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="rag-chat-widget">
            <div className="messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                        <p>{msg.content}</p>
                        {msg.sources && (
                            <div className="sources">
                                <small>Fuentes: {msg.sources.map(s => s.filename).join(', ')}</small>
                            </div>
                        )}
                    </div>
                ))}
                {loading && <div className="loading">Pensando...</div>}
            </div>
            <div className="input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Escribe tu pregunta..."
                />
                <button onClick={sendMessage}>Enviar</button>
            </div>
        </div>
    );
};

export default RAGChatWidget;
```

---

## 📊 Monitoreo y Analytics

### Script de Monitoreo (Python)

```python
import requests
import time
from datetime import datetime

def monitor_rag_health():
    """Monitorear salud del sistema RAG"""
    
    test_query = "test de conectividad"
    
    while True:
        try:
            start = time.time()
            response = requests.post(
                'http://159.203.149.247:5678/webhook/rag/query',
                json={"query": test_query},
                timeout=10
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                print(f"[{datetime.now()}] ✅ Sistema operativo - {elapsed:.2f}s")
            else:
                print(f"[{datetime.now()}] ⚠️  Error {response.status_code}")
                
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Sistema caído - {e}")
        
        time.sleep(60)  # Verificar cada minuto

if __name__ == "__main__":
    monitor_rag_health()
```

---

**Nota:** Asegúrate de reemplazar `http://159.203.149.247:5678` con la URL correcta de tu servidor n8n si es diferente.

