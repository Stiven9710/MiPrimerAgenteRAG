# 🐍 Scripts Python del Proyecto

Esta carpeta contiene los scripts Python para gestionar y operar el sistema RAG.

## 📋 Scripts Disponibles

### 1. 🔧 `n8n_manager.py`
**Descripción**: Cliente Python completo para interactuar con la API de n8n.

**Funcionalidades**:
- ✅ Listar workflows
- ✅ Obtener detalles de workflows
- ✅ Crear nuevos workflows
- ✅ Actualizar workflows existentes
- ✅ Eliminar workflows
- ✅ Activar/Desactivar workflows
- ✅ Ejecutar workflows manualmente
- ✅ Ver historial de ejecuciones
- ✅ Exportar workflows a JSON
- ✅ Importar workflows desde JSON

**Uso básico**:
```python
from scripts.n8n_manager import N8nManager

manager = N8nManager(
    base_url="http://159.203.149.247:5678",
    api_key="TU_API_KEY"
)

# Listar workflows
workflows = manager.list_workflows()
for wf in workflows:
    print(f"{wf['name']} - {'Activo' if wf['active'] else 'Inactivo'}")

# Ver detalles
workflow = manager.get_workflow("workflow_id")

# Ejecutar workflow
result = manager.execute_workflow("workflow_id", {"data": "test"})

# Exportar
manager.export_workflow("workflow_id", "workflows/backup.json")
```

**Ejecutar directamente**:
```bash
# Desde la raíz del proyecto
python3 scripts/n8n_manager.py

# Muestra resumen de workflows existentes
```

---

### 2. 🚀 `setup_rag_workflows.py`
**Descripción**: Script interactivo para crear automáticamente los 3 workflows RAG principales.

**Workflows que crea**:
1. RAG - Ingesta Completa de Documentos
2. RAG - Sistema de Consultas Completo
3. RAG - Eliminar Documento

**Uso**:
```bash
# Desde la raíz del proyecto
python3 scripts/setup_rag_workflows.py

# Sigue las instrucciones en pantalla
# Presiona 's' cuando te pregunte si deseas crear los workflows
```

**Salida esperada**:
```
🚀 SETUP DE WORKFLOWS RAG PARA N8N
================================================================================

📋 Workflows disponibles para crear:

1. RAG - Ingesta Completa de Documentos
2. RAG - Sistema de Consultas Completo
3. RAG - Eliminar Documento

¿Deseas crear los workflows? (s/n): s

🔨 Creando workflows...

1️⃣  Creando workflow de ingesta... ✅ Creado - ID: abc123
2️⃣  Creando workflow de consultas... ✅ Creado - ID: def456
3️⃣  Creando workflow de eliminación... ✅ Creado - ID: ghi789

✅ WORKFLOWS CREADOS EXITOSAMENTE
```

**Nota**: Los workflows se crean con placeholders (datos simulados). Para hacerlos funcionar con datos reales, debes configurar Azure y actualizar los nodos según `docs/CHECKLIST_IMPLEMENTACION.md`.

---

### 3. 🧪 `test_connection.py`
**Descripción**: Script de diagnóstico para verificar el estado del sistema completo.

**Pruebas que realiza**:
1. ✅ Conexión con API de n8n
2. ✅ Existencia de webhook de ingesta
3. ✅ Existencia de webhook de consultas
4. ✅ Configuración de variables Azure

**Uso**:
```bash
# Desde la raíz del proyecto
python3 scripts/test_connection.py
```

**Salida**:
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PRUEBAS DEL SISTEMA RAG                                   ║
║                    Banco Caja Social                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Fecha: 2025-10-21 18:00:00
Servidor n8n: http://159.203.149.247:5678

================================================================================
  1. PRUEBA DE CONEXIÓN CON N8N API
================================================================================
✅ Conexión exitosa con n8n API
   └─ Workflows encontrados: 5

================================================================================
  2. PRUEBA DE WEBHOOK DE INGESTA
================================================================================
✅ Webhook de ingesta funcional
   └─ Document ID: doc_abc123
   └─ Chunks generados: 5

...

📊 REPORTE DE PRUEBAS
✓ Pruebas pasadas: 4/4
```

**Cuándo ejecutarlo**:
- Después de instalar el proyecto
- Después de crear workflows
- Después de configurar Azure
- Cuando algo no funciona (diagnóstico)
- Antes de un deployment

---

## 🔧 Configuración

Todos los scripts requieren:

### 1. Dependencias Python
```bash
pip install -r config/requirements.txt
```

### 2. Variables de Entorno (opcional para algunos scripts)
```bash
# Copiar template
cp config/config_template.env .env

# Editar .env con tus credenciales
nano .env

# Cargar variables
export $(cat .env | xargs)
```

### 3. Acceso a n8n
Los scripts usan estas credenciales hardcodeadas (puedes cambiarlas):
- **URL**: http://159.203.149.247:5678
- **API Key**: Configurada en cada script

---

## 📦 Dependencias

Los scripts requieren estos paquetes Python:

```python
requests==2.31.0        # Para llamadas HTTP a n8n API
python-dotenv==1.0.0    # Para cargar variables de entorno (opcional)
```

Instalar con:
```bash
pip install -r config/requirements.txt
```

---

## 🎯 Flujo de Uso Recomendado

### Primera vez:
```bash
# 1. Instalar dependencias
pip install -r config/requirements.txt

# 2. Verificar conexión con n8n
python3 scripts/test_connection.py

# 3. Crear workflows RAG
python3 scripts/setup_rag_workflows.py

# 4. Verificar que se crearon correctamente
python3 scripts/test_connection.py
```

### Uso regular:
```bash
# Ver estado del sistema
python3 scripts/test_connection.py

# Gestionar workflows desde Python
python3 scripts/n8n_manager.py
```

---

## 🔍 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'requests'"
```bash
pip install -r config/requirements.txt
```

### Error: "Connection refused" o "Timeout"
- Verificar que n8n esté corriendo: http://159.203.149.247:5678
- Verificar que el puerto 5678 esté abierto
- Verificar la URL en el script

### Error: "401 Unauthorized"
- Verificar que la API Key sea correcta
- Verificar que la API esté habilitada en n8n (Settings > API)

### Los workflows se crean pero no funcionan
- Normal! Los workflows usan placeholders
- Sigue `docs/CHECKLIST_IMPLEMENTACION.md` para configurar Azure
- Reemplaza los nodos simulados con integraciones reales

---

## 🚀 Extensión de Scripts

### Crear tu propio script

```python
"""
mi_script.py - Descripción de tu script
"""

import sys
import os

# Importar el manager de n8n
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from n8n_manager import N8nManager

def main():
    manager = N8nManager(
        base_url="http://159.203.149.247:5678",
        api_key="TU_API_KEY"
    )
    
    # Tu lógica aquí
    workflows = manager.list_workflows()
    print(f"Total workflows: {len(workflows)}")

if __name__ == "__main__":
    main()
```

---

## 📝 Buenas Prácticas

1. **No hardcodear credenciales sensibles** en scripts que se commitean
2. **Usar variables de entorno** para API keys en producción
3. **Hacer backups** antes de modificar workflows
4. **Probar en desarrollo** antes de aplicar en producción
5. **Documentar** cualquier script nuevo que crees

---

## 📞 Soporte

Si tienes problemas con los scripts:

1. **Leer** este README
2. **Ejecutar** `test_connection.py` para diagnóstico
3. **Revisar** logs de error
4. **Consultar** `docs/CHECKLIST_IMPLEMENTACION.md`
5. **Contactar** al equipo técnico

---

**¡Comienza ejecutando `test_connection.py` para verificar tu setup! 🚀**

