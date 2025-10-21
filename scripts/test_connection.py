"""
Script de pruebas para verificar conexión con n8n y funcionalidad básica
"""

import requests
import json
import base64
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuración
N8N_URL = "http://159.203.149.247:5678"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5NDJjY2UxYS0yNTUzLTRjZmMtODE0Ny1hMGU5ODM2N2VjZTkiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxMDg2ODM5LCJleHAiOjE3NjM2MTQ4MDB9.OpGYJhtqHkZ1sW91PGKY9b5MmSBATsncf938QOMEc-w"

def print_header(text):
    """Imprimir encabezado decorado"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_result(success, message):
    """Imprimir resultado de prueba"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def test_api_connection():
    """Probar conexión con API de n8n"""
    print_header("1. PRUEBA DE CONEXIÓN CON N8N API")
    
    try:
        response = requests.get(
            f"{N8N_URL}/api/v1/workflows",
            headers={
                'X-N8N-API-KEY': API_KEY,
                'Accept': 'application/json'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            workflows_count = len(data.get('data', []))
            print_result(True, f"Conexión exitosa con n8n API")
            print(f"   └─ Workflows encontrados: {workflows_count}")
            return True, data.get('data', [])
        else:
            print_result(False, f"Error de conexión: HTTP {response.status_code}")
            return False, []
            
    except Exception as e:
        print_result(False, f"Error de conexión: {e}")
        return False, []

def test_webhook_ingestion():
    """Probar webhook de ingesta (si existe)"""
    print_header("2. PRUEBA DE WEBHOOK DE INGESTA")
    
    # Crear un documento de prueba pequeño
    test_content = "Este es un documento de prueba del sistema RAG del Banco Caja Social."
    test_base64 = base64.b64encode(test_content.encode()).decode()
    
    payload = {
        "filename": "test_document.txt",
        "file_base64": test_base64,
        "department": "testing",
        "document_type": "test",
        "tags": ["test", "automatico"],
        "uploaded_by": "test_script"
    }
    
    try:
        response = requests.post(
            f"{N8N_URL}/webhook/rag/ingest",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, "Webhook de ingesta funcional")
            print(f"   └─ Document ID: {result.get('document_id', 'N/A')}")
            print(f"   └─ Chunks generados: {result.get('chunks_generated', 'N/A')}")
            return True
        elif response.status_code == 404:
            print_result(False, "Webhook de ingesta no encontrado (aún no creado)")
            print("   └─ Ejecuta: python3 scripts/setup_rag_workflows.py")
            return False
        else:
            print_result(False, f"Error en webhook: HTTP {response.status_code}")
            print(f"   └─ Respuesta: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print_result(False, "Timeout - El webhook está tardando mucho")
        return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False

def test_webhook_query():
    """Probar webhook de consultas (si existe)"""
    print_header("3. PRUEBA DE WEBHOOK DE CONSULTAS")
    
    payload = {
        "query": "¿Qué es el Banco Caja Social?",
        "top_k": 3
    }
    
    try:
        response = requests.post(
            f"{N8N_URL}/webhook/rag/query",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, "Webhook de consultas funcional")
            print(f"   └─ Respuesta: {result.get('answer', 'N/A')[:100]}...")
            print(f"   └─ Fuentes: {len(result.get('sources', []))}")
            return True
        elif response.status_code == 404:
            print_result(False, "Webhook de consultas no encontrado (aún no creado)")
            print("   └─ Ejecuta: python3 scripts/setup_rag_workflows.py")
            return False
        else:
            print_result(False, f"Error en webhook: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False

def test_azure_services():
    """Verificar si hay variables de Azure configuradas"""
    print_header("4. VERIFICACIÓN DE CONFIGURACIÓN AZURE")
    
    # Solo verificar si existen (no hacer llamadas reales)
    import os
    
    azure_vars = {
        "AZURE_OPENAI_ENDPOINT": "Endpoint de Azure OpenAI",
        "AZURE_OPENAI_KEY": "API Key de Azure OpenAI",
        "AZURE_SEARCH_ENDPOINT": "Endpoint de Azure AI Search",
        "AZURE_SEARCH_KEY": "API Key de Azure Search",
        "COSMOS_DB_ENDPOINT": "Endpoint de Cosmos DB"
    }
    
    configured = 0
    for var, description in azure_vars.items():
        if os.getenv(var):
            print_result(True, f"{description} configurado")
            configured += 1
        else:
            print_result(False, f"{description} no configurado")
    
    if configured == 0:
        print("\n⚠️  No se encontraron variables de entorno de Azure")
        print("   Configura las variables en config_template.env y carga con:")
        print("   export $(cat .env | xargs)")
    
    return configured > 0

def generate_report(api_ok, workflows, ingestion_ok, query_ok, azure_ok):
    """Generar reporte final"""
    print_header("📊 REPORTE DE PRUEBAS")
    
    total_tests = 4
    passed = sum([api_ok, ingestion_ok, query_ok, azure_ok])
    
    print(f"\n✓ Pruebas pasadas: {passed}/{total_tests}")
    print(f"✗ Pruebas fallidas: {total_tests - passed}/{total_tests}")
    
    print("\n" + "─"*80)
    print("ESTADO DE COMPONENTES:")
    print("─"*80)
    
    components = [
        ("Conexión API n8n", api_ok),
        ("Webhook de Ingesta", ingestion_ok),
        ("Webhook de Consultas", query_ok),
        ("Configuración Azure", azure_ok)
    ]
    
    for component, status in components:
        icon = "🟢" if status else "🔴"
        status_text = "OPERATIVO" if status else "NO DISPONIBLE"
        print(f"{icon} {component:<25} {status_text}")
    
    print("\n" + "─"*80)
    print("WORKFLOWS EXISTENTES:")
    print("─"*80)
    
    if workflows:
        for wf in workflows:
            status_icon = "🟢" if wf['active'] else "⚪"
            print(f"{status_icon} {wf['name']}")
            print(f"   └─ ID: {wf['id']}")
            print(f"   └─ Nodos: {len(wf.get('nodes', []))}")
            print(f"   └─ Estado: {'Activo' if wf['active'] else 'Inactivo'}")
    else:
        print("❌ No se encontraron workflows")
    
    print("\n" + "="*80)
    
    if passed == total_tests:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("   Tu sistema RAG está listo para usar.")
    elif passed >= 2:
        print("⚠️  SISTEMA PARCIALMENTE FUNCIONAL")
        print("   Algunos componentes necesitan configuración.")
    else:
        print("❌ SISTEMA REQUIERE CONFIGURACIÓN")
        print("   Sigue los pasos en CHECKLIST_IMPLEMENTACION.md")
    
    print("\n" + "="*80)
    print("PRÓXIMOS PASOS:")
    print("="*80)
    
    if not api_ok:
        print("\n1. Verifica que n8n esté corriendo")
        print("   URL: http://159.203.149.247:5678")
    
    if not ingestion_ok or not query_ok:
        print("\n2. Crea los workflows RAG:")
        print("   python3 scripts/setup_rag_workflows.py")
    
    if not azure_ok:
        print("\n3. Configura servicios de Azure:")
        print("   - Azure OpenAI")
        print("   - Azure AI Search")
        print("   - Azure Cosmos DB")
        print("   Consulta: docs/CHECKLIST_IMPLEMENTACION.md")
    
    print("\n" + "="*80 + "\n")

def main():
    """Función principal"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "PRUEBAS DEL SISTEMA RAG" + " "*35 + "║")
    print("║" + " "*20 + "Banco Caja Social" + " "*41 + "║")
    print("╚" + "="*78 + "╝")
    
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Servidor n8n: {N8N_URL}")
    
    # Ejecutar pruebas
    api_ok, workflows = test_api_connection()
    ingestion_ok = test_webhook_ingestion() if api_ok else False
    query_ok = test_webhook_query() if api_ok else False
    azure_ok = test_azure_services()
    
    # Generar reporte
    generate_report(api_ok, workflows, ingestion_ok, query_ok, azure_ok)

if __name__ == "__main__":
    main()

