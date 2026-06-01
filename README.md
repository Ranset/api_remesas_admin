# 💸 Remesas Admin API

API REST para la administración y control de un negocio de remesas. Permite gestionar grupos de trabajo, crear y asignar órdenes a gestores, hacer seguimiento de su estado y obtener estadísticas de operaciones por periodos.

---

## 🚀 Características principales

- **Autenticación JWT** con registro, verificación por correo y recuperación de contraseña
- **Gestión de usuarios** con roles y perfiles personalizables
- **Grupos de trabajo** con asignación de múltiples usuarios y roles
- **Órdenes de remesas** con ciclo de vida completo (activa → ejecutada / cancelada)
- **Notificaciones push** mediante Firebase Cloud Messaging
- **Estadísticas** de órdenes por grupo y periodo (últimos 3 meses)
- **Exportación a Excel** de las estadísticas detalladas
- **Envío de correos transaccionales** vía Mailjet

---

## 🛠️ Stack tecnológico

| Componente | Tecnología |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org/) |
| Base de datos | PostgreSQL (Supabase) |
| Autenticación | JWT (`PyJWT`) + `passlib` (bcrypt) |
| Correo | [Mailjet REST](https://github.com/mailjet/mailjet-apiv3-python) |
| Push Notifications | [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup) |
| Exportación | `openpyxl` |
| Variables de entorno | `python-dotenv` |

---

## 📁 Estructura del proyecto

```
remesas-admin/
│
├── main.py                          # Punto de entrada, definición de rutas FastAPI
├── modulos/
│   ├── __init__.py
│   ├── auth.py                      # Lógica de autenticación y JWT
│   ├── config.py                    # Carga de variables de entorno
│   ├── date_utility.py              # Utilidades de fecha y generación de códigos
│   ├── mailjet_email.py             # Envío de correos transaccionales
│   ├── models.py                    # Modelos SQLAlchemy, Pydantic y funciones de DB
│   ├── notifications.py             # Envío de notificaciones push con Firebase
│   └── statics.py                   # Estadísticas y exportación a Excel
└── .env                             # Variables de entorno
```

---

## ⚙️ Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/remesas-admin.git
cd remesas-admin
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
# Base de datos (Supabase / PostgreSQL)
DB_URL=your-db-host:port
SUPABASE_DB_NAME=your-db-name
SUPABASE_USER=your-db-user
SUPABASE_PASSWORD=your-db-password

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTESS=10080   # 7 días en minutos

# Mailjet
MJ_APIKEY_PUBLIC=your-mailjet-public-key
MJ_APIKEY_PRIVATE=your-mailjet-private-key
```

### 5. Configurar Firebase

Coloca el archivo de credenciales del servicio de Firebase en:

```
modulos/remesa-admin-firebase-adminsdk-xxxxx.json
```

### 6. Levantar el servidor

```bash
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000`.

La documentación interactiva (Swagger) en `http://localhost:8000/docs`.

---

## 📌 Endpoints principales

### 🔐 Auth

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/auth/register` | Registro de usuario |
| `POST` | `/api/auth/verify_email` | Verificación de correo con código |
| `POST` | `/api/auth/resend_verification_code` | Reenviar código de verificación |
| `POST` | `/api/auth/login` | Inicio de sesión (retorna JWT) |
| `POST` | `/api/auth/forgot_password` | Recuperación / restablecimiento de contraseña |

### 👤 Usuarios

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/user/{nickname}` | Obtener usuario por nickname |
| `PATCH` | `/api/user/{user_id}` | Actualizar datos del usuario |
| `DELETE` | `/api/user/{user_id}` | Eliminar usuario |
| `GET` | `/api/user/roles/getall` | Listar todos los roles disponibles |

### 👥 Grupos

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/groups` | Crear grupo |
| `GET` | `/api/groups/{group_id}` | Obtener detalle del grupo |
| `GET` | `/api/groups/user/{user_id}` | Listar grupos de un usuario |
| `PUT` | `/api/groups` | Actualizar grupo |
| `DELETE` | `/api/groups/{group_id}` | Eliminar grupo |

### 📦 Órdenes

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/order/products` | Listar productos disponibles |
| `POST` | `/api/order` | Crear orden |
| `PUT` | `/api/order/{order_id}` | Actualizar orden (incluyendo estado) |

### 📊 Estadísticas

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/order/statics/{group_id}` | Estadísticas de los últimos 3 meses |
| `GET` | `/api/order/statics/{group_id}/download` | Descargar estadísticas en Excel |

> Todos los endpoints (excepto los de auth) requieren el header `Authorization: Bearer <token>`.

---

## 🔐 Autenticación

La API utiliza **JWT Bearer tokens**. Tras el login, incluye el token en cada petición:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Los tokens tienen una validez de **7 días**.

---

## 📧 Flujo de registro

```
1. POST /api/auth/register       → se envía código de verificación al correo
2. POST /api/auth/verify_email   → se activa la cuenta con el código de 4 dígitos
3. POST /api/auth/login          → se obtiene el JWT para operar
```

---

## 📊 Estados de una orden

| Estado | Descripción |
|---|---|
| `active` | Orden creada y pendiente de ejecución |
| `executed` | Orden ejecutada por el gestor |
| `cancelled` | Orden cancelada |

---

## 🔒 Seguridad

- Las contraseñas se almacenan hasheadas con **bcrypt**.
- Los tokens JWT expiran automáticamente.
- Los códigos de verificación por correo expiran en **24 horas**.

---

## 📄 Licencia

Este proyecto es de uso privado. Todos los derechos reservados.