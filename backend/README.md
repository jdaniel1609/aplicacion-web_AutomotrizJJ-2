# Automotriz JJ - Backend API

Sistema de gestión empresarial desarrollado con FastAPI.

## 🚀 Tecnologías Utilizadas

- **FastAPI** - Framework web moderno y rápido
- **Uvicorn** - Servidor ASGI
- **Python-JOSE** - JWT tokens
- **Passlib** - Encriptación de contraseñas
- **Pydantic** - Validación de datos
- **Python-Multipart** - Manejo de formularios

## 📦 Instalación y Configuración

### 1. Crear entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
APP_NAME="Automotriz JJ API"
APP_VERSION="1.0.0"
DEBUG=True

SECRET_KEY="tu_clave_secreta_super_segura_cambiala_en_produccion_123456789"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173"

DATABASE_URL="sqlite:///./automotriz_jj.db"

DEFAULT_USERNAME="admin"
DEFAULT_PASSWORD="admin123"
```

### 4. Ejecutar el servidor

```bash
# Modo desarrollo con auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Modo producción
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

La API estará disponible en: `http://localhost:8000`

## 📚 Documentación

Una vez que el servidor esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Autenticación

### Credenciales por Defecto

```
Usuario: admin
Contraseña: admin123
```

### Flujo de Autenticación

1. **Login**: `POST /auth/login`
   - Enviar credenciales mediante form data
   - Recibir token JWT

2. **Usar Token**: 
   - Incluir en header: `Authorization: Bearer <token>`

3. **Verificar Usuario**: `GET /auth/me`
   - Requiere token válido

## 🛠️ Endpoints Disponibles

### Públicos

```
GET  /              # Información de la API
GET  /health        # Estado del servidor
GET  /docs          # Documentación Swagger
```

### Autenticación

```
POST /auth/login    # Iniciar sesión
GET  /auth/me       # Información del usuario actual
POST /auth/logout   # Cerrar sesión
```

## 📁 Estructura del Proyecto

```
app/
├── main.py              # Punto de entrada
├── config.py            # Configuración
├── models/              # Modelos ORM
├── schemas/             # Esquemas Pydantic
│   ├── user.py
│   └── token.py
├── routes/              # Endpoints
│   └── auth.py
├── services/            # Lógica de negocio
│   └── auth_service.py
└── utils/               # Utilidades
    └── security.py
```

## 🔧 Desarrollo

### Agregar nuevos endpoints

1. Crear archivo en `app/routes/`
2. Definir router:
```python
from fastapi import APIRouter

router = APIRouter(prefix="/mi-ruta", tags=["Mi Tag"])

@router.get("/")
async def mi_endpoint():
    return {"message": "Hola"}
```

3. Incluir en `app/main.py`:
```python
from app.routes import mi_ruta
app.include_router(mi_ruta.router)
```

### Agregar validación con Pydantic

```python
from pydantic import BaseModel, Field

class MiModelo(BaseModel):
    nombre: str = Field(..., min_length=3)
    edad: int = Field(..., gt=0, lt=150)
```

## 🧪 Pruebas

### Probar con cURL

```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Obtener usuario actual
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <tu_token>"
```

### Probar con Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Usar token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/auth/me",
    headers=headers
)
print(response.json())
```

## 🔒 Seguridad

### Mejores Prácticas Implementadas

✅ **Contraseñas hasheadas** con bcrypt
✅ **JWT tokens** con expiración
✅ **CORS configurado** correctamente
✅ **Validación de datos** con Pydantic
✅ **Variables de entorno** para configuración sensible

### Para Producción

⚠️ **IMPORTANTE**: Antes de desplegar en producción:

1. **Cambiar SECRET_KEY** a un valor seguro y único
2. **Usar base de datos real** (PostgreSQL, MySQL, etc.)
3. **Configurar HTTPS** con certificados SSL
4. **Limitar CORS** a dominios específicos
5. **Agregar rate limiting** para prevenir ataques
6. **Implementar logging** adecuado
7. **Usar variables de entorno** reales (no .env)

## 🐳 Docker (Opcional)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY .env .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
    volumes:
      - ./app:/app/app
```

### Ejecutar con Docker

```bash
# Construir y ejecutar
docker-compose up --build

# Solo ejecutar
docker-compose up
```

## 📊 Monitoreo

### Endpoints de Salud

```bash
# Verificar estado
curl http://localhost:8000/health

# Respuesta esperada:
{
  "status": "healthy",
  "service": "Automotriz JJ API",
  "version": "1.0.0"
}
```

## 🔄 Integración con Frontend

El backend está configurado para trabajar con el frontend React en:
- `http://localhost:3000` (Create React App)
- `http://localhost:5173` (Vite)

### Configurar CORS para otros orígenes

Edita `.env`:
```env
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173,https://mi-dominio.com"
```

## 📝 Logs

Los logs se muestran en la consola durante el desarrollo:

```bash
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🚀 Iniciando Automotriz JJ API v1.0.0
📝 Documentación disponible en: http://localhost:8000/docs
🔐 Usuario de prueba: admin
INFO:     Application startup complete.
```

## ❓ Solución de Problemas

### Error: "ModuleNotFoundError"
```bash
# Asegúrate de estar en el entorno virtual
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "Port already in use"
```bash
# Cambiar puerto
uvicorn app.main:app --reload --port 8001
```

### Error: "CORS policy"
```bash
# Verificar ALLOWED_ORIGINS en .env
# Debe incluir el origen del frontend
```

## 📞 Soporte

Para reportar problemas o sugerencias, contacta al equipo de desarrollo.

---

**Desarrollado para Automotriz JJ** - Sistema de Gestión Empresarial