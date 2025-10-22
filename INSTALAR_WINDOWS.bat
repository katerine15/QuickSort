@echo off
echo ========================================
echo Instalando Dependencias de QuickSort
echo ========================================
echo.

echo [1/3] Instalando dependencias de Python...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias de Python
    pause
    exit /b 1
)
echo.

echo [2/3] Inicializando base de datos...
python init_db.py
if %errorlevel% neq 0 (
    echo ERROR: No se pudo inicializar la base de datos
    pause
    exit /b 1
)
echo.

echo [3/3] Instalando dependencias de Node.js...
cd ..\frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias de Node.js
    pause
    exit /b 1
)
echo.

cd ..
echo ========================================
echo INSTALACION COMPLETADA EXITOSAMENTE!
echo ========================================
echo.
echo Para ejecutar el proyecto:
echo 1. Abre una terminal y ejecuta: cd QuickSort\backend ^&^& python app.py
echo 2. Abre OTRA terminal y ejecuta: cd QuickSort\frontend ^&^& npm start
echo.
pause
