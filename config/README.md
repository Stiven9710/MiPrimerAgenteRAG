# ⚙️ Configuración del Proyecto

Esta carpeta contiene los archivos de configuración necesarios para el sistema RAG.

## 📋 Archivos

### 1. `requirements.txt`
**Descripción**: Lista de dependencias Python del proyecto.

**Contenido**:
```
requests==2.31.0              # Cliente HTTP para APIs
python-dotenv==1.0.0          # Cargar variables de entorno
azure-storage-blob==12.19.0   # Azure Blob Storage
azure-cosmos==4.5.1           # Azure Cosmos DB
openai==1.12.0                # OpenAI/Azure OpenAI
pypdf2==3.0.1                 # Procesamiento de PDFs
pdfplumber==0.10.3            # Extracción avanzada de PDFs
langchain==0.1.10             # Framework RAG
langchain-openai==0.0.6       # Integración LangChain + OpenAI
```

**Instalación**:
```bash
# Opción 1: pip estándar
pip install -r config/requirements.txt

# Opción 2: en virtual environment (recomendado)
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r config/requirements.txt

# Opción 3: con usuario específico
pip install --user -r config/requirements.txt
```

---

### 2. `config_template.env`
**Descripción**: Template de variables de entorno para configuración de Azure y n8n.

**Uso**:

#### Paso 1: Copiar el template
```bash
cp config/config_template.env .env
```

#### Paso 2: Editar con tus credenciales
```bash
# Opción 1: Editor de texto
nano .env

# Opción 2: VS Code / Cursor
code .env
```

#### Paso 3: Configurar variables
```env
# n8n
N8N_URL=http://159.203.149.247:5678
N8N_API_KEY=tu_api_key_real_aqui

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com
AZURE_OPENAI_KEY=tu_key_aqui
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_GPT_DEPLOYMENT=gpt-4

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://tu-search.search.windows.net
AZURE_SEARCH_KEY=tu_key_aqui
AZURE_SEARCH_INDEX=rag-documents

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...

# Azure Cosmos DB
COSMOS_DB_ENDPOINT=https://tu-cosmos.documents.azure.com:443/
COSMOS_DB_KEY=tu_key_aqui
COSMOS_DB_DATABASE=rag-system

# Azure Document Intelligence
AZURE_FORM_RECOGNIZER_ENDPOINT=https://tu-recurso.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY=tu_key_aqui

# Configuración RAG
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
TEMPERATURE=0.3
MAX_TOKENS=800
```

#### Paso 4: Cargar en tu shell
```bash
# Bash/Zsh
export $(cat .env | xargs)

# Fish shell
export (cat .env | xargs)

# Windows PowerShell
Get-Content .env | ForEach-Object {
    $name, $value = $_.split('=')
    Set-Content env:\$name $value
}
```

#### Paso 5: Verificar que se cargaron
```bash
echo $AZURE_OPENAI_ENDPOINT
echo $N8N_URL
```

---

## 🔐 Seguridad

### ⚠️ IMPORTANTE: Proteger Credenciales

El archivo `.env` contiene credenciales sensibles y **NUNCA** debe commitearse a Git.

**Verificar que `.gitignore` incluye**:
```gitignore
.env
.env.local
.env.*.local
```

**Buenas prácticas**:
1. ✅ Usar `.env` solo en desarrollo local
2. ✅ En producción, usar variables de entorno del sistema o secrets manager
3. ✅ Rotar keys periódicamente
4. ✅ Usar diferentes keys por ambiente (dev/staging/prod)
5. ❌ NUNCA hardcodear keys en código
6. ❌ NUNCA commitear `.env` a Git
7. ❌ NUNCA compartir `.env` por email/Slack

---

## 📦 Gestión de Dependencias

### Agregar nueva dependencia

1. Instalar el paquete:
```bash
pip install nombre-paquete==version
```

2. Actualizar requirements.txt:
```bash
pip freeze | grep nombre-paquete >> config/requirements.txt
```

3. O editarlo manualmente:
```
nombre-paquete==1.2.3
```

### Actualizar dependencias

```bash
# Ver versiones actuales
pip list

# Actualizar paquete específico
pip install --upgrade nombre-paquete

# Actualizar requirements.txt
pip freeze > config/requirements.txt
```

### Verificar vulnerabilidades

```bash
# Instalar safety
pip install safety

# Escanear dependencias
safety check -r config/requirements.txt
```

---

## 🌍 Variables de Entorno en n8n

Algunas variables también se configuran en n8n:

### Opción 1: Via docker-compose.yml
```yaml
services:
  n8n:
    environment:
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_KEY=${AZURE_OPENAI_KEY}
      - AZURE_SEARCH_ENDPOINT=${AZURE_SEARCH_ENDPOINT}
      # ... resto de variables
```

### Opción 2: Via archivo .env de n8n
```bash
# En el servidor donde corre n8n
nano /path/to/n8n/.env
```

### Opción 3: Variables de workflow
En n8n, puedes usar variables en nodos con:
```
{{ $env.AZURE_OPENAI_ENDPOINT }}
{{ $env.AZURE_OPENAI_KEY }}
```

---

## 🎯 Configuración por Ambiente

### Desarrollo
```bash
cp config/config_template.env .env.development
# Editar con valores de desarrollo
export $(cat .env.development | xargs)
```

### Staging
```bash
cp config/config_template.env .env.staging
# Editar con valores de staging
export $(cat .env.staging | xargs)
```

### Producción
```bash
# No usar archivo .env en producción
# Configurar variables directamente en el sistema
export AZURE_OPENAI_ENDPOINT="https://prod.openai.azure.com"
export AZURE_OPENAI_KEY="prod_key_here"
# ...
```

---

## 🔍 Verificación de Configuración

### Script de verificación

```python
import os

required_vars = [
    'AZURE_OPENAI_ENDPOINT',
    'AZURE_OPENAI_KEY',
    'AZURE_SEARCH_ENDPOINT',
    'AZURE_SEARCH_KEY',
    'COSMOS_DB_ENDPOINT',
    'COSMOS_DB_KEY'
]

missing = []
for var in required_vars:
    if not os.getenv(var):
        missing.append(var)

if missing:
    print("❌ Variables faltantes:")
    for var in missing:
        print(f"  - {var}")
else:
    print("✅ Todas las variables configuradas")
```

Guardar como `check_config.py` y ejecutar:
```bash
python3 check_config.py
```

---

## 📝 Template de Configuración Mínima

Si solo quieres probar sin Azure:

```env
# Mínimo para n8n
N8N_URL=http://159.203.149.247:5678
N8N_API_KEY=tu_api_key

# Resto opcional si solo exploras workflows
```

---

## 🆘 Solución de Problemas

### Error: "ModuleNotFoundError"
```bash
# Reinstalar dependencias
pip install -r config/requirements.txt
```

### Error: Variable de entorno no encontrada
```bash
# Verificar que el .env esté cargado
echo $AZURE_OPENAI_ENDPOINT

# Si está vacío, cargar:
export $(cat .env | xargs)
```

### Error: "Invalid credentials"
- Verificar que las keys sean correctas
- Verificar que no haya espacios extras en .env
- Verificar que las keys no hayan expirado

### Conflicto de versiones
```bash
# Crear virtual environment limpio
python3 -m venv venv_new
source venv_new/bin/activate
pip install -r config/requirements.txt
```

---

## 📞 Referencias

- **Python dotenv**: https://pypi.org/project/python-dotenv/
- **Azure SDK**: https://learn.microsoft.com/python/api/overview/azure/
- **n8n Environment Variables**: https://docs.n8n.io/hosting/configuration/

---

**Comienza copiando `config_template.env` a `.env` y configurando tus credenciales! 🔐**

