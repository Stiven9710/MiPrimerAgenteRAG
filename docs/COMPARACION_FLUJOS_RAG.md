# 🔄 Comparación de Flujos RAG

## 📊 Resumen Ejecutivo

| Característica | RAG Tradicional | RAG con Documento Temporal |
|----------------|-----------------|----------------------------|
| **Documentos** | Solo pre-indexados | Pre-indexados + Temporal |
| **Latencia** | ⚡ Rápida (2-3s) | 🐌 Más lenta (10-30s) |
| **Flexibilidad** | ⚪ Baja | 🟢 Alta |
| **Casos de uso** | Conocimiento estable | Análisis ad-hoc |
| **Complejidad** | ⚪ Simple | 🟡 Media |
| **Costo** | 💰 Bajo | 💰💰 Medio |

---

## 🏗️ Arquitectura Visual

### Flujo 1: RAG Tradicional (Solo Documentos Indexados)

```
┌─────────────────────────────────────────────────────────────┐
│  USUARIO                                                     │
│  "¿Cuáles son las políticas de crédito?"                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  N8N WORKFLOW: RAG - Consulta                                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Recibir pregunta                                         │
│  2. Generar embedding de pregunta ────────┐                 │
│  3. Buscar en Azure AI Search              │                │
│     (documentos pre-indexados)             │                │
│  4. Obtener top-K resultados               │                │
│  5. Construir contexto                     │                │
│  6. GPT-4 genera respuesta                 │                │
│                                             │                │
└─────────────────────────────────────────────┼───────────────┘
                                              │
                         ┌────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  AZURE AI SEARCH                                             │
│  📚 Índice Vectorial                                         │
│  ├─ politicas_credito.pdf (indexado)                        │
│  ├─ manual_banco.pdf (indexado)                             │
│  ├─ procedimientos.pdf (indexado)                           │
│  └─ 1,000+ documentos más...                                │
└─────────────────────────────────────────────────────────────┘

✅ Ventajas:
   • Rápido (2-3 segundos)
   • Económico
   • Simple de mantener
   • Escalable

❌ Limitaciones:
   • Solo documentos pre-cargados
   • No puede analizar documentos nuevos sin indexar
   • Menos flexible para casos ad-hoc
```

---

### Flujo 2: RAG con Documento Temporal

```
┌─────────────────────────────────────────────────────────────┐
│  USUARIO                                                     │
│  "¿Este contrato cumple políticas?"                          │
│  + 📄 contrato_nuevo.pdf                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  N8N WORKFLOW: RAG - Consulta con Documento                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Recibir pregunta + documento                             │
│  2. Extraer texto del documento ─────────┐                  │
│  3. Dividir en chunks                     │                  │
│  4. Generar embeddings del documento      │                  │
│  5. Generar embedding de pregunta         │                  │
│  6. Calcular similitud                    │                  │
│  7. [OPCIONAL] Buscar en índice ──────────┼────┐            │
│  8. Combinar contextos                    │    │            │
│  9. GPT-4 genera respuesta comparando     │    │            │
│                                            │    │            │
└────────────────────────────────────────────┼────┼────────────┘
                                             │    │
                    ┌────────────────────────┘    │
                    ▼                             │
┌─────────────────────────────────────┐          │
│  DOCUMENTO TEMPORAL                 │          │
│  📄 contrato_nuevo.pdf              │          │
│  ├─ Texto extraído                  │          │
│  ├─ Dividido en 15 chunks          │          │
│  └─ Embeddings generados            │          │
└─────────────────────────────────────┘          │
                                                  │
                         ┌────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  AZURE AI SEARCH (Opcional)                                  │
│  📚 Índice Vectorial                                         │
│  ├─ politicas_credito.pdf (indexado)                        │
│  ├─ manual_contratos.pdf (indexado)                         │
│  └─ requisitos_legales.pdf (indexado)                       │
└─────────────────────────────────────────────────────────────┘

                         ↓
┌─────────────────────────────────────────────────────────────┐
│  GPT-4 CONTEXTO COMBINADO                                    │
│  ═══════════════════════════════════════════════            │
│  DOCUMENTO PROPORCIONADO:                                    │
│  • Contrato entre Banco y Cliente X                         │
│  • Monto: $50,000,000 COP                                   │
│  • Plazo: 36 meses                                          │
│  ---                                                         │
│  DOCUMENTOS DE REFERENCIA:                                   │
│  • Política: Montos máximos hasta $100M                     │
│  • Manual: Plazos permitidos 12-60 meses                   │
│  • Requisitos: Debe incluir cláusula X                      │
└─────────────────────────────────────────────────────────────┘

✅ Ventajas:
   • Analiza documentos sin indexarlos
   • Compara con base de conocimiento
   • Flexible para análisis ad-hoc
   • Útil para documentos sensibles/temporales

❌ Limitaciones:
   • Más lento (10-30 segundos)
   • Mayor costo (más tokens GPT-4)
   • Límite de tamaño de documento
   • Más complejo de implementar
```

---

## 🎯 Casos de Uso por Flujo

### RAG Tradicional

| Caso de Uso | ¿Por qué este flujo? |
|-------------|---------------------|
| **Base de conocimiento corporativa** | Documentos estables, consultados frecuentemente |
| **FAQ automatizado** | Respuestas a preguntas comunes |
| **Chatbot de soporte** | Información de productos y servicios |
| **Búsqueda en manuales** | Documentación interna estandarizada |
| **Políticas y procedimientos** | Documentos oficiales versionados |

### RAG con Documento Temporal

| Caso de Uso | ¿Por qué este flujo? |
|-------------|---------------------|
| **Análisis de contratos** | Cada contrato es único, validar con políticas |
| **Revisión de facturas** | Verificar datos contra tarifario actualizado |
| **Evaluación de reportes** | Comparar con reportes históricos sin indexar todos |
| **Due diligence** | Analizar documentos de terceros sensibles |
| **Comparación de propuestas** | Analizar propuestas nuevas vs. criterios |

---

## ⚡ Comparación de Performance

### Métricas

| Métrica | RAG Tradicional | RAG con Doc Temporal |
|---------|-----------------|---------------------|
| **Latencia** | 2-3 segundos | 10-30 segundos |
| **Tokens consumidos** | ~1,000 tokens | ~3,000-5,000 tokens |
| **Costo por consulta** | $0.002 | $0.006-0.010 |
| **Documentos analizados** | 3-5 (pre-indexados) | 1 temporal + 3-5 indexados |
| **Límite de documento** | Sin límite (ya indexado) | ~10 MB |

### Cuándo Usar Cada Uno

```
                    Frecuencia de Consulta
                            │
    Alta                    │
     ↑                      │
     │    ┌─────────────────┼──────────────┐
     │    │                 │              │
     │    │  RAG            │  RAG         │
     │    │  Tradicional    │  Tradicional │
     │    │  ✅ Ideal       │  ✅ Ideal    │
     │    │                 │              │
     │    ├─────────────────┼──────────────┤
     │    │                 │              │
     │    │  RAG            │  RAG con Doc │
Baja │    │  Tradicional    │  Temporal    │
     │    │  ⚠️ OK          │  ✅ Ideal    │
     │    │                 │              │
     ↓    └─────────────────┴──────────────┘
          Estable          Cambiante/Único
                Naturaleza del Documento
```

---

## 💰 Comparación de Costos

### Escenario 1: 1,000 Consultas/Día

#### RAG Tradicional
```
1,000 consultas × $0.002 = $2/día
$2 × 30 días = $60/mes
```

#### RAG con Documento Temporal
```
1,000 consultas × $0.008 = $8/día
$8 × 30 días = $240/mes
```

**Diferencia**: 4x más caro

### Escenario 2: Mix (80% tradicional, 20% con documento)

```
800 consultas tradicionales = $1.60/día
200 consultas con documento = $1.60/día
Total = $3.20/día × 30 = $96/mes
```

**Ahorro**: 60% vs. solo documento temporal

---

## 🔄 Workflow Híbrido Recomendado

### Estrategia: Usar el mejor flujo según el caso

```javascript
// En tu aplicación, detectar qué flujo usar
function selectRAGWorkflow(hasDocument, documentType, frequency) {
  if (!hasDocument) {
    // Sin documento adjunto → RAG tradicional
    return 'traditional';
  }
  
  if (documentType === 'contract' || documentType === 'proposal') {
    // Documentos únicos que requieren análisis → RAG temporal
    return 'with_document';
  }
  
  if (frequency === 'one-time') {
    // Consulta única → RAG temporal
    return 'with_document';
  }
  
  if (frequency === 'repeated') {
    // Si se va a consultar muchas veces → Indexar y usar tradicional
    return 'index_first_then_traditional';
  }
  
  return 'traditional'; // Default
}
```

---

## 📊 Matriz de Decisión

| Pregunta | Respuesta | → Flujo Recomendado |
|----------|-----------|---------------------|
| ¿Tienes documento para analizar? | No | RAG Tradicional |
| ¿Tienes documento para analizar? | Sí | ↓ |
| ¿El documento se consultará más de 10 veces? | Sí | Indexar → RAG Tradicional |
| ¿El documento se consultará más de 10 veces? | No | ↓ |
| ¿El documento es sensible/confidencial? | Sí | RAG con Doc Temporal |
| ¿El documento es sensible/confidencial? | No | ↓ |
| ¿Necesitas comparar con docs indexados? | Sí | RAG con Doc Temporal |
| ¿Necesitas comparar con docs indexados? | No | ↓ |
| ¿El documento es <5MB? | Sí | RAG con Doc Temporal |
| ¿El documento es <5MB? | No | Dividir o Indexar primero |

---

## 🚀 Implementación Progresiva

### Fase 1: Solo RAG Tradicional (Semana 1-2)
```
✅ Implementar workflow básico
✅ Indexar documentos corporativos
✅ Probar con usuarios
✅ Medir métricas
```

### Fase 2: Agregar RAG con Documento (Semana 3-4)
```
✅ Implementar workflow con documento temporal
✅ Probar con casos de uso específicos
✅ Optimizar performance
✅ Documentar mejores prácticas
```

### Fase 3: Workflow Inteligente (Semana 5-6)
```
✅ Implementar lógica de selección automática
✅ Monitorear costos y performance
✅ Ajustar según uso real
✅ Entrenar usuarios
```

---

## 💡 Recomendación Final

**Para Banco Caja Social:**

1. **Implementar primero RAG Tradicional** (80% de casos de uso)
   - Base de conocimiento de productos
   - Políticas y procedimientos
   - FAQ de clientes

2. **Agregar RAG con Documento para casos específicos** (20%)
   - Análisis de contratos nuevos
   - Evaluación de propuestas
   - Due diligence

3. **Usar workflow híbrido inteligente**
   - Detectar automáticamente qué flujo usar
   - Optimizar costos
   - Mejor experiencia de usuario

**Beneficio esperado:**
- ✅ Cubre 100% de casos de uso
- ✅ Optimiza costos (mix de flujos)
- ✅ Maximiza flexibilidad
- ✅ Mantiene performance

---

**Última actualización**: 21 de Octubre, 2025

