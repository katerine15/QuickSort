# 🚀 Cómo Ejecutar QuickSort

## ✅ Estado Actual del Proyecto

- ✅ Todos los archivos creados
- ✅ Entorno virtual Python creado
- ✅ Dependencias Python instaladas
- ✅ Dependencias React instalándose

## 📋 Pasos para Ejecutar

### 1️⃣ Iniciar el Backend (Flask)

Abre una terminal y ejecuta:

```bash
# Navegar a la carpeta backend
cd QuickSort/backend

# Activar entorno virtual
# En PowerShell (si tienes permisos):
.\venv\Scripts\Activate.ps1

# O en CMD:
venv\Scripts\activate.bat

# Ejecutar el servidor Flask
python app.py
```

El backend estará disponible en: **http://localhost:5000**

### 2️⃣ Iniciar el Frontend (React)

Abre **OTRA terminal nueva** y ejecuta:

```bash
# Navegar a la carpeta frontend
cd QuickSort/frontend

# Iniciar el servidor React
npm start
```

El frontend se abrirá automáticamente en: **http://localhost:3000**

## 🎯 Primer Uso

Una vez que ambos servidores estén corriendo:

1. **Accede a http://localhost:3000** en tu navegador

2. **Pestaña "Árbol"**: 
   - Crea tu primer nodo (carpeta de destino)
   - Ejemplo: Nombre: "PDFs", Ruta: "C:/Organized/PDFs"

3. **Pestaña "Reglas"**:
   - Crea una regla para el nodo
   - Ejemplo: Tipo: "Extensión", Patrón: ".pdf"

4. **Pestaña "Monitor"**:
   - Configura la carpeta a monitorear (ej: tu carpeta de Descargas)
   - Activa "Organizar automáticamente"
   - Haz clic en "Iniciar Monitor"

5. **¡Listo!** Cualquier archivo que cumpla las reglas se organizará automáticamente

## 🔧 Solución de Problemas

### Error: "No se puede cargar el archivo Activate.ps1"
**Solución**: Usa `venv\Scripts\activate.bat` en su lugar

### Error: "Puerto 5000 en uso"
**Solución**: Cambia el puerto en `backend/app.py` (última línea)

### Error: "Puerto 3000 en uso"
**Solución**: React te preguntará si quieres usar otro puerto, acepta

### Error: "Cannot connect to backend"
**Solución**: Asegúrate de que el backend esté corriendo en http://localhost:5000

## 📊 Verificar que Todo Funciona

1. Backend: Visita http://localhost:5000/api/health
   - Deberías ver: `{"status": "ok", "message": "QuickSort API is running"}`

2. Frontend: Visita http://localhost:3000
   - Deberías ver la interfaz de QuickSort

## 🛑 Detener los Servidores

- **Backend**: Presiona `Ctrl + C` en la terminal del backend
- **Frontend**: Presiona `Ctrl + C` en la terminal del frontend

## 💡 Consejos

- Mantén ambas terminales abiertas mientras uses la aplicación
- Los logs del backend aparecerán en su terminal
- Los errores del frontend aparecerán en la consola del navegador (F12)
- La base de datos se crea automáticamente en `backend/database.db`

## 📝 Comandos Rápidos

### Backend
```bash
cd QuickSort/backend
venv\Scripts\activate.bat
python app.py
```

### Frontend
```bash
cd QuickSort/frontend
npm start
```

---

**¡Disfruta organizando tus archivos automáticamente con QuickSort! 🌳**
