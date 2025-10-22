@echo off
echo ========================================
echo Iniciando Backend de QuickSort
echo ========================================
echo.
echo El servidor estara disponible en: http://localhost:5000
echo Presiona Ctrl+C para detener el servidor
echo.

cd /d "%~dp0backend"
python app.py

pause
