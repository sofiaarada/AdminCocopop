@echo off
echo ==========================================
echo       INICIANDO COCOPOP DASHBOARD...
echo ==========================================
echo Por favor, no cierres esta ventana negra mientras usas la aplicacion.
echo Cuando termines, puedes cerrarla.
echo.
cd /d "%~dp0"
streamlit run app.py
pause
