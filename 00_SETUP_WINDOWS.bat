@echo off
setlocal
echo === JR DP Automation Hub - Setup Windows ===

where python >nul 2>nul
if errorlevel 1 (
    echo Python nao encontrado no PATH. Instale o Python 3.11+ antes de continuar.
    exit /b 1
)

python -m venv .venv
call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo.
echo Setup concluido. Proximo passo: 01_TESTAR.bat
endlocal
