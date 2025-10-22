# Guía de Instalación Rápida - QuickSort

## Pasos de Instalación

### 1. Backend (Python/Flask)

```bash
# Navegar a la carpeta del proyecto
cd QuickSort/backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Activar entorno virtual (Linux/Mac)
# source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos y ejecutar
python app.py
```

### 2. Frontend (React)

Abrir una nueva terminal:

```bash
# Navegar a la carpeta frontend
cd QuickSort/frontend

# Instalar dependencias
npm install

# Iniciar aplicación
npm start
```

## Verificación

- Backend: http://localhost:5000/api/health
- Frontend: http://localhost:3000

## Solución de Problemas

### Error: Python no encontrado
- Instalar Python 3.8+ desde python.org
- Verificar: `python --version`

### Error: npm no encontrado
- Instalar Node.js desde nodejs.org
- Verificar: `node --version` y `npm --version`

### Error: Puerto en uso
- Backend: Cambiar puerto en `backend/app.py` (línea final)
- Frontend: Cambiar puerto con variable de entorno `PORT=3001 npm start`

### Error: Módulos no encontrados
- Backend: Asegurarse de activar el entorno virtual
- Frontend: Ejecutar `npm install` nuevamente

## Primer Uso

1. Acceder a http://localhost:3000
2. Ir a pestaña "Árbol" y crear nodos
3. Ir a pestaña "Reglas" y crear reglas
4. Ir a pestaña "Monitor" y configurar carpeta
5. Iniciar el monitor
6. ¡Listo! Los archivos se organizarán automáticamente
