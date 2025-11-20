@echo off
echo 🚀 SA Investment Analyzer - Quick Start
echo.

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Creating .env file...
if not exist .env (
    copy .env.example .env
)

echo Initializing system...
python scripts\init_system.py

echo.
echo ✅ Setup complete!
echo.
echo To start the dashboard:
echo   venv\Scripts\activate.bat
echo   streamlit run app.py
pause