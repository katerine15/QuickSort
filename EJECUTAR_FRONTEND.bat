@echo off
echo ========================================
echo Iniciando Frontend de QuickSort
echo ========================================
echo.
echo La aplicacion se abrira automaticamente en: http://localhost:3000
echo Presiona Ctrl+C para detener el servidor
echo.

cd /d "%~dp0frontend"
call npm start

pause
