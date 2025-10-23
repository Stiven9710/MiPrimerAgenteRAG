"""
Test RAG con Documento Temporal
Script para probar consultas RAG con documentos proporcionados en tiempo real
"""

import base64
import requests
import sys
import os
from datetime import datetime

# Configuración
N8N_URL = "http://159.203.149.247:5678"
QUERY_WITH_DOC_ENDPOINT = f"{N8N_URL}/webhook/rag/query-with-document"

def query_with_document(
    question: str,
    document_path: str,
    use_indexed: bool = True,
    top_k_indexed: int = 3,
    verbose: bool = True
):
    """
    Consultar RAG con documento temporal
    
    Args:
        question: Pregunta del usuario
        document_path: Ruta al documento temporal
        use_indexed: Si también buscar en documentos indexados
        top_k_indexed: Cuántos documentos indexados traer
        verbose: Imprimir detalles
    
    Returns:
        Diccionario con la respuesta o None si hay error
    """
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"🔍 CONSULTA RAG CON DOCUMENTO TEMPORAL")
        print(f"{'='*80}\n")
        print(f"📝 Pregunta: {question}")
        print(f"📄 Documento: {document_path}")
        print(f"📚 Usar índice: {'Sí' if use_indexed else 'No'}")
        print(f"\n{'─'*80}\n")
    
    # Validar que el archivo existe
    if not os.path.exists(document_path):
        print(f"❌ Error: Archivo no encontrado: {document_path}")
        return None
    
    # Obtener tamaño del archivo
    file_size = os.path.getsize(document_path)
    if verbose:
        print(f"📦 Tamaño del archivo: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    
    # Límite de 10MB
    if file_size > 10 * 1024 * 1024:
        print(f"⚠️  Advertencia: Archivo muy grande ({file_size/1024/1024:.2f} MB)")
        print(f"   El procesamiento puede tardar o fallar")
    
    # Leer y codificar documento
    if verbose:
        print(f"📤 Leyendo y codificando documento...")
    
    try:
        with open(document_path, 'rb') as f:
            file_content = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return None
    
    # Preparar payload
    payload = {
        "query": question,
        "document": {
            "filename": os.path.basename(document_path),
            "file_base64": file_content,
            "use_indexed_docs": use_indexed,
            "top_k_indexed": top_k_indexed
        }
    }
    
    if verbose:
        print(f"🚀 Enviando consulta a n8n...")
        print(f"   Endpoint: {QUERY_WITH_DOC_ENDPOINT}")
    
    # Enviar request
    try:
        start_time = datetime.now()
        
        response = requests.post(
            QUERY_WITH_DOC_ENDPOINT,
            json=payload,
            timeout=120  # 2 minutos de timeout
        )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if verbose:
            print(f"⏱️  Tiempo de respuesta: {elapsed:.2f}s\n")
        
        if response.status_code == 200:
            result = response.json()
            
            if verbose:
                print(f"{'='*80}")
                print(f"✅ RESPUESTA")
                print(f"{'='*80}\n")
                print(f"{result.get('answer', 'Sin respuesta')}\n")
                print(f"{'─'*80}")
                print(f"📚 FUENTES")
                print(f"{'─'*80}\n")
                
                sources = result.get('sources', {})
                
                if sources.get('temporary_document'):
                    print(f"📄 Documento temporal:")
                    for doc in sources['temporary_document']:
                        print(f"   • {doc}")
                
                if sources.get('indexed_documents'):
                    print(f"\n📚 Documentos indexados:")
                    for doc in sources['indexed_documents']:
                        print(f"   • {doc}")
                
                print(f"\n{'='*80}\n")
            
            return result
            
        elif response.status_code == 404:
            print(f"❌ Error 404: Workflow no encontrado")
            print(f"\n💡 Pasos para crear el workflow:")
            print(f"   1. Lee: docs/RAG_CON_DOCUMENTOS_TEMPORALES.md")
            print(f"   2. Implementa el workflow en n8n")
            print(f"   3. Configura el webhook: /webhook/rag/query-with-document\n")
            return None
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}\n")
            return None
            
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: La consulta tardó más de 2 minutos")
        print(f"   El documento puede ser muy grande o el servidor lento\n")
        return None
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}\n")
        return None


def example_usage():
    """Ejemplos de uso"""
    print("\n" + "="*80)
    print("📖 EJEMPLOS DE USO")
    print("="*80 + "\n")
    
    print("Ejemplo 1: Solo documento temporal")
    print("-" * 40)
    print("query_with_document(")
    print("    question='Resume este documento',")
    print("    document_path='./docs/mi_documento.pdf',")
    print("    use_indexed=False")
    print(")\n")
    
    print("Ejemplo 2: Documento + búsqueda en índice")
    print("-" * 40)
    print("query_with_document(")
    print("    question='¿Este contrato cumple con nuestras políticas?',")
    print("    document_path='./contratos/nuevo_contrato.pdf',")
    print("    use_indexed=True,")
    print("    top_k_indexed=5")
    print(")\n")
    
    print("Ejemplo 3: Análisis comparativo")
    print("-" * 40)
    print("query_with_document(")
    print("    question='¿Qué diferencias hay con reportes anteriores?',")
    print("    document_path='./reportes/reporte_actual.pdf',")
    print("    use_indexed=True")
    print(")\n")
    
    print("="*80 + "\n")


def interactive_mode():
    """Modo interactivo"""
    print("\n" + "="*80)
    print("💬 MODO INTERACTIVO - RAG CON DOCUMENTO")
    print("="*80 + "\n")
    
    while True:
        # Pedir documento
        print("📄 Ruta al documento (o 'salir' para terminar):")
        doc_path = input("   > ").strip()
        
        if doc_path.lower() in ['salir', 'exit', 'quit']:
            print("\n👋 ¡Hasta luego!\n")
            break
        
        if not doc_path:
            continue
        
        # Validar archivo
        if not os.path.exists(doc_path):
            print(f"❌ Archivo no encontrado: {doc_path}\n")
            continue
        
        # Pedir pregunta
        print("\n❓ Tu pregunta:")
        question = input("   > ").strip()
        
        if not question:
            print("❌ Pregunta vacía\n")
            continue
        
        # Preguntar si usar índice
        print("\n📚 ¿Buscar también en documentos indexados? (s/n):")
        use_idx = input("   > ").strip().lower()
        use_indexed = use_idx in ['s', 'si', 'sí', 'y', 'yes']
        
        # Ejecutar consulta
        query_with_document(
            question=question,
            document_path=doc_path,
            use_indexed=use_indexed
        )
        
        print("\n" + "-"*80 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("\n" + "="*80)
            print("🔍 TEST RAG CON DOCUMENTO TEMPORAL")
            print("="*80 + "\n")
            print("Uso:")
            print("  python3 scripts/test_rag_with_document.py [opciones]\n")
            print("Opciones:")
            print("  --help          Muestra esta ayuda")
            print("  --examples      Muestra ejemplos de uso")
            print("  --interactive   Modo interactivo\n")
            print("  Sin argumentos: Ejecuta test de ejemplo\n")
            print("="*80 + "\n")
            
        elif sys.argv[1] == '--examples':
            example_usage()
            
        elif sys.argv[1] == '--interactive':
            interactive_mode()
            
    else:
        # Test de ejemplo (requiere workflow implementado)
        print("\n" + "="*80)
        print("🧪 TEST DE EJEMPLO")
        print("="*80)
        print("\n⚠️  Este test requiere:")
        print("   1. Workflow implementado en n8n")
        print("   2. Documento de prueba en ./test_document.pdf\n")
        
        response = input("¿Continuar con el test? (s/n): ").strip().lower()
        
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            # Crear documento de prueba si no existe
            test_file = "test_document.txt"
            if not os.path.exists(test_file):
                print(f"\n📝 Creando documento de prueba: {test_file}")
                with open(test_file, 'w') as f:
                    f.write("""
Este es un documento de prueba para el sistema RAG del Banco Caja Social.

Información importante:
- El sistema puede procesar documentos en tiempo real
- Los documentos se analizan y comparan con la base de conocimiento
- Se generan respuestas contextualizadas usando GPT-4

Características del banco:
- Banco Caja Social es una entidad financiera colombiana
- Ofrece productos como cuentas de ahorro, créditos y tarjetas
- Se enfoca en servicios para la comunidad

Este documento es solo para testing del sistema RAG.
                    """)
            
            query_with_document(
                question="¿Qué información contiene este documento?",
                document_path=test_file,
                use_indexed=False
            )
        else:
            print("\n❌ Test cancelado")
            print("\nPara ver ejemplos: python3 scripts/test_rag_with_document.py --examples")
            print("Para modo interactivo: python3 scripts/test_rag_with_document.py --interactive\n")

