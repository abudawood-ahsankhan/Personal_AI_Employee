@echo off
echo ==========================================
echo  Qwen-Agent + Ollama Setup Checker
echo ==========================================
echo.

echo [1] Checking Ollama status...
ollama list
echo.

echo [2] Checking Ollama server...
curl http://localhost:11434/api/tags 2>nul
echo.
echo.

echo [3] Testing Qwen-Agent import...
C:\Users\LEnovo\AppData\Local\Python\bin\python.exe -c "from qwen_agent.llm import get_chat_model; print('Qwen-Agent: OK')"
echo.

echo [4] Available Qwen models to download:
echo     - ollama pull qwen3        (latest, ~5GB)
echo     - ollama pull qwen2.5      (stable, ~4.7GB)
echo     - ollama pull qwen2:7b     (smaller, ~4.4GB)
echo     - ollama pull qwen2:1.8b   (lightweight, ~1.8GB)
echo.

echo ==========================================
echo  Next Steps:
echo  1. Download a model: ollama pull qwen2.5
echo  2. Copy .env.example to .env
echo  3. Run: python qwen_agent_config.py
echo ==========================================
