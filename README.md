# QuickSort - Organizador Automático de Archivos

QuickSort es una aplicación web que utiliza una estructura de árbol para organizar automáticamente archivos según reglas personalizables basadas en extensiones y palabras clave.

## 🚀 Características

- **Estructura de Árbol**: Organización jerárquica de carpetas usando estructura de datos de árbol
- **Monitoreo Automático**: Detecta nuevos archivos en tiempo real
- **Reglas Personalizables**: Clasifica archivos por extensión, palabras clave, tamaño o fecha
- **Interfaz Web Moderna**: Frontend React con Material-UI
- **API REST**: Backend Flask con Python
- **Base de Datos**: SQLite para persistencia de configuración
- **Sistema de Logs**: Historial completo de operaciones

## 📋 Requisitos Previos

- Python 3.8 o superior
- Node.js 14 o superior
- npm o yarn

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
cd QuickSort
```

### 2. Configurar el Backend (Python/Flask)

```bash
# Navegar a la carpeta backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar el Frontend (React)

```bash
# Navegar a la carpeta frontend
cd ../frontend

# Instalar dependencias
npm install
```

## 🚀 Ejecución

### Iniciar el Backend

```bash
# Desde la carpeta backend con el entorno virtual activado
cd backend
python app.py
```

El servidor Flask se ejecutará en `http://localhost:5000`

### Iniciar el Frontend

```bash
# Desde la carpeta frontend en otra terminal
cd frontend
npm start
```

La aplicación React se abrirá en `http://localhost:3000`

## 📖 Uso

### 1. Configurar el Árbol de Carpetas

- Ve a la pestaña **"Árbol"**
- Crea nodos que representen las carpetas de destino
- Cada nodo puede tener hijos para crear una estructura jerárquica

### 2. Crear Reglas de Organización

- Ve a la pestaña **"Reglas"**
- Crea reglas para cada nodo:
  - **Extensión**: `.pdf`, `.jpg`, `.docx`, etc.
  - **Palabra clave**: `factura`, `reporte`, `contrato`, etc.
  - **Prioridad**: Mayor número = mayor prioridad

### 3. Configurar el Monitor

- Ve a la pestaña **"Monitor"**
- Configura la carpeta a monitorear (ej: Descargas)
- Activa/desactiva la organización automática
- Inicia el monitor

### 4. Ver Historial

- Ve a la pestaña **"Historial"**
- Revisa todas las operaciones realizadas
- Consulta estadísticas de éxito/fallos

## 🏗️ Estructura del Proyecto

```
QuickSort/
├── backend/
│   ├── app.py                 # Aplicación Flask principal
│   ├── models.py              # Modelos de base de datos
│   ├── tree_structure.py      # Implementación del árbol
│   ├── file_organizer.py      # Lógica de organización
│   ├── file_monitor.py        # Monitoreo de archivos
│   ├── config.py              # Configuración
│   ├── requirements.txt       # Dependencias Python
│   └── database.db            # Base de datos SQLite
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── TreeView.js    # Visualización del árbol
│   │   │   ├── FileMonitor.js # Control del monitor
│   │   │   ├── RuleManager.js # Gestión de reglas
│   │   │   └── LogViewer.js   # Visualización de logs
│   │   ├── services/
│   │   │   └── api.js         # Cliente API
│   │   ├── App.js             # Componente principal
│   │   └── index.js           # Punto de entrada
│   └── package.json           # Dependencias React
├── logs/                      # Archivos de log
└── README.md
```

## 🔧 API Endpoints

### Árbol
- `GET /api/tree` - Obtener estructura del árbol
- `GET /api/tree/nodes` - Obtener todos los nodos
- `POST /api/tree/nodes` - Crear nodo
- `DELETE /api/tree/nodes/:id` - Eliminar nodo

### Reglas
- `GET /api/rules` - Obtener todas las reglas
- `POST /api/rules` - Crear regla
- `PUT /api/rules/:id` - Actualizar regla
- `DELETE /api/rules/:id` - Eliminar regla

### Monitor
- `GET /api/monitor/status` - Estado del monitor
- `POST /api/monitor/start` - Iniciar monitor
- `POST /api/monitor/stop` - Detener monitor
- `GET /api/monitor/config` - Obtener configuración
- `PUT /api/monitor/config` - Actualizar configuración

### Organización
- `POST /api/organize/file` - Organizar archivo individual
- `POST /api/organize/folder` - Organizar carpeta
- `POST /api/organize/preview` - Previsualizar organización

### Logs
- `GET /api/logs` - Obtener historial
- `GET /api/logs/stats` - Obtener estadísticas

## 🎯 Ejemplo de Uso

### Ejemplo 1: Organizar PDFs

1. Crear nodo "Documentos PDF" con ruta `/Organized/PDFs`
2. Crear regla: Tipo = "Extensión", Patrón = ".pdf"
3. Iniciar monitor en carpeta "Descargas"
4. Cualquier PDF descargado se moverá automáticamente a `/Organized/PDFs`

### Ejemplo 2: Organizar por Palabra Clave

1. Crear nodo "Facturas" con ruta `/Organized/Facturas`
2. Crear regla: Tipo = "Palabra clave", Patrón = "factura"
3. Archivos con "factura" en el nombre se organizarán automáticamente

## 🛡️ Tecnologías Utilizadas

### Backend
- **Flask**: Framework web
- **SQLAlchemy**: ORM para base de datos
- **Watchdog**: Monitoreo de sistema de archivos
- **SQLite**: Base de datos

### Frontend
- **React**: Librería UI
- **Material-UI**: Componentes de interfaz
- **Axios**: Cliente HTTP
- **React Icons**: Iconos

## 📝 Notas Importantes

- El monitor debe estar activo para la organización automática
- Las reglas con mayor prioridad se evalúan primero
- Los archivos duplicados se renombran automáticamente
- Todos los movimientos se registran en el historial

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Autor

Desarrollado como proyecto universitario de Ingeniería - Estructura de Datos (Árboles)

## 🐛 Reporte de Bugs

Si encuentras algún bug, por favor abre un issue en el repositorio.

---

**QuickSort** - Organiza tus archivos automáticamente con el poder de los árboles 🌳
