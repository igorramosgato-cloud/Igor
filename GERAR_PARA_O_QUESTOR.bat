@echo off
setlocal
call .venv\Scripts\activate.bat 2>nul
set PYTHONPATH=%CD%\src

echo === Gerar para o Questor ===
echo Este botao esta BLOQUEADO por seguranca ate que as pre-condicoes
echo listadas em docs\P01_ART_LATEX_QUESTOR.md sejam satisfeitas
echo (layout real, planilhas reais, chave de matching, codigo da Cesta
echo da Matriz, versao do conversor, exemplo de importacao bem sucedida).
echo.

python -m jrdp.cli
endlocal
