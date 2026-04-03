@echo off
echo ============================================================
echo  Personal AI Employee - Qwen Code CLI Quick Start
echo ============================================================
echo.

echo [1] Checking Qwen Code CLI installation...
qwen --version
if errorlevel 1 (
    echo ERROR: Qwen Code CLI not installed!
    echo Install with: npm install -g @qwen-code/qwen-code@latest
    pause
    exit /b 1
)
echo.

echo [2] Qwen Code CLI Status:
qwen --help 2>&1 | findstr /C:"version"
echo.

echo [3] Authentication Status:
if exist "%USERPROFILE%\.qwen\oauth_creds.json" (
    echo ✓ OAuth credentials found
) else (
    echo ⚠ No OAuth credentials found
    echo.
    echo To authenticate:
    echo   1. Run: qwen
    echo   2. Type: /auth
    echo   3. Select: Qwen OAuth
    echo   4. Login with Qwen Chat account
)
echo.

echo [4] Available Models:
echo    - qwen3.5-plus (recommended)
echo    - qwen3-coder (coding specialist)
echo    - qwen2.5 (fallback)
echo.

echo [5] Test Qwen Code:
echo.
echo ============================================================
echo  Testing Qwen Code CLI...
echo ============================================================
echo.
qwen -p "Hello! I'm setting up Personal AI Employee with Qwen Code CLI. Confirm you're working."
echo.
echo.

echo ============================================================
echo  Next Steps:
echo ============================================================
echo  1. Complete OAuth setup if not done (run: qwen ^&^& /auth)
echo  2. Configure AI_Employee_Vault/.env
echo  3. Run orchestrator: python AI_Employee_Vault/src/orchestrator.py
echo  4. View docs: QWEN_CODE_SETUP.md
echo ============================================================
echo.
pause
