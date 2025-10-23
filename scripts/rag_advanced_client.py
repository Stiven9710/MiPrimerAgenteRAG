"""
Cliente Avanzado para RAG con Feedback y Métricas
Soporta múltiples tipos de entrada: texto, documentos, imágenes
Incluye sistema de feedback y complementación automática
"""

import base64
import requests
import json
from typing import List, Dict, Optional, Union
from pathlib import Path
from datetime import datetime
import time

class AdvancedRAGClient:
    """Cliente avanzado para sistema RAG con feedback"""
    
    def __init__(self, base_url: str = "http://159.203.149.247:5678"):
        self.base_url = base_url.rstrip('/')
        self.query_endpoint = f"{self.base_url}/webhook/rag/advanced-query"
        self.feedback_endpoint = f"{self.base_url}/webhook/rag/feedback"
        self.complement_endpoint = f"{self.base_url}/webhook/rag/complement"
        self.last_query_id = None
        self.last_result = None
    
    def query(
        self,
        question: str,
        documents: List[str] = None,
        images: List[str] = None,
        additional_text: str = None,
        use_indexed: bool = True,
        require_high_confidence: bool = False,
        verbose: bool = True
    ) -> Dict:
        """
        Realizar consulta avanzada con múltiples tipos de entrada
        
        Args:
            question: Pregunta principal
            documents: Lista de rutas a documentos PDF, DOCX, TXT
            images: Lista de rutas a imágenes JPG, PNG
            additional_text: Texto adicional de contexto
            use_indexed: Buscar también en documentos indexados
            require_high_confidence: Solo responder si confianza >80%
            verbose: Imprimir detalles
        
        Returns:
            Diccionario con respuesta estructurada y metadata
        """
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"🔍 CONSULTA AVANZADA AL RAG")
            print(f"{'='*80}\n")
            print(f"📝 Pregunta: {question}")
        
        # Preparar inputs
        inputs = []
        
        # Agregar texto adicional
        if additional_text:
            inputs.append({
                "type": "text",
                "content": additional_text
            })
            if verbose:
                print(f"📄 Texto adicional: {len(additional_text)} caracteres")
        
        # Agregar documentos
        if documents:
            for doc_path in documents:
                if not Path(doc_path).exists():
                    print(f"⚠️  Archivo no encontrado: {doc_path}")
                    continue
                
                with open(doc_path, 'rb') as f:
                    file_content = base64.b64encode(f.read()).decode('utf-8')
                
                file_size = Path(doc_path).stat().st_size
                
                inputs.append({
                    "type": "document",
                    "filename": Path(doc_path).name,
                    "file_base64": file_content
                })
                
                if verbose:
                    print(f"📎 Documento: {Path(doc_path).name} ({file_size/1024:.1f} KB)")
        
        # Agregar imágenes
        if images:
            for img_path in images:
                if not Path(img_path).exists():
                    print(f"⚠️  Imagen no encontrada: {img_path}")
                    continue
                
                with open(img_path, 'rb') as f:
                    file_content = base64.b64encode(f.read()).decode('utf-8')
                
                file_size = Path(img_path).stat().st_size
                
                inputs.append({
                    "type": "image",
                    "filename": Path(img_path).name,
                    "file_base64": file_content
                })
                
                if verbose:
                    print(f"🖼️  Imagen: {Path(img_path).name} ({file_size/1024:.1f} KB)")
        
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
        
        if verbose:
            print(f"\n🚀 Enviando consulta...")
            print(f"   └─ Tipos de entrada: {len(inputs)}")
            print(f"   └─ Usar docs indexados: {'Sí' if use_indexed else 'No'}")
        
        # Enviar request
        try:
            start_time = time.time()
            
            response = requests.post(
                self.query_endpoint,
                json=payload,
                timeout=120
            )
            
            elapsed = time.time() - start_time
            
            response.raise_for_status()
            result = response.json()
            
            # Guardar para referencia
            self.last_query_id = result.get('query_id')
            self.last_result = result
            
            if verbose:
                print(f"⏱️  Tiempo de respuesta: {elapsed:.2f}s\n")
                self._print_result(result)
            
            return result
            
        except requests.exceptions.Timeout:
            print(f"❌ Timeout: La consulta tardó más de 2 minutos")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"❌ Error 404: Workflow no encontrado")
                print(f"   💡 Implementa el workflow según: docs/RAG_AVANZADO_CON_FEEDBACK.md")
            else:
                print(f"❌ Error HTTP {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def _print_result(self, result: Dict):
        """Imprimir resultado de forma legible"""
        print(f"{'='*80}")
        print(f"✅ RESPUESTA")
        print(f"{'='*80}\n")
        
        answer = result.get('answer', {})
        
        print(f"📌 RESPUESTA PRINCIPAL:")
        print(f"{answer.get('main_response', 'Sin respuesta')}\n")
        
        if answer.get('detailed_analysis'):
            print(f"🔬 ANÁLISIS DETALLADO:")
            print(f"{answer['detailed_analysis']}\n")
        
        if answer.get('confidence'):
            confidence = answer['confidence']
            emoji = "🟢" if confidence >= 80 else "🟡" if confidence >= 50 else "🔴"
            print(f"📊 CONFIANZA: {emoji} {confidence}%")
        
        if answer.get('sources'):
            print(f"\n📚 FUENTES ({len(answer['sources'])}):")
            for source in answer['sources']:
                icon = "📎" if source['type'] == 'user_document' else "🖼️" if source['type'] == 'user_image' else "📚"
                print(f"   {icon} {source.get('filename', 'N/A')}")
        
        if answer.get('follow_up_suggestions'):
            print(f"\n💡 SUGERENCIAS DE SEGUIMIENTO:")
            for i, suggestion in enumerate(answer['follow_up_suggestions'], 1):
                print(f"   {i}. {suggestion}")
        
        if answer.get('warnings'):
            print(f"\n⚠️  ADVERTENCIAS:")
            for warning in answer['warnings']:
                print(f"   • {warning}")
        
        print(f"\n{'='*80}\n")
    
    def send_feedback(
        self,
        rating: int,
        was_helpful: bool = None,
        comment: str = "",
        query_id: str = None,
        user_id: str = "anonymous",
        verbose: bool = True
    ) -> Dict:
        """
        Enviar feedback sobre una respuesta
        
        Args:
            rating: Calificación 1-5 estrellas
            was_helpful: Si fue útil (auto-calcula si None)
            comment: Comentario opcional del usuario
            query_id: ID de la consulta (usa last_query_id si None)
            user_id: ID del usuario que da feedback
            verbose: Imprimir detalles
        
        Returns:
            Diccionario con resultado del feedback
        """
        
        # Usar último query_id si no se proporciona
        if query_id is None:
            query_id = self.last_query_id
        
        if query_id is None:
            print("❌ Error: No hay query_id disponible. Realiza una consulta primero.")
            return None
        
        # Auto-calcular was_helpful si no se proporciona
        if was_helpful is None:
            was_helpful = rating >= 4
        
        payload = {
            "query_id": query_id,
            "rating": rating,
            "was_helpful": was_helpful,
            "comment": comment,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        if verbose:
            stars = "⭐" * rating
            print(f"\n📤 Enviando feedback...")
            print(f"   └─ Rating: {stars} ({rating}/5)")
            print(f"   └─ Útil: {'Sí' if was_helpful else 'No'}")
            if comment:
                print(f"   └─ Comentario: {comment}")
        
        try:
            response = requests.post(
                self.feedback_endpoint,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if verbose:
                print(f"\n✅ Feedback procesado")
                print(f"   └─ Acción: {result.get('action_taken', 'N/A')}")
                
                if result.get('notification'):
                    print(f"   └─ 💬 {result['notification']['message']}")
                
                if result.get('complement'):
                    print(f"\n📝 INFORMACIÓN COMPLEMENTARIA GENERADA:")
                    print(f"{result['complement'][:300]}...")
            
            return result
            
        except Exception as e:
            print(f"❌ Error enviando feedback: {e}")
            return None
    
    def query_with_feedback_loop(
        self,
        question: str,
        auto_feedback: bool = False,
        **kwargs
    ) -> Dict:
        """
        Consulta con loop de feedback interactivo
        
        Args:
            question: Pregunta
            auto_feedback: Si True, no solicita feedback interactivo
            **kwargs: Argumentos para query()
        
        Returns:
            Dict con query_result y feedback_result
        """
        
        # Hacer consulta
        result = self.query(question, **kwargs)
        
        if result is None:
            return None
        
        # Solicitar feedback
        if auto_feedback:
            # Feedback automático basado en confianza
            confidence = result.get('answer', {}).get('confidence', 50)
            rating = 5 if confidence >= 80 else 4 if confidence >= 60 else 3
            feedback_result = self.send_feedback(
                rating=rating,
                comment="Feedback automático basado en confianza"
            )
        else:
            # Feedback interactivo
            print("\n" + "─"*80)
            print("📊 ¿TE FUE ÚTIL ESTA RESPUESTA?")
            print("─"*80)
            print("\nCalifica del 1 al 5:")
            print("  5 ⭐⭐⭐⭐⭐ Excelente")
            print("  4 ⭐⭐⭐⭐ Buena")
            print("  3 ⭐⭐⭐ Aceptable")
            print("  2 ⭐⭐ Insuficiente")
            print("  1 ⭐ No útil")
            
            try:
                rating = int(input("\nTu calificación (1-5): "))
                if rating < 1 or rating > 5:
                    rating = 3
            except:
                rating = 3
            
            comment = input("Comentario (opcional, Enter para omitir): ").strip()
            
            feedback_result = self.send_feedback(
                rating=rating,
                comment=comment
            )
        
        return {
            'query_result': result,
            'feedback_result': feedback_result
        }
    
    def get_complement(self, query_id: str = None, verbose: bool = True) -> Dict:
        """
        Obtener complemento generado para una consulta
        
        Args:
            query_id: ID de la consulta (usa last_query_id si None)
            verbose: Imprimir detalles
        
        Returns:
            Diccionario con el complemento
        """
        
        if query_id is None:
            query_id = self.last_query_id
        
        if query_id is None:
            print("❌ Error: No hay query_id disponible")
            return None
        
        try:
            response = requests.get(
                f"{self.complement_endpoint}/{query_id}",
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if verbose:
                print(f"\n{'='*80}")
                print(f"📝 INFORMACIÓN COMPLEMENTARIA")
                print(f"{'='*80}\n")
                print(result.get('complement', 'No hay complemento disponible'))
                print(f"\n{'='*80}\n")
            
            return result
            
        except Exception as e:
            if verbose:
                print(f"ℹ️  No hay complemento disponible aún")
            return None


# ============================================================================
# FUNCIONES DE EJEMPLO
# ============================================================================

def example_text_only():
    """Ejemplo: Solo texto"""
    print("\n" + "="*80)
    print("EJEMPLO 1: SOLO TEXTO")
    print("="*80)
    
    client = AdvancedRAGClient()
    
    result = client.query(
        question="¿Cuáles son los requisitos para un crédito de vivienda?",
        use_indexed=True
    )
    
    if result:
        client.send_feedback(rating=4, comment="Clara y completa")


def example_text_with_document():
    """Ejemplo: Texto + Documento"""
    print("\n" + "="*80)
    print("EJEMPLO 2: TEXTO + DOCUMENTO")
    print("="*80)
    
    client = AdvancedRAGClient()
    
    result = client.query(
        question="¿Este contrato cumple con nuestras políticas de crédito?",
        documents=["./test_contract.pdf"],
        use_indexed=True
    )
    
    if result:
        client.send_feedback(rating=5, comment="Análisis muy completo")


def example_multimodal():
    """Ejemplo: Texto + Documento + Imagen"""
    print("\n" + "="*80)
    print("EJEMPLO 3: MULTIMODAL (Texto + Documento + Imagen)")
    print("="*80)
    
    client = AdvancedRAGClient()
    
    result = client.query(
        question="¿La firma en este contrato es válida y el documento está completo?",
        documents=["./contract.pdf"],
        images=["./signature.jpg"],
        additional_text="El firmante es el representante legal de la empresa XYZ S.A.",
        use_indexed=True
    )
    
    if result:
        client.send_feedback(rating=5, comment="Análisis de firma excelente")


def example_interactive():
    """Ejemplo: Modo interactivo"""
    print("\n" + "="*80)
    print("EJEMPLO 4: MODO INTERACTIVO")
    print("="*80)
    
    client = AdvancedRAGClient()
    
    # Con feedback interactivo
    result = client.query_with_feedback_loop(
        question="¿Qué documentos necesito para abrir una cuenta empresarial?",
        use_indexed=True,
        auto_feedback=False  # Solicitar feedback del usuario
    )


def example_batch_queries():
    """Ejemplo: Múltiples consultas con análisis"""
    print("\n" + "="*80)
    print("EJEMPLO 5: BATCH DE CONSULTAS")
    print("="*80)
    
    client = AdvancedRAGClient()
    
    questions = [
        "¿Cuáles son las tasas de interés actuales?",
        "¿Cómo abrir una cuenta de ahorros?",
        "¿Qué requisitos hay para crédito de vehículo?"
    ]
    
    results = []
    for i, question in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] Procesando...")
        result = client.query(
            question=question,
            use_indexed=True,
            verbose=False
        )
        
        if result:
            # Feedback automático
            confidence = result.get('answer', {}).get('confidence', 50)
            rating = 5 if confidence >= 80 else 4 if confidence >= 60 else 3
            
            client.send_feedback(
                rating=rating,
                comment=f"Consulta batch {i}",
                verbose=False
            )
            
            results.append({
                'question': question,
                'confidence': confidence,
                'rating': rating
            })
    
    # Resumen
    print(f"\n{'='*80}")
    print("RESUMEN DE CONSULTAS")
    print(f"{'='*80}\n")
    for r in results:
        print(f"❓ {r['question']}")
        print(f"   📊 Confianza: {r['confidence']}% | Rating: {r['rating']}/5\n")


# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("\n" + "="*80)
            print("🔍 CLIENTE AVANZADO DE RAG")
            print("="*80 + "\n")
            print("Uso:")
            print("  python3 scripts/rag_advanced_client.py [opción]\n")
            print("Opciones:")
            print("  --help        Muestra esta ayuda")
            print("  --example1    Ejemplo: Solo texto")
            print("  --example2    Ejemplo: Texto + Documento")
            print("  --example3    Ejemplo: Multimodal")
            print("  --example4    Ejemplo: Interactivo")
            print("  --example5    Ejemplo: Batch de consultas")
            print("\n  Sin argumentos: Menú interactivo\n")
            print("="*80 + "\n")
            
        elif sys.argv[1] == '--example1':
            example_text_only()
        elif sys.argv[1] == '--example2':
            example_text_with_document()
        elif sys.argv[1] == '--example3':
            example_multimodal()
        elif sys.argv[1] == '--example4':
            example_interactive()
        elif sys.argv[1] == '--example5':
            example_batch_queries()
    else:
        print("\n" + "="*80)
        print("🤖 CLIENTE AVANZADO DE RAG - BANCO CAJA SOCIAL")
        print("="*80)
        print("\nEste cliente permite consultas avanzadas con:")
        print("  • 📝 Texto")
        print("  • 📎 Documentos (PDF, DOCX, TXT)")
        print("  • 🖼️  Imágenes (JPG, PNG)")
        print("  • 📊 Sistema de feedback")
        print("  • 🔄 Complementación automática")
        print("\nEjecuta con --help para ver opciones")
        print("\n⚠️  Requiere que el workflow esté implementado en n8n")
        print("   Ver: docs/RAG_AVANZADO_CON_FEEDBACK.md")
        print("\n" + "="*80 + "\n")

