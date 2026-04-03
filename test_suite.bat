@echo off
echo ============================================================
echo  Personal AI Employee - TEST SUITE
echo ============================================================
echo.

echo [TEST 1] Checking Qwen Code CLI Installation...
qwen --version
if errorlevel 1 (
    echo FAIL: Qwen Code CLI not installed!
    goto :end
)
echo PASS: Qwen Code CLI installed
echo.

echo [TEST 2] Checking OAuth Credentials...
if exist "%USERPROFILE%\.qwen\oauth_creds.json" (
    echo PASS: OAuth credentials found
) else (
    echo WARN: No OAuth credentials - Run: qwen auth
)
echo.

echo [TEST 3] Checking Project Structure...
cd /d "E:\Hackathon 0\Personal_AI_Employee\AI_Employee_Vault"
dir /b | findstr /C:"Needs_Action" /C:"Plans" /C:"Done"
echo.

echo [TEST 4] Checking Gold Tier Components...
dir src\ralph_wiggum.py src\error_recovery.py src\audit_logger.py src\ceo_briefing.py 2>nul
echo.

echo [TEST 5] Checking MCP Servers...
dir /b src\mcp-* | findstr "mcp"
echo.

echo [TEST 6] Testing Python Components...
C:\Users\LEnovo\AppData\Local\Python\bin\python.exe src\test_gold_tier.py "E:\Hackathon 0\Personal_AI_Employee\AI_Employee_Vault"
echo.

echo [TEST 7] Testing Orchestrator (Dry Run)...
C:\Users\LEnovo\AppData\Local\Python\bin\python.exe src\orchestrator.py --once
echo.

echo ============================================================
echo  TEST SUMMARY
echo ============================================================
echo.
echo To complete authentication:
echo   1. Run: qwen auth
echo   2. Select: Qwen OAuth
echo   3. Complete login in browser
echo.
echo Then test Qwen Code:
echo   qwen -p "Hello!"
echo.
echo ============================================================

:end
pause
