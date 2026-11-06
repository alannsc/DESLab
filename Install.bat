@echo off
setlocal
cd /d "%~dp0"
python -m pip install .
exit /b %errorlevel%
