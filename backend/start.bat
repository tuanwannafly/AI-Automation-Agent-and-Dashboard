@echo off
REM Always run from this script's own directory (backend/) so uvicorn can find main.py
cd /d "%~dp0"
py -3.10 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
