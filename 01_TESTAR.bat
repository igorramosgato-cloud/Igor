@echo off
setlocal
call .venv\Scripts\activate.bat 2>nul
set PYTHONPATH=%CD%\src
python -m pytest tests -v
endlocal
