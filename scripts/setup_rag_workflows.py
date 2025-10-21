"""
Setup RAG Workflows - Script interactivo para crear workflows RAG en n8n
Autor: AI Assistant
Fecha: 2025-10-21
"""

import json
import sys
import os

# Agregar el directorio scripts al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from n8n_manager import N8nManager, create_rag_ingestion_workflow, create_rag_query_workflow


def create_complete_rag_ingestion_workflow():
    """Crear workflow completo de ingesta con todos los pasos"""
    return {
        "name": "RAG - Ingesta Completa de Documentos",
        "nodes": [
            # 1. Webhook para recibir documento
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "rag/ingest",
                    "responseMode": "responseNode",
                    "options": {
                        "rawBody": False
                    }
                },
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1.1,
                "position": [240, 400],
                "id": "webhook-ingest",
                "name": "📥 Recibir Documento"
            },
            
            # 2. Validar input
            {
                "parameters": {
                    "jsCode": "// Validar que el documento tenga los campos necesarios\nconst items = $input.all();\nconst output = [];\n\nfor (const item of items) {\n  const errors = [];\n  \n  // Validar campos requeridos\n  if (!item.json.filename) errors.push('filename requerido');\n  if (!item.json.file_base64 && !item.binary) errors.push('archivo requerido');\n  \n  if (errors.length > 0) {\n    throw new Error('Validación fallida: ' + errors.join(', '));\n  }\n  \n  // Extraer metadata adicional\n  const metadata = {\n    department: item.json.department || 'general',\n    document_type: item.json.document_type || 'unknown',\n    tags: item.json.tags || [],\n    uploaded_by: item.json.uploaded_by || 'system'\n  };\n  \n  output.push({\n    json: {\n      ...item.json,\n      metadata: metadata,\n      received_at: new Date().toISOString()\n    },\n    binary: item.binary\n  });\n}\n\nreturn output;"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [460, 400],
                "id": "validate-input",
                "name": "✅ Validar Input"
            },
            
            # 3. Calcular hash
            {
                "parameters": {
                    "jsCode": "// Calcular hash SHA-256 del documento\nconst crypto = require('crypto');\nconst items = $input.all();\nconst output = [];\n\nfor (const item of items) {\n  let buffer;\n  \n  if (item.binary && item.binary.data) {\n    buffer = Buffer.from(item.binary.data.data);\n  } else if (item.json.file_base64) {\n    buffer = Buffer.from(item.json.file_base64, 'base64');\n  } else {\n    throw new Error('No se encontró el archivo');\n  }\n  \n  const hash = crypto.createHash('sha256').update(buffer).digest('hex');\n  const documentId = `doc_${hash.substring(0, 16)}`;\n  \n  output.push({\n    json: {\n      ...item.json,\n      document_hash: hash,\n      document_id: documentId,\n      file_size: buffer.length\n    },\n    binary: item.binary\n  });\n}\n\nreturn output;"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 400],
                "id": "calc-hash",
                "name": "🔐 Calcular Hash"
            },
            
            # 4. Verificar duplicados (placeholder - requiere Cosmos DB)
            {
                "parameters": {
                    "jsCode": "// En producción, aquí se consulta Cosmos DB para verificar duplicados\n// Por ahora, asumimos que no hay duplicados\nconst items = $input.all();\nreturn items.map(item => ({\n  json: {\n    ...item.json,\n    is_duplicate: false,\n    checked_duplicates: true\n  },\n  binary: item.binary\n}));"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [900, 400],
                "id": "check-duplicates",
                "name": "🔍 Verificar Duplicados"
            },
            
            # 5. Extraer texto del documento
            {
                "parameters": {
                    "jsCode": "// Extracción de texto - en producción usar Azure Document Intelligence\n// Este es un placeholder que simula la extracción\nconst items = $input.all();\nconst output = [];\n\nfor (const item of items) {\n  // Simular extracción de texto\n  const extractedText = `Texto extraído del documento ${item.json.filename}.\\n\\nEste es un contenido de ejemplo que en producción vendría de Azure Document Intelligence (Form Recognizer) o de una librería de procesamiento de PDFs.\\n\\nEl documento contiene información importante que será indexada en el sistema RAG.`;\n  \n  output.push({\n    json: {\n      ...item.json,\n      extracted_text: extractedText,\n      extraction_method: 'placeholder',\n      extraction_timestamp: new Date().toISOString(),\n      char_count: extractedText.length\n    },\n    binary: item.binary\n  });\n}\n\nreturn output;"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1120, 400],
                "id": "extract-text",
                "name": "📄 Extraer Texto"
            },
            
            # 6. Dividir en chunks
            {
                "parameters": {
                    "jsCode": "// Dividir texto en chunks con overlap\nconst items = $input.all();\nconst output = [];\n\nconst CHUNK_SIZE = 500; // caracteres\nconst OVERLAP = 50;\n\nfor (const item of items) {\n  const text = item.json.extracted_text;\n  const chunks = [];\n  \n  let start = 0;\n  let chunkIndex = 0;\n  \n  while (start < text.length) {\n    const end = Math.min(start + CHUNK_SIZE, text.length);\n    const chunkText = text.substring(start, end);\n    \n    // Crear un chunk por cada fragmento\n    output.push({\n      json: {\n        document_id: item.json.document_id,\n        chunk_id: `${item.json.document_id}_chunk_${chunkIndex}`,\n        chunk_index: chunkIndex,\n        chunk_text: chunkText,\n        filename: item.json.filename,\n        metadata: item.json.metadata,\n        document_hash: item.json.document_hash,\n        total_chunks: Math.ceil(text.length / (CHUNK_SIZE - OVERLAP))\n      }\n    });\n    \n    start = end - OVERLAP;\n    chunkIndex++;\n  }\n}\n\nreturn output;"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1340, 400],
                "id": "split-chunks",
                "name": "✂️ Dividir en Chunks"
            },
            
            # 7. Mensaje de éxito (agregador)
            {
                "parameters": {
                    "jsCode": "// Agregar información de todos los chunks procesados\nconst items = $input.all();\n\nif (items.length === 0) {\n  return [{ json: { success: false, message: 'No se generaron chunks' } }];\n}\n\nconst documentId = items[0].json.document_id;\nconst filename = items[0].json.filename;\nconst totalChunks = items.length;\n\nreturn [{\n  json: {\n    success: true,\n    message: 'Documento procesado exitosamente',\n    document_id: documentId,\n    filename: filename,\n    chunks_generated: totalChunks,\n    status: 'ready_for_embedding',\n    timestamp: new Date().toISOString()\n  }\n}];"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1560, 400],
                "id": "aggregate-result",
                "name": "📊 Agregar Resultado"
            },
            
            # 8. Responder al webhook
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ $json }}"
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [1780, 400],
                "id": "respond",
                "name": "✅ Responder"
            }
        ],
        "connections": {
            "📥 Recibir Documento": {
                "main": [[{"node": "✅ Validar Input", "type": "main", "index": 0}]]
            },
            "✅ Validar Input": {
                "main": [[{"node": "🔐 Calcular Hash", "type": "main", "index": 0}]]
            },
            "🔐 Calcular Hash": {
                "main": [[{"node": "🔍 Verificar Duplicados", "type": "main", "index": 0}]]
            },
            "🔍 Verificar Duplicados": {
                "main": [[{"node": "📄 Extraer Texto", "type": "main", "index": 0}]]
            },
            "📄 Extraer Texto": {
                "main": [[{"node": "✂️ Dividir en Chunks", "type": "main", "index": 0}]]
            },
            "✂️ Dividir en Chunks": {
                "main": [[{"node": "📊 Agregar Resultado", "type": "main", "index": 0}]]
            },
            "📊 Agregar Resultado": {
                "main": [[{"node": "✅ Responder", "type": "main", "index": 0}]]
            }
        },
        "active": False,
        "settings": {
            "executionOrder": "v1"
        }
    }


def create_rag_delete_workflow():
    """Crear workflow para eliminación de documentos"""
    return {
        "name": "RAG - Eliminar Documento",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "DELETE",
                    "path": "rag/document",
                    "responseMode": "responseNode",
                    "options": {}
                },
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1.1,
                "position": [240, 300],
                "id": "webhook-delete",
                "name": "🗑️ Solicitud de Eliminación"
            },
            {
                "parameters": {
                    "jsCode": "// Validar que se proporcione document_id\nconst items = $input.all();\n\nfor (const item of items) {\n  if (!item.json.document_id) {\n    throw new Error('document_id es requerido');\n  }\n}\n\nreturn items;"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [460, 300],
                "id": "validate-delete",
                "name": "✅ Validar"
            },
            {
                "parameters": {
                    "jsCode": "// Placeholder para obtener metadata del documento\n// En producción, consultar Cosmos DB\nconst items = $input.all();\nconst output = [];\n\nfor (const item of items) {\n  // Simular metadata del documento\n  const metadata = {\n    document_id: item.json.document_id,\n    filename: 'documento_ejemplo.pdf',\n    chunk_ids: [\n      `${item.json.document_id}_chunk_0`,\n      `${item.json.document_id}_chunk_1`,\n      `${item.json.document_id}_chunk_2`\n    ],\n    blob_url: `https://storage.azure.com/raw-documents/${item.json.document_id}.pdf`\n  };\n  \n  output.push({\n    json: {\n      ...item.json,\n      metadata: metadata,\n      chunks_to_delete: metadata.chunk_ids.length\n    }\n  });\n}\n\nreturn output;"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 300],
                "id": "get-metadata",
                "name": "📋 Obtener Metadata"
            },
            {
                "parameters": {
                    "jsCode": "// Simular eliminación de chunks del índice de búsqueda\n// En producción, usar Azure AI Search API\nconst items = $input.all();\nconst output = [];\n\nfor (const item of items) {\n  output.push({\n    json: {\n      ...item.json,\n      deleted_from_index: true,\n      chunks_deleted: item.json.metadata.chunk_ids.length,\n      deletion_timestamp: new Date().toISOString()\n    }\n  });\n}\n\nreturn output;"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [900, 300],
                "id": "delete-from-index",
                "name": "🗑️ Eliminar del Índice"
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ { \"success\": true, \"document_id\": $json.document_id, \"message\": \"Documento eliminado exitosamente\", \"chunks_deleted\": $json.chunks_deleted } }}"
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [1120, 300],
                "id": "respond-deleted",
                "name": "✅ Confirmar Eliminación"
            }
        ],
        "connections": {
            "🗑️ Solicitud de Eliminación": {
                "main": [[{"node": "✅ Validar", "type": "main", "index": 0}]]
            },
            "✅ Validar": {
                "main": [[{"node": "📋 Obtener Metadata", "type": "main", "index": 0}]]
            },
            "📋 Obtener Metadata": {
                "main": [[{"node": "🗑️ Eliminar del Índice", "type": "main", "index": 0}]]
            },
            "🗑️ Eliminar del Índice": {
                "main": [[{"node": "✅ Confirmar Eliminación", "type": "main", "index": 0}]]
            }
        },
        "active": False,
        "settings": {
            "executionOrder": "v1"
        }
    }


def create_complete_rag_query_workflow():
    """Crear workflow completo de consultas RAG"""
    return {
        "name": "RAG - Sistema de Consultas Completo",
        "nodes": [
            # 1. Webhook
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "rag/query",
                    "responseMode": "responseNode",
                    "options": {}
                },
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1.1,
                "position": [240, 400],
                "id": "webhook-query",
                "name": "❓ Recibir Consulta"
            },
            
            # 2. Validar query
            {
                "parameters": {
                    "jsCode": "const items = $input.all();\n\nfor (const item of items) {\n  if (!item.json.query || item.json.query.trim().length === 0) {\n    throw new Error('La consulta no puede estar vacía');\n  }\n  \n  if (item.json.query.length > 1000) {\n    throw new Error('La consulta es demasiado larga (máximo 1000 caracteres)');\n  }\n}\n\nreturn items.map(item => ({\n  json: {\n    ...item.json,\n    query: item.json.query.trim(),\n    query_timestamp: new Date().toISOString(),\n    query_id: `query_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`\n  }\n}));"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [460, 400],
                "id": "validate-query",
                "name": "✅ Validar Consulta"
            },
            
            # 3. Generar embedding (placeholder)
            {
                "parameters": {
                    "jsCode": "// Placeholder para generar embedding\n// En producción: llamar a Azure OpenAI Embeddings API\nconst items = $input.all();\n\nreturn items.map(item => ({\n  json: {\n    ...item.json,\n    query_embedding: [0.1, 0.2, 0.3], // Embedding simulado\n    embedding_model: 'text-embedding-ada-002',\n    embedding_generated: true\n  }\n}));"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 400],
                "id": "generate-embedding",
                "name": "🧮 Generar Embedding"
            },
            
            # 4. Búsqueda vectorial (placeholder)
            {
                "parameters": {
                    "jsCode": "// Placeholder para búsqueda vectorial\n// En producción: llamar a Azure AI Search\nconst items = $input.all();\nconst output = [];\n\nfor (const item of items) {\n  // Simular resultados de búsqueda\n  const searchResults = [\n    {\n      chunk_id: 'doc_123_chunk_0',\n      content: 'El Banco Caja Social ofrece diversos productos financieros incluyendo cuentas de ahorro, créditos de consumo y tarjetas de crédito.',\n      document_id: 'doc_123',\n      filename: 'productos_banco.pdf',\n      score: 0.92,\n      metadata: { department: 'productos', document_type: 'catalog' }\n    },\n    {\n      chunk_id: 'doc_456_chunk_2',\n      content: 'Los clientes pueden acceder a sus cuentas a través de la banca en línea, aplicación móvil o en nuestras oficinas físicas.',\n      document_id: 'doc_456',\n      filename: 'canales_atencion.pdf',\n      score: 0.87,\n      metadata: { department: 'servicio_cliente', document_type: 'manual' }\n    },\n    {\n      chunk_id: 'doc_789_chunk_1',\n      content: 'El proceso de apertura de cuenta requiere documento de identidad, comprobante de domicilio y firma del contrato de vinculación.',\n      document_id: 'doc_789',\n      filename: 'requisitos_apertura.pdf',\n      score: 0.84,\n      metadata: { department: 'legal', document_type: 'requirements' }\n    }\n  ];\n  \n  output.push({\n    json: {\n      ...item.json,\n      search_results: searchResults,\n      results_count: searchResults.length,\n      search_completed: true\n    }\n  });\n}\n\nreturn output;"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [900, 400],
                "id": "vector-search",
                "name": "🔍 Búsqueda Vectorial"
            },
            
            # 5. Construir contexto
            {
                "parameters": {
                    "jsCode": "const items = $input.all();\nconst output = [];\n\nfor (const item of items) {\n  const results = item.json.search_results;\n  \n  // Construir contexto a partir de los resultados\n  const contextParts = results.map((result, index) => \n    `[Fuente ${index + 1}: ${result.filename}]\\n${result.content}`\n  );\n  \n  const context = contextParts.join('\\n\\n---\\n\\n');\n  \n  // Extraer fuentes únicas\n  const sources = results.map(r => ({\n    document_id: r.document_id,\n    filename: r.filename,\n    score: r.score\n  }));\n  \n  output.push({\n    json: {\n      ...item.json,\n      context: context,\n      sources: sources,\n      context_length: context.length\n    }\n  });\n}\n\nreturn output;"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1120, 400],
                "id": "build-context",
                "name": "📝 Construir Contexto"
            },
            
            # 6. Generar respuesta (placeholder)
            {
                "parameters": {
                    "jsCode": "// Placeholder para generación de respuesta con LLM\n// En producción: llamar a Azure OpenAI GPT-4\nconst items = $input.all();\nconst output = [];\n\nfor (const item of items) {\n  // Simular respuesta del LLM\n  const answer = `Basándome en la información proporcionada, puedo responder a tu consulta \"${item.json.query}\":\\n\\nEl Banco Caja Social ofrece diversos productos y servicios financieros. Los clientes pueden acceder a través de múltiples canales incluyendo banca en línea, aplicación móvil y oficinas físicas. Para abrir una cuenta, se requiere documentación específica incluyendo documento de identidad y comprobante de domicilio.\\n\\nEsta respuesta se basa en ${item.json.sources.length} documentos relevantes del sistema.`;\n  \n  output.push({\n    json: {\n      query_id: item.json.query_id,\n      query: item.json.query,\n      answer: answer,\n      sources: item.json.sources,\n      model: 'gpt-4',\n      timestamp: new Date().toISOString(),\n      processing_time_ms: Math.floor(Math.random() * 2000) + 500\n    }\n  });\n}\n\nreturn output;"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1340, 400],
                "id": "generate-answer",
                "name": "🤖 Generar Respuesta"
            },
            
            # 7. Responder
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ $json }}"
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [1560, 400],
                "id": "respond-answer",
                "name": "✅ Enviar Respuesta"
            }
        ],
        "connections": {
            "❓ Recibir Consulta": {
                "main": [[{"node": "✅ Validar Consulta", "type": "main", "index": 0}]]
            },
            "✅ Validar Consulta": {
                "main": [[{"node": "🧮 Generar Embedding", "type": "main", "index": 0}]]
            },
            "🧮 Generar Embedding": {
                "main": [[{"node": "🔍 Búsqueda Vectorial", "type": "main", "index": 0}]]
            },
            "🔍 Búsqueda Vectorial": {
                "main": [[{"node": "📝 Construir Contexto", "type": "main", "index": 0}]]
            },
            "📝 Construir Contexto": {
                "main": [[{"node": "🤖 Generar Respuesta", "type": "main", "index": 0}]]
            },
            "🤖 Generar Respuesta": {
                "main": [[{"node": "✅ Enviar Respuesta", "type": "main", "index": 0}]]
            }
        },
        "active": False,
        "settings": {
            "executionOrder": "v1"
        }
    }


def main():
    """Función principal"""
    print("\n" + "="*80)
    print("🚀 SETUP DE WORKFLOWS RAG PARA N8N")
    print("="*80)
    
    # Configuración
    N8N_URL = "http://159.203.149.247:5678"
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5NDJjY2UxYS0yNTUzLTRjZmMtODE0Ny1hMGU5ODM2N2VjZTkiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxMDg2ODM5LCJleHAiOjE3NjM2MTQ4MDB9.OpGYJhtqHkZ1sW91PGKY9b5MmSBATsncf938QOMEc-w"
    
    manager = N8nManager(N8N_URL, API_KEY)
    
    print("\n📋 Workflows disponibles para crear:")
    print("\n1. RAG - Ingesta Completa de Documentos")
    print("   └─ Recibe documentos, valida, extrae texto y crea chunks")
    print("\n2. RAG - Sistema de Consultas Completo")
    print("   └─ Recibe preguntas, busca contexto y genera respuestas")
    print("\n3. RAG - Eliminar Documento")
    print("   └─ Elimina documentos del índice de búsqueda")
    print("\n" + "="*80)
    
    print("\n¿Deseas crear los workflows? (s/n): ", end="")
    response = input().strip().lower()
    
    if response == 's':
        print("\n🔨 Creando workflows...")
        
        try:
            # Crear workflow de ingesta
            print("\n1️⃣  Creando workflow de ingesta...", end="")
            ingestion_wf = create_complete_rag_ingestion_workflow()
            result1 = manager.create_workflow(ingestion_wf)
            print(f" ✅ Creado - ID: {result1['id']}")
            
            # Crear workflow de consultas
            print("2️⃣  Creando workflow de consultas...", end="")
            query_wf = create_complete_rag_query_workflow()
            result2 = manager.create_workflow(query_wf)
            print(f" ✅ Creado - ID: {result2['id']}")
            
            # Crear workflow de eliminación
            print("3️⃣  Creando workflow de eliminación...", end="")
            delete_wf = create_rag_delete_workflow()
            result3 = manager.create_workflow(delete_wf)
            print(f" ✅ Creado - ID: {result3['id']}")
            
            print("\n" + "="*80)
            print("✅ WORKFLOWS CREADOS EXITOSAMENTE")
            print("="*80)
            print("\n📌 Próximos pasos:")
            print("\n1. Accede a tu n8n: http://159.203.149.247:5678")
            print("2. Revisa los workflows creados")
            print("3. Configura las credenciales de Azure")
            print("4. Activa los workflows cuando estés listo")
            print("\n💡 Los workflows están configurados con placeholders.")
            print("   Deberás reemplazar los nodos simulados con llamadas reales a:")
            print("   - Azure OpenAI (embeddings y GPT-4)")
            print("   - Azure AI Search (búsqueda vectorial)")
            print("   - Azure Cosmos DB (metadata)")
            print("   - Azure Blob Storage (almacenamiento)")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nVerifica que:")
            print("- Tu servidor n8n esté accesible")
            print("- La API key sea válida")
            print("- Tengas permisos para crear workflows")
    else:
        print("\n❌ Operación cancelada")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()

