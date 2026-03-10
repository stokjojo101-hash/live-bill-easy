@echo off
title LIVE Bill Easy
color 0A

echo ===============================
echo     LIVE Bill Easy System
echo ===============================
echo.

:: ถ้าไม่มี venv ให้สร้าง
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate
call venv\Scripts\activate

echo.
echo Checking required packages...
echo.

:: เช็ค Flask
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Flask...
    pip install flask
)

:: เช็ค pandas
pip show pandas >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pandas...
    pip install pandas
)

:: เช็ค openpyxl
pip show openpyxl >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing openpyxl...
    pip install openpyxl
)

:: 🔥 เช็ค reportlab
pip show reportlab >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing reportlab...
    pip install reportlab
)

pip show pillow >nul 2>&1
if %errorlevel% neq 0 (
    pip install pillow
)

echo.
echo Starting server...
echo.

python app.py

pause