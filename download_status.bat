@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo    QWEN 2.5 DOWNLOAD MONITOR
echo ==========================================
echo.

:loop
cls
echo ==========================================
echo    QWEN 2.5 DOWNLOAD MONITOR
echo ==========================================
echo.
echo [Models Downloaded:]
ollama list
echo.
echo [Active Processes:]
ollama ps
echo.
echo [Ollama Server Status:]
curl -s http://localhost:11434/api/tags
echo.
echo.
echo ==========================================
echo Last Updated: !time!
echo Press Ctrl+C to exit
echo ==========================================
timeout /t 3 /nobreak >nul
goto loop
