# 📂 Workflows de n8n

Esta carpeta contiene los workflows exportados de n8n en formato JSON.

## 📋 Estructura

Los workflows se guardan con el siguiente formato:
```
workflows/
├── rag_ingestion.json          # Workflow de ingesta de documentos
├── rag_query.json              # Workflow de consultas RAG
├── rag_delete.json             # Workflow de eliminación de documentos
└── backups/                    # Respaldos de workflows
    └── YYYY-MM-DD/
        └── workflow_name.json
```

## 💾 Exportar Workflows

### Opción 1: Desde la UI de n8n
1. Abrir n8n: http://159.203.149.247:5678
2. Ir al workflow que deseas exportar
3. Clic en menú ⋮ → "Download"
4. Guardar el archivo .json en esta carpeta

### Opción 2: Usando Python Script
```python
from scripts.n8n_manager import N8nManager

manager = N8nManager(
    base_url="http://159.203.149.247:5678",
    api_key="TU_API_KEY"
)

# Exportar workflow específico
manager.export_workflow("workflow_id", "workflows/mi_workflow.json")
```

### Opción 3: Script de Backup Automático
```bash
# Desde la raíz del proyecto
python3 scripts/n8n_manager.py --export-all --output workflows/backups/
```

## 📥 Importar Workflows

### Opción 1: Desde la UI de n8n
1. Abrir n8n: http://159.203.149.247:5678
2. Ir a "Workflows"
3. Clic en "Import from File"
4. Seleccionar el archivo .json de esta carpeta

### Opción 2: Usando Python Script
```python
from scripts.n8n_manager import N8nManager

manager = N8nManager(
    base_url="http://159.203.149.247:5678",
    api_key="TU_API_KEY"
)

# Importar workflow
manager.import_workflow("workflows/mi_workflow.json")
```

## 🔄 Control de Versiones

Es recomendable mantener versiones de los workflows:

```
workflows/
├── rag_ingestion_v1.json
├── rag_ingestion_v2.json
└── rag_ingestion_latest.json  # Symlink o copia del más reciente
```

## 📝 Notas

- Los workflows en JSON contienen toda la configuración de nodos y conexiones
- **IMPORTANTE**: Los workflows NO contienen credenciales (por seguridad)
- Después de importar, debes configurar las credenciales manualmente en n8n
- Mantén backups regulares de tus workflows antes de hacer cambios

## 🚀 Workflows RAG Disponibles

Una vez ejecutes `python3 scripts/setup_rag_workflows.py`, se crearán 3 workflows:

1. **RAG - Ingesta Completa de Documentos**
   - Recibe documentos
   - Extrae texto
   - Divide en chunks
   - Genera embeddings
   - Indexa en Azure AI Search

2. **RAG - Sistema de Consultas Completo**
   - Recibe pregunta del usuario
   - Genera embedding de la pregunta
   - Busca en índice vectorial
   - Genera respuesta con GPT-4
   - Retorna respuesta + fuentes

3. **RAG - Eliminar Documento**
   - Recibe document_id
   - Obtiene metadata
   - Elimina del índice
   - Actualiza base de datos

## 🔐 Seguridad

⚠️ **NO commitear** workflows que contengan:
- API Keys hardcodeadas
- URLs internas sensibles
- Información confidencial

Usar el archivo `.env` para credenciales.

