# 🪟 Instrucciones para Windows - QuickSort

## ⚠️ Problema Detectado

Windows PowerShell tiene restricciones de seguridad que impiden ejecutar scripts de activación de entornos virtuales.

---

## ✅ Solución Simple (Recomendada)

### Opción 1: Usar los Scripts .BAT (MÁS FÁCIL)

He creado scripts especiales para Windows que no requieren configuración adicional:

#### 1. Instalar Todo Automáticamente
```cmd
Haz doble clic en: INSTALAR_WINDOWS.bat
```

Este script:
- ✅ Instala dependencias de Python
- ✅ Inicializa la base de datos
- ✅ Instala dependencias de Node.js

#### 2. Ejecutar el Backend
```cmd
Haz doble clic en: EJECUTAR_BACKEND.bat
```

#### 3. Ejecutar el Frontend (en otra ventana)
```cmd
Haz doble clic en: EJECUTAR_FRONTEND.bat
```

---

### Opción 2: Comandos Manuales

Si prefieres ejecutar comandos manualmente:

#### 1. Instalar Dependencias de Python
```cmd
cd QuickSort\backend
pip install Flask Flask-CORS Flask-SQLAlchemy watchdog python-dotenv
```

#### 2. Inicializar Base de Datos
```cmd
cd QuickSort\backend
python init_db.py
```

#### 3. Instalar Dependencias de Node.js
```cmd
cd QuickSort\frontend
npm install
```

#### 4. Ejecutar Backend
```cmd
cd QuickSort\backend
python app.py
```

#### 5. Ejecutar Frontend (en otra terminal)
```cmd
cd QuickSort\frontend
npm start
```

---

## 🔧 Solución al Problema de PowerShell (Opcional)

Si quieres habilitar la ejecución de scripts en PowerShell:

### Paso 1: Abrir PowerShell como Administrador
1. Busca "PowerShell" en el menú inicio
2. Clic derecho → "Ejecutar como administrador"

### Paso 2: Cambiar la Política de Ejecución
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Paso 3: Confirmar
Escribe `Y` y presiona Enter

### Paso 4: Ahora puedes activar el entorno virtual
```powershell
cd QuickSort\backend
.\venv\Scripts\Activate.ps1
```

---

## 📊 Estado Actual de Instalación

Según los logs, necesitas:

1. ✅ **Python instalado**: Detectado en C:\Python311
2. ⏳ **Dependencias de Python**: Instalándose ahora
3. ❓ **Node.js**: Verificar si está instalado
4. ❓ **Dependencias de Node.js**: Pendiente

---

## 🚀 Inicio Rápido (Después de Instalar)

### Método 1: Scripts BAT (Recomendado)
1. Doble clic en `EJECUTAR_BACKEND.bat`
2. Doble clic en `EJECUTAR_FRONTEND.bat`
3. Abre http://localhost:3000 en tu navegador

### Método 2: Línea de Comandos
```cmd
# Terminal 1 - Backend
cd QuickSort\backend
python app.py

# Terminal 2 - Frontend
cd QuickSort\frontend
npm start
```

---

## 🐛 Solución de Problemas Comunes

### Error: "python no se reconoce como comando"
**Solución**: Instala Python desde https://www.python.org/downloads/
- ✅ Marca la opción "Add Python to PATH" durante la instalación

### Error: "npm no se reconoce como comando"
**Solución**: Instala Node.js desde https://nodejs.org/
- Descarga la versión LTS (recomendada)

### Error: "ModuleNotFoundError: No module named 'flask'"
**Solución**: 
```cmd
pip install Flask Flask-CORS Flask-SQLAlchemy watchdog
```

### Error: "Port 5000 already in use"
**Solución**: 
1. Cierra otras aplicaciones que usen el puerto 5000
2. O cambia el puerto en `backend/app.py` (última línea)

### Error: "Cannot connect to backend"
**Solución**: 
1. Verifica que el backend esté ejecutándose
2. Verifica que no haya errores en la terminal del backend
3. Intenta acceder a http://localhost:5000/api/health

---

## ✅ Verificación de Instalación

Para verificar que todo está instalado correctamente:

```cmd
# Verificar Python
python --version

# Verificar pip
pip --version

# Verificar Node.js
node --version

# Verificar npm
npm --version

# Verificar Flask
python -c "import flask; print(flask.__version__)"
```

---

## 📝 Notas Importantes

1. **No cierres las terminales** mientras los servidores estén ejecutándose
2. **Backend primero**: Siempre inicia el backend antes que el frontend
3. **Puerto 5000**: El backend usa el puerto 5000
4. **Puerto 3000**: El frontend usa el puerto 3000
5. **Ctrl+C**: Para detener los servidores, presiona Ctrl+C en cada terminal

---

## 🎯 Próximos Pasos

Una vez que ambos servidores estén corriendo:

1. ✅ Abre http://localhost:3000
2. ✅ Crea tu primer nodo en la pestaña "Árbol"
3. ✅ Define una regla en la pestaña "Reglas"
4. ✅ Configura el monitor en la pestaña "Monitor"
5. ✅ ¡Prueba organizando archivos!

---

## 📞 Ayuda Adicional

Si sigues teniendo problemas:

1. Revisa `ERRORES_Y_CORRECCIONES.md` para errores conocidos
2. Revisa `PASOS_FINALES.md` para instrucciones generales
3. Verifica los logs en la terminal para mensajes de error específicos

---

**Creado específicamente para Windows**
**Última actualización**: Correcciones aplicadas y scripts BAT creados
