@echo off
setlocal
call .venv\Scripts\activate.bat 2>nul
set PYTHONPATH=%CD%\src
echo === DEMO ART LATEX (nao gera arquivo de importacao real) ===
python -m jrdp.cli
endlocal
