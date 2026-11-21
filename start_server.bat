@echo off
title Daily Intelligence Backend Server
echo ====================================================================
echo  DAILY INTELLIGENCE BACKEND SERVER
echo  Running on http://0.0.0.0:8000
echo  Local access:  http://127.0.0.1:8000
echo  Phone Wi-Fi access: http://10.110.243.131:8000
echo ====================================================================
cd /d "%~dp0"
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
