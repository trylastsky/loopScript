@echo off
echo Loading...
pip install -r requirements.txt >nul 2>&1

echo Starting...
python main.py
pause