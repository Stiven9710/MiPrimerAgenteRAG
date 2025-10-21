# 📂 Estructura del Proyecto RAG

## 🌳 Vista General

```
RAG Agent/
│
├── 📄 README.md                      # Documentación principal del proyecto
├── 📄 ESTRUCTURA.md                  # Este archivo (mapa del proyecto)
├── 🚫 .gitignore                     # Archivos a ignorar en Git
│
├── 📂 config/                        # ⚙️ Configuración
│   ├── README.md                     # Guía de configuración
│   ├── requirements.txt              # Dependencias Python
│   └── config_template.env           # Template de variables de entorno
│
├── 📂 docs/                          # 📚 Documentación
│   ├── README.md                     # Índice de documentación
│   ├── INICIO_RAPIDO.md              # ⚡ Guía de inicio rápido
│   ├── ARQUITECTURA_RAG.md           # 🏗️ Arquitectura técnica
│   ├── CHECKLIST_IMPLEMENTACION.md   # ✅ Pasos de implementación
│   ├── EJEMPLOS_USO.md               # 💻 Ejemplos de código
│   └── RESUMEN_EJECUTIVO.md          # 📊 Presentación ejecutiva
│
├── 📂 scripts/                       # 🐍 Scripts Python
│   ├── README.md                     # Guía de scripts
│   ├── n8n_manager.py                # Cliente para gestionar n8n
│   ├── setup_rag_workflows.py        # Crear workflows automáticamente
│   └── test_connection.py            # Pruebas del sistema
│
└── 📂 workflows/                     # 🔄 Workflows de n8n
    └── README.md                     # Guía de workflows
```

## 📋 Contenido Detallado

### 📄 Raíz del Proyecto

| Archivo | Descripción | Para Quién |
|---------|-------------|------------|
| `README.md` | Documentación principal, punto de entrada | Todos |
| `ESTRUCTURA.md` | Este archivo, mapa del proyecto | Todos |
| `.gitignore` | Archivos ignorados por Git | Desarrolladores |

---

### ⚙️ Carpeta `config/`

**Propósito**: Archivos de configuración y dependencias

| Archivo | Descripción | Tamaño |
|---------|-------------|--------|
| `README.md` | Guía completa de configuración | ~5 KB |
| `requirements.txt` | Dependencias Python del proyecto | ~300 bytes |
| `config_template.env` | Template de variables de entorno Azure | ~2 KB |

**Archivos generados** (no en Git):
- `.env` - Variables de entorno reales (contiene credenciales)

**Uso típico**:
```bash
# Instalar dependencias
pip install -r config/requirements.txt

# Configurar ambiente
cp config/config_template.env .env
nano .env  # Editar con tus credenciales
export $(cat .env | xargs)
```

---

### 📚 Carpeta `docs/`

**Propósito**: Documentación completa del proyecto

| Archivo | Descripción | Páginas | Audiencia | Prioridad |
|---------|-------------|---------|-----------|-----------|
| `README.md` | Índice de documentación | 1 | Todos | ⭐⭐⭐ |
| `INICIO_RAPIDO.md` | Guía de inicio rápido | ~10 | Todos | ⭐⭐⭐ |
| `RESUMEN_EJECUTIVO.md` | Presentación ejecutiva, ROI | ~20 | Management | ⭐⭐⭐ |
| `ARQUITECTURA_RAG.md` | Arquitectura técnica detallada | ~30 | Técnicos | ⭐⭐ |
| `CHECKLIST_IMPLEMENTACION.md` | Pasos de implementación | ~35 | DevOps | ⭐⭐ |
| `EJEMPLOS_USO.md` | Ejemplos de código | ~25 | Developers | ⭐ |

**Flujo de lectura recomendado**:
```
1. INICIO_RAPIDO.md (5 min)
   ↓
2. RESUMEN_EJECUTIVO.md o ARQUITECTURA_RAG.md (según rol)
   ↓
3. CHECKLIST_IMPLEMENTACION.md (durante implementación)
   ↓
4. EJEMPLOS_USO.md (cuando integres)
```

**Métricas**:
- Total de documentación: ~120 páginas
- Tiempo de lectura completa: ~2-3 horas
- Cobertura: 100% del sistema

---

### 🐍 Carpeta `scripts/`

**Propósito**: Scripts Python para automatización y gestión

| Script | Líneas | Descripción | Uso |
|--------|--------|-------------|-----|
| `README.md` | ~250 | Guía de scripts | Referencia |
| `n8n_manager.py` | ~430 | Cliente completo de n8n API | Gestión workflows |
| `setup_rag_workflows.py` | ~425 | Crear workflows RAG automáticamente | Setup inicial |
| `test_connection.py` | ~260 | Diagnóstico del sistema | Testing |

**Funcionalidades por script**:

#### `n8n_manager.py`
- ✅ Listar workflows
- ✅ Crear/Actualizar/Eliminar workflows
- ✅ Activar/Desactivar workflows
- ✅ Ejecutar workflows
- ✅ Ver ejecuciones
- ✅ Exportar/Importar JSON

#### `setup_rag_workflows.py`
- ✅ Crear workflow de ingesta
- ✅ Crear workflow de consultas
- ✅ Crear workflow de eliminación
- ✅ Validación de creación

#### `test_connection.py`
- ✅ Test de API n8n
- ✅ Test de webhooks
- ✅ Test de configuración Azure
- ✅ Reporte completo

**Uso rápido**:
```bash
# Ver workflows existentes
python3 scripts/n8n_manager.py

# Crear workflows RAG
python3 scripts/setup_rag_workflows.py

# Diagnosticar sistema
python3 scripts/test_connection.py
```

---

### 🔄 Carpeta `workflows/`

**Propósito**: Almacenar exports JSON de workflows de n8n

**Estructura esperada**:
```
workflows/
├── README.md
├── rag_ingestion.json           # Workflow de ingesta
├── rag_query.json               # Workflow de consultas
├── rag_delete.json              # Workflow de eliminación
└── backups/                     # Respaldos
    └── 2025-10-21/
        ├── rag_ingestion.json
        └── rag_query.json
```

**Workflows disponibles** (después de `setup_rag_workflows.py`):

1. **RAG - Ingesta Completa de Documentos**
   - Nodos: 8
   - Webhook: `/webhook/rag/ingest`
   - Función: Procesar documentos y crear embeddings

2. **RAG - Sistema de Consultas Completo**
   - Nodos: 7
   - Webhook: `/webhook/rag/query`
   - Función: Responder preguntas con contexto

3. **RAG - Eliminar Documento**
   - Nodos: 5
   - Webhook: `/webhook/rag/document` (DELETE)
   - Función: Eliminar documentos del índice

**Uso**:
```bash
# Exportar workflow
python3 -c "
from scripts.n8n_manager import N8nManager
m = N8nManager('http://159.203.149.247:5678', 'API_KEY')
m.export_workflow('workflow_id', 'workflows/backup.json')
"

# Importar workflow
python3 -c "
from scripts.n8n_manager import N8nManager
m = N8nManager('http://159.203.149.247:5678', 'API_KEY')
m.import_workflow('workflows/backup.json')
"
```

---

## 📊 Estadísticas del Proyecto

### Archivos Creados
```
Total de archivos:    17
Archivos .md:         11 (documentación)
Archivos .py:         3  (scripts)
Archivos config:      2  (.env, requirements.txt)
Archivos meta:        1  (.gitignore)
```

### Líneas de Código
```
Scripts Python:       ~1,115 líneas
Documentación:        ~2,500 líneas
Total:                ~3,615 líneas
```

### Documentación
```
Páginas totales:      ~120 páginas
Tiempo lectura:       2-3 horas
Ejemplos de código:   20+ ejemplos
```

---

## 🎯 Guías de Navegación

### Por Rol

#### 👨‍💼 Manager / Product Owner
```
1. README.md (raíz)
2. docs/RESUMEN_EJECUTIVO.md
3. docs/INICIO_RAPIDO.md
```

#### 👨‍💻 Desarrollador
```
1. README.md (raíz)
2. docs/INICIO_RAPIDO.md
3. docs/ARQUITECTURA_RAG.md
4. docs/EJEMPLOS_USO.md
5. scripts/README.md
```

#### 🔧 DevOps / Implementador
```
1. README.md (raíz)
2. docs/CHECKLIST_IMPLEMENTACION.md
3. config/README.md
4. scripts/README.md
```

#### 🧪 QA / Tester
```
1. README.md (raíz)
2. docs/INICIO_RAPIDO.md
3. scripts/README.md (test_connection.py)
```

---

### Por Tarea

#### Quiero empezar rápido
```
1. README.md
2. docs/INICIO_RAPIDO.md
3. python3 scripts/test_connection.py
```

#### Quiero implementar el sistema
```
1. docs/CHECKLIST_IMPLEMENTACION.md (paso a paso)
2. config/README.md (configurar)
3. scripts/setup_rag_workflows.py (crear workflows)
```

#### Quiero integrar el RAG en mi app
```
1. docs/EJEMPLOS_USO.md (copiar código)
2. scripts/n8n_manager.py (ver cómo funciona)
```

#### Quiero presentar el proyecto
```
1. docs/RESUMEN_EJECUTIVO.md (presentación completa)
2. README.md (overview técnico)
```

---

## 🔍 Búsqueda Rápida de Información

| Necesito saber... | Archivo | Sección |
|-------------------|---------|---------|
| ¿Cómo empezar? | `docs/INICIO_RAPIDO.md` | Inicio |
| ¿Cuánto cuesta? | `docs/RESUMEN_EJECUTIVO.md` | Costos vs Beneficios |
| ¿Qué servicios Azure? | `docs/ARQUITECTURA_RAG.md` | Componentes Azure |
| ¿Cómo configurar? | `config/README.md` | Configuración |
| ¿Cómo hacer consultas? | `docs/EJEMPLOS_USO.md` | Consultas RAG |
| ¿Cómo probar el sistema? | `scripts/README.md` | test_connection.py |
| ¿Cuál es el ROI? | `docs/RESUMEN_EJECUTIVO.md` | ROI: 7,354% |
| ¿Cómo crear workflows? | `scripts/README.md` | setup_rag_workflows.py |
| ¿Cómo exportar workflows? | `workflows/README.md` | Exportar |

---

## 📦 Archivos No Incluidos (Generados)

Estos archivos se generan automáticamente y no están en Git:

```
.env                    # Variables de entorno (credenciales)
venv/                   # Virtual environment Python
__pycache__/            # Cache de Python
*.pyc                   # Bytecode Python
.DS_Store               # Metadatos macOS
```

---

## 🚀 Comandos Rápidos

### Setup Inicial
```bash
# 1. Instalar dependencias
pip install -r config/requirements.txt

# 2. Configurar ambiente
cp config/config_template.env .env
nano .env

# 3. Probar conexión
python3 scripts/test_connection.py

# 4. Crear workflows
python3 scripts/setup_rag_workflows.py
```

### Uso Diario
```bash
# Ver estado del sistema
python3 scripts/test_connection.py

# Listar workflows
python3 scripts/n8n_manager.py

# Backup de workflows
python3 -c "from scripts.n8n_manager import N8nManager; ..."
```

---

## 📞 Soporte

Si necesitas ayuda navegando el proyecto:

1. **Lee**: `README.md` (raíz) para overview general
2. **Consulta**: `docs/README.md` para índice de documentación
3. **Busca**: En este archivo (ESTRUCTURA.md) para ubicar información
4. **Ejecuta**: `python3 scripts/test_connection.py` para diagnóstico

---

## 📝 Contribuir

Al agregar archivos al proyecto:

1. **Documentación**: Agregar a `docs/`
2. **Scripts**: Agregar a `scripts/`
3. **Configuración**: Agregar a `config/`
4. **Workflows**: Exportar a `workflows/`
5. **Actualizar**: Este archivo y los README correspondientes

---

**Última actualización**: 21 de Octubre, 2025  
**Versión**: 1.0.0  
**Total de archivos**: 17  
**Estado**: ✅ Proyecto organizado y documentado

