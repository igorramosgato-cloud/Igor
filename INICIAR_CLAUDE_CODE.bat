@echo off
setlocal
where claude >nul 2>nul
if errorlevel 1 (
    echo Claude Code CLI nao encontrado no PATH.
    echo Instale via: npm install -g @anthropic-ai/claude-code
    exit /b 1
)
claude
endlocal
