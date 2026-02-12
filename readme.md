# 🚗 Autos Ruta Capital - Sistema Web de Gestión y Alquiler de Vehículos

## 📌 Descripción del Proyecto

C&C Auto Online es una aplicación web desarrollada con **Python (Flask), HTML, CSS y JavaScript**, que permite la gestión y visualización de una flota de vehículos para alquiler.

El sistema incluye:

- Visualización pública de vehículos
- Sistema de registro e inicio de sesión
- Panel administrativo
- Gestión de vehículos
- Gestión de usuarios
- Base de datos relacional
- Sistema de autenticación

Esta versión ya no es solo frontend. Es una aplicación web completa con backend y base de datos.

---

## 🛠️ Tecnologías Utilizadas

### Backend
- Python 3
- Flask
- SQL (Base de datos relacional)

### Frontend
- HTML5
- CSS3
- JavaScript

### Base de Datos
- Archivo `concesionario.sql`

---

## 📂 Estructura del Proyecto

```
PROYECTO/
│
├── app.py
├── concesionario.sql
├── requirements.txt
├── readme.md
│
├── static/
│   ├── Media/
│   ├── uploads/
│   ├── carrusel.js
│   ├── filtro.js
│   ├── styles.css
│   ├── flota-styles.css
│   ├── dark-mode.css
│
├── templates/
│   ├── index.html
│   ├── flota.html
│   ├── login.html
│   ├── register.html
│   ├── registro_exitoso.html
│   ├── dashboard.html
│   ├── admin_panel.html
│   ├── edit_usuario.html
│   ├── edit_vehiculo.html
│   ├── guia_usuario.html
│   ├── construction.html
```

---

## 🔐 Funcionalidades del Sistema

### 👤 Usuarios

- Registro de usuario
- Inicio de sesión
- Edición de perfil
- Gestión desde panel administrativo

### 🚘 Vehículos

- Visualización de flota
- Filtrado por categorías
- Gestión de vehículos (admin)
- Edición de vehículos

### 🛠️ Administración

- Panel de control
- Gestión de usuarios
- Gestión de vehículos
- Sistema de autenticación

---

## 🧠 Cómo Funciona el Sistema

### 1️⃣ Backend (`app.py`)

El archivo `app.py` contiene:

- Configuración de Flask
- Rutas del sistema
- Conexión con la base de datos
- Lógica de autenticación
- Gestión de sesiones
- CRUD de usuarios y vehículos

Flask renderiza las vistas ubicadas en la carpeta `templates`.

---

### 2️⃣ Carpeta `templates/`

Contiene las vistas HTML renderizadas por Flask.

Cada archivo corresponde a una ruta del sistema:

- `index.html` → Página principal
- `login.html` → Inicio de sesión
- `register.html` → Registro
- `dashboard.html` → Panel de usuario
- `admin_panel.html` → Panel administrador
- etc.

---

### 3️⃣ Carpeta `static/`

Contiene los recursos estáticos:

- Archivos CSS
- Archivos JavaScript
- Imágenes
- Archivos subidos por usuarios

Flask los sirve automáticamente.

---

### 4️⃣ Base de Datos

El archivo `concesionario.sql` contiene:

- Estructura de tablas
- Relaciones
- Datos iniciales (si aplica)

Se utiliza para almacenar:

- Usuarios
- Vehículos
- Información del sistema

---

## 🚀 Cómo Ejecutar el Proyecto

### 1️⃣ Clonar el repositorio

```
git clone <URL_DEL_REPOSITORIO>
```

### 2️⃣ Crear entorno virtual

```
python -m venv venv
```

### 3️⃣ Activar entorno virtual

Windows:
```
venv\Scripts\activate
```

Mac/Linux:
```
source venv/bin/activate
```

### 4️⃣ Instalar dependencias

```
pip install -r requirements.txt
```

### 5️⃣ Configurar la base de datos

- Crear base de datos
- Importar el archivo `concesionario.sql`

### 6️⃣ Ejecutar la aplicación

```
python app.py
```

Luego abrir en el navegador:

```
http://127.0.0.1:5000
```

---

## 📌 Características Técnicas

- Arquitectura MVC (Flask + Templates)
- CRUD completo
- Autenticación de usuarios
- Manejo de sesiones
- Separación backend / frontend
- Gestión de archivos subidos
- Estructura escalable

---

## 🔮 Posibles Mejoras Futuras

- Sistema de reservas en tiempo real
- Integración con pasarela de pagos
- API REST
- Autenticación con JWT
- Roles y permisos más avanzados
- Despliegue en servidor cloud

---

## 👨‍💻 Autor: Ivan Carrasco: Octubre 2025

Proyecto académico desarrollado como aplicación web completa utilizando Flask.
