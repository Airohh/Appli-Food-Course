@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 🛒 Génération de la liste de courses...
echo.
python generate_courses.py
echo.
pause

