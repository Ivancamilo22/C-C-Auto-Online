# 🚗 Proyecto Web - Sistema de Visualización de Flota de Vehículos

## 📌 Descripción del Proyecto

Este proyecto es una aplicación web estática desarrollada con **HTML, CSS y JavaScript puro**, cuyo propósito es mostrar una flota de vehículos de manera interactiva y organizada.

El sistema permite:

- Visualizar vehículos disponibles
- Filtrar vehículos por categoría
- Mostrar imágenes dinámicas mediante un carrusel automático
- Navegar entre secciones del sitio

Es una solución pensada para empresas de alquiler de autos, concesionarios o catálogos digitales de vehículos.

---

## 🎯 Objetivo

Proporcionar una interfaz clara y dinámica para que los usuarios puedan:

- Explorar diferentes tipos de vehículos
- Filtrar por categorías específicas
- Visualizar imágenes destacadas automáticamente

Sin necesidad de backend ni base de datos.

---

## 🛠️ Tecnologías Utilizadas

- **HTML5** → Estructura del sitio
- **CSS3** → Diseño y estilos visuales
- **JavaScript (Vanilla JS)** → Interactividad y comportamiento dinámico

No se utilizan frameworks ni librerías externas.

---

## 📂 Estructura del Proyecto

```
/proyecto
│
├── index.html
├── flota.html
│
├── styles.css
├── flota-styles.css
│
├── carrusel.js
├── filtro.js
│
└── README.md
```

---

## 🔎 Funcionamiento del Proyecto

### 1️⃣ Página Principal (`index.html`)

Contiene:

- Sección principal con imágenes destacadas
- Carrusel automático de imágenes
- Navegación hacia la sección de flota

El carrusel funciona mediante `carrusel.js`.

---

### 2️⃣ Sistema de Carrusel (`carrusel.js`)

Este archivo:

- Espera a que el DOM cargue completamente
- Selecciona las imágenes dentro del contenedor `.slider-container`
- Alterna la clase `active` cada 5 segundos
- Crea un efecto de rotación automática

Lógica principal:

- Se guarda el índice actual
- Se elimina la clase `active`
- Se calcula la siguiente imagen
- Se activa la nueva imagen

El cambio ocurre cada **5000 ms (5 segundos)** usando `setInterval`.

---

### 3️⃣ Página de Flota (`flota.html`)

Contiene:

- Tarjetas de vehículos (`.car-card`)
- Botones de categoría (`.category-btn`)
- Atributos `data-category` para clasificar vehículos

---

### 4️⃣ Sistema de Filtro (`filtro.js`)

Este archivo permite:

- Filtrar vehículos según la categoría seleccionada
- Activar visualmente el botón seleccionado
- Mostrar u ocultar tarjetas dinámicamente

Funcionamiento:

1. Detecta clic en un botón
2. Obtiene el valor `data-category`
3. Recorre todas las tarjetas
4. Muestra solo las que coinciden
5. Si la categoría es `all`, muestra todas

No recarga la página.
No requiere servidor.

---

## 🎨 Estilos

- `styles.css` → Estilos generales del sitio
- `flota-styles.css` → Estilos específicos de la sección de flota

Incluyen:

- Diseño responsivo
- Efectos visuales
- Estados activos
- Organización visual de tarjetas

---

## 🚀 Cómo Ejecutar el Proyecto

1. Descargar o clonar el repositorio
2. Abrir el archivo `index.html` en cualquier navegador moderno

No se necesita:

- Servidor
- Base de datos
- Instalación de dependencias

Es 100% frontend.

---

## 📌 Características Técnicas Implementadas

- Manipulación del DOM
- Uso de `data-attributes`
- Uso de `classList`
- Eventos `addEventListener`
- Uso de `setInterval`
- Separación de responsabilidades (HTML / CSS / JS)

---

## 🔮 Posibles Mejoras Futuras

- Integración con backend y base de datos
- Sistema de reservas en línea
- Panel administrativo
- Búsqueda avanzada
- Paginación de resultados
- Animaciones más avanzadas
- Implementación con framework moderno (React / Vue)

---

## 👨‍💻 Autor: Ivan Camilo Carrasco Cano Marzo 2025

Proyecto desarrollado como práctica de desarrollo web frontend.
