"""
n8n Manager - Script para gestionar workflows en n8n vía API
Autor: AI Assistant
Fecha: 2025-10-21
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

class N8nManager:
    """Clase para gestionar workflows en n8n"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        Inicializar el gestor de n8n
        
        Args:
            base_url: URL base del servidor n8n (ej: http://159.203.149.247:5678)
            api_key: API Key de n8n
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-N8N-API-KEY': api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def list_workflows(self) -> List[Dict]:
        """Listar todos los workflows"""
        response = requests.get(
            f"{self.base_url}/api/v1/workflows",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()['data']
    
    def get_workflow(self, workflow_id: str) -> Dict:
        """Obtener un workflow específico"""
        response = requests.get(
            f"{self.base_url}/api/v1/workflows/{workflow_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_workflow(self, workflow_data: Dict) -> Dict:
        """
        Crear un nuevo workflow
        
        Args:
            workflow_data: Definición del workflow en formato JSON
        """
        response = requests.post(
            f"{self.base_url}/api/v1/workflows",
            headers=self.headers,
            json=workflow_data
        )
        response.raise_for_status()
        return response.json()
    
    def update_workflow(self, workflow_id: str, workflow_data: Dict) -> Dict:
        """Actualizar un workflow existente"""
        response = requests.patch(
            f"{self.base_url}/api/v1/workflows/{workflow_id}",
            headers=self.headers,
            json=workflow_data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Eliminar un workflow"""
        response = requests.delete(
            f"{self.base_url}/api/v1/workflows/{workflow_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return True
    
    def activate_workflow(self, workflow_id: str) -> Dict:
        """Activar un workflow"""
        workflow = self.get_workflow(workflow_id)
        workflow['active'] = True
        return self.update_workflow(workflow_id, workflow)
    
    def deactivate_workflow(self, workflow_id: str) -> Dict:
        """Desactivar un workflow"""
        workflow = self.get_workflow(workflow_id)
        workflow['active'] = False
        return self.update_workflow(workflow_id, workflow)
    
    def execute_workflow(self, workflow_id: str, input_data: Optional[Dict] = None) -> Dict:
        """
        Ejecutar un workflow manualmente
        
        Args:
            workflow_id: ID del workflow
            input_data: Datos de entrada opcionales
        """
        payload = {'workflowId': workflow_id}
        if input_data:
            payload['data'] = input_data
            
        response = requests.post(
            f"{self.base_url}/api/v1/executions",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_execution(self, execution_id: str) -> Dict:
        """Obtener detalles de una ejecución"""
        response = requests.get(
            f"{self.base_url}/api/v1/executions/{execution_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def list_executions(self, workflow_id: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Listar ejecuciones"""
        params = {'limit': limit}
        if workflow_id:
            params['workflowId'] = workflow_id
            
        response = requests.get(
            f"{self.base_url}/api/v1/executions",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()['data']
    
    def export_workflow(self, workflow_id: str, filepath: str):
        """Exportar un workflow a un archivo JSON"""
        workflow = self.get_workflow(workflow_id)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"✅ Workflow exportado a: {filepath}")
    
    def import_workflow(self, filepath: str) -> Dict:
        """Importar un workflow desde un archivo JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        # Remover campos que no se deben enviar en creación
        fields_to_remove = ['id', 'createdAt', 'updatedAt', 'versionId']
        for field in fields_to_remove:
            workflow_data.pop(field, None)
        
        return self.create_workflow(workflow_data)
    
    def print_workflows_summary(self):
        """Imprimir resumen de workflows"""
        workflows = self.list_workflows()
        
        print("\n" + "="*80)
        print(f"📊 RESUMEN DE WORKFLOWS ({len(workflows)} totales)")
        print("="*80)
        
        for wf in workflows:
            status = "🟢 ACTIVO" if wf['active'] else "🔴 INACTIVO"
            print(f"\n{status}")
            print(f"  ID: {wf['id']}")
            print(f"  Nombre: {wf['name']}")
            print(f"  Nodos: {len(wf.get('nodes', []))}")
            print(f"  Creado: {wf['createdAt']}")
            print(f"  Actualizado: {wf['updatedAt']}")
        
        print("\n" + "="*80)


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def create_rag_ingestion_workflow() -> Dict:
    """
    Crear definición del workflow de ingesta de documentos RAG
    
    Returns:
        Diccionario con la definición del workflow
    """
    return {
        "name": "RAG - Ingesta de Documentos",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "ingest-document",
                    "responseMode": "responseNode",
                    "options": {}
                },
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1.1,
                "position": [240, 300],
                "id": "webhook-ingest",
                "name": "Webhook - Recibir Documento",
                "webhookId": ""
            },
            {
                "parameters": {
                    "jsCode": "// Calcular hash del documento para detectar duplicados\nconst crypto = require('crypto');\n\nconst items = $input.all();\nconst output = [];\n\nfor (const item of items) {\n  let hash = '';\n  \n  // Si viene como binary data\n  if (item.binary && item.binary.data) {\n    const buffer = Buffer.from(item.binary.data.data);\n    hash = crypto.createHash('sha256').update(buffer).digest('hex');\n  } \n  // Si viene como base64 string\n  else if (item.json.file_base64) {\n    const buffer = Buffer.from(item.json.file_base64, 'base64');\n    hash = crypto.createHash('sha256').update(buffer).digest('hex');\n  }\n  \n  output.push({\n    json: {\n      ...item.json,\n      document_hash: hash,\n      document_id: `doc_${hash.substring(0, 12)}`,\n      timestamp: new Date().toISOString()\n    },\n    binary: item.binary\n  });\n}\n\nreturn output;"
                },
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [460, 300],
                "id": "code-hash",
                "name": "Calcular Hash"
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "={{ $env.COSMOS_DB_ENDPOINT }}/dbs/{{ $env.COSMOS_DB_DATABASE }}/colls/documents_metadata/docs",
                    "authentication": "genericCredentialType",
                    "genericAuthType": "httpHeaderAuth",
                    "sendHeaders": true,
                    "headerParameters": {
                        "parameters": [
                            {
                                "name": "x-ms-version",
                                "value": "2018-12-31"
                            },
                            {
                                "name": "x-ms-documentdb-is-upsert",
                                "value": "true"
                            }
                        ]
                    },
                    "sendBody": true,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "id",
                                "value": "={{ $json.document_id }}"
                            },
                            {
                                "name": "filename",
                                "value": "={{ $json.filename }}"
                            },
                            {
                                "name": "hash",
                                "value": "={{ $json.document_hash }}"
                            },
                            {
                                "name": "status",
                                "value": "processing"
                            },
                            {
                                "name": "upload_date",
                                "value": "={{ $json.timestamp }}"
                            }
                        ]
                    },
                    "options": {}
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [680, 300],
                "id": "http-cosmos-save",
                "name": "Guardar en Cosmos DB"
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ { \"success\": true, \"document_id\": $json.document_id, \"message\": \"Documento procesado exitosamente\" } }}"
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 300],
                "id": "respond-success",
                "name": "Responder Éxito"
            }
        ],
        "connections": {
            "Webhook - Recibir Documento": {
                "main": [[{"node": "Calcular Hash", "type": "main", "index": 0}]]
            },
            "Calcular Hash": {
                "main": [[{"node": "Guardar en Cosmos DB", "type": "main", "index": 0}]]
            },
            "Guardar en Cosmos DB": {
                "main": [[{"node": "Responder Éxito", "type": "main", "index": 0}]]
            }
        },
        "active": False,
        "settings": {
            "executionOrder": "v1"
        }
    }


def create_rag_query_workflow() -> Dict:
    """Crear definición del workflow de consultas RAG"""
    return {
        "name": "RAG - Consultas",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "query-rag",
                    "responseMode": "responseNode",
                    "options": {}
                },
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1.1,
                "position": [240, 300],
                "id": "webhook-query",
                "name": "Webhook - Recibir Consulta"
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "={{ $env.AZURE_OPENAI_ENDPOINT }}/openai/deployments/{{ $env.AZURE_OPENAI_EMBEDDING_DEPLOYMENT }}/embeddings?api-version=2023-05-15",
                    "authentication": "genericCredentialType",
                    "genericAuthType": "httpHeaderAuth",
                    "sendBody": true,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "input",
                                "value": "={{ $json.query }}"
                            }
                        ]
                    },
                    "options": {}
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [460, 300],
                "id": "http-embedding",
                "name": "Generar Embedding"
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "={{ $env.AZURE_SEARCH_ENDPOINT }}/indexes/{{ $env.AZURE_SEARCH_INDEX }}/docs/search?api-version=2023-11-01",
                    "authentication": "genericCredentialType",
                    "genericAuthType": "httpHeaderAuth",
                    "sendBody": true,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "search",
                                "value": "*"
                            },
                            {
                                "name": "vectorQueries",
                                "value": "={{ [{\"kind\": \"vector\", \"vector\": $json.data[0].embedding, \"fields\": \"content_vector\", \"k\": 5}] }}"
                            },
                            {
                                "name": "top",
                                "value": "5"
                            }
                        ]
                    },
                    "options": {}
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [680, 300],
                "id": "http-search",
                "name": "Búsqueda Vectorial"
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ $json }}"
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 300],
                "id": "respond-results",
                "name": "Responder Resultados"
            }
        ],
        "connections": {
            "Webhook - Recibir Consulta": {
                "main": [[{"node": "Generar Embedding", "type": "main", "index": 0}]]
            },
            "Generar Embedding": {
                "main": [[{"node": "Búsqueda Vectorial", "type": "main", "index": 0}]]
            },
            "Búsqueda Vectorial": {
                "main": [[{"node": "Responder Resultados", "type": "main", "index": 0}]]
            }
        },
        "active": False,
        "settings": {
            "executionOrder": "v1"
        }
    }


# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    # Configuración
    N8N_URL = "http://159.203.149.247:5678"
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5NDJjY2UxYS0yNTUzLTRjZmMtODE0Ny1hMGU5ODM2N2VjZTkiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxMDg2ODM5LCJleHAiOjE3NjM2MTQ4MDB9.OpGYJhtqHkZ1sW91PGKY9b5MmSBATsncf938QOMEc-w"
    
    # Crear instancia del manager
    manager = N8nManager(N8N_URL, API_KEY)
    
    # Imprimir resumen de workflows existentes
    manager.print_workflows_summary()
    
    print("\n")
    print("="*80)
    print("🛠️  OPCIONES DISPONIBLES")
    print("="*80)
    print("\nEste script proporciona las siguientes funcionalidades:")
    print("\n1. Listar workflows existentes")
    print("2. Crear nuevos workflows RAG")
    print("3. Exportar/Importar workflows")
    print("4. Ejecutar workflows")
    print("5. Ver historial de ejecuciones")
    print("\n" + "="*80)
    print("\n💡 Ejemplo de uso en Python:")
    print("\n    from n8n_manager import N8nManager")
    print("    manager = N8nManager(N8N_URL, API_KEY)")
    print("    workflows = manager.list_workflows()")
    print("    manager.execute_workflow('workflow_id', {'data': 'test'})")
    print("\n" + "="*80)

