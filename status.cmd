@echo off
title Qwen 2.5 - Download Status
color 0B

:loop
cls
echo.
echo ==============================================================================
echo                    QWEN 2.5 DOWNLOAD STATUS                                  
echo ==============================================================================
echo.
echo  Model: qwen2.5 | Size: 4.7 GB | Status: Downloading...
echo.
echo ┌────────────────────────────────────────────────────────────────────────────┐
echo │ DOWNLOADED MODELS:                                                         │
echo └────────────────────────────────────────────────────────────────────────────┘
ollama list
echo.
echo ┌────────────────────────────────────────────────────────────────────────────┐
echo │ RUNNING PROCESSES:                                                         │
echo └────────────────────────────────────────────────────────────────────────────┘
ollama ps
echo.
echo ┌────────────────────────────────────────────────────────────────────────────┐
echo │ AVAILABLE MODELS (Server):                                                 │
echo └────────────────────────────────────────────────────────────────────────────┘
curl -s http://localhost:11434/api/tags
echo.
echo.
echo ==============================================================================
echo  Last Check: %date% %time%
echo  Refreshing every 2 seconds... Press Ctrl+C to exit
echo ==============================================================================
timeout /t 2 /nobreak >nul
goto loop
