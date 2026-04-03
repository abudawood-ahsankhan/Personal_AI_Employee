@echo off
title Personal AI Employee - Quick Start Menu
color 0A

:menu
cls
echo ============================================================
echo         PERSONAL AI EMPLOYEE - GOLD TIER
echo              Quick Start Menu
echo ============================================================
echo.
echo  AUTHENTICATION
echo  ============================================================
echo  [1] Authenticate Qwen Code (First Time)
echo  [2] Test Qwen Code
echo.
echo  RUN SYSTEM
echo  ============================================================
echo  [3] Run Orchestrator (Continuous)
echo  [4] Run Orchestrator (Once - Test Mode)
echo  [5] Run Ralph Wiggum Loop
echo.
echo  TEST COMPONENTS
echo  ============================================================
echo  [6] Test All Components
echo  [7] Test Plan Generator
echo  [8] Test CEO Briefing
echo  [9] Test Audit Logger
echo  [A] Run Gold Tier Verification
echo.
echo  MONITORING
echo  ============================================================
echo  [B] View Needs_Action Folder
echo  [C] View Plans Folder
echo  [D] View Done Folder
echo  [E] View Recent Audit Logs
echo.
echo  HELP
echo  ============================================================
echo  [H] Show Help
echo  [Q] Quit
echo.
echo ============================================================
set /p choice="Enter your choice (1-Q): "

if /i "%choice%"=="1" goto authenticate
if /i "%choice%"=="2" goto test_qwen
if /i "%choice%"=="3" goto orchestrator
if /i "%choice%"=="4" goto orchestrator_once
if /i "%choice%"=="5" goto ralph
if /i "%choice%"=="6" goto test_all
if /i "%choice%"=="7" goto plan_gen
if /i "%choice%"=="8" goto ceo_brief
if /i "%choice%"=="9" goto audit_log
if /i "%choice%"=="A" goto gold_test
if /i "%choice%"=="B" goto view_needs
if /i "%choice%"=="C" goto view_plans
if /i "%choice%"=="D" goto view_done
if /i "%choice%"=="E" goto view_audit
if /i "%choice%"=="H" goto help
if /i "%choice%"=="Q" goto quit
goto menu

:authenticate
cls
echo ============================================================
echo  QWEN CODE AUTHENTICATION
echo ============================================================
echo.
echo Starting authentication...
echo.
echo INSTRUCTIONS:
echo 1. Select: Qwen OAuth (use arrow keys)
echo 2. Press: Enter
echo 3. Login in browser that opens
echo 4. Return here when done
echo.
pause
qwen auth
echo.
echo Authentication complete!
pause
goto menu

:test_qwen
cls
echo ============================================================
echo  TESTING QWEN CODE
echo ============================================================
echo.
qwen -p "Hello! I'm testing my Personal AI Employee setup. Confirm you're working."
echo.
pause
goto menu

:orchestrator
cls
echo ============================================================
echo  RUNNING ORCHESTRATOR (Continuous Mode)
echo ============================================================
echo.
echo Press Ctrl+C to stop
echo.
pause
cd /d "%~dp0AI_Employee_Vault"
python src\orchestrator.py
goto menu

:orchestrator_once
cls
echo ============================================================
echo  RUNNING ORCHESTRATOR (Once Mode)
echo ============================================================
echo.
cd /d "%~dp0AI_Employee_Vault"
python src\orchestrator.py --once
echo.
pause
goto menu

:ralph
cls
echo ============================================================
echo  RUNNING RALPH WIGGUM LOOP
echo ============================================================
echo.
echo Press Ctrl+C to stop
echo.
pause
cd /d "%~dp0AI_Employee_Vault"
python src\ralph_wiggum.py
goto menu

:test_all
cls
echo ============================================================
echo  RUNNING FULL TEST SUITE
echo ============================================================
echo.
call "%~dp0test_suite.bat"
pause
goto menu

:plan_gen
cls
echo ============================================================
echo  TESTING PLAN GENERATOR
echo ============================================================
echo.
cd /d "%~dp0AI_Employee_Vault"
python src\plan_generator.py
echo.
pause
goto menu

:ceo_brief
cls
echo ============================================================
echo  TESTING CEO BRIEFING GENERATOR
echo ============================================================
echo.
cd /d "%~dp0AI_Employee_Vault"
python src\ceo_briefing.py
echo.
pause
goto menu

:audit_log
cls
echo ============================================================
echo  TESTING AUDIT LOGGER
echo ============================================================
echo.
cd /d "%~dp0AI_Employee_Vault"
python src\audit_logger.py
echo.
pause
goto menu

:gold_test
cls
echo ============================================================
echo  GOLD TIER VERIFICATION
echo ============================================================
echo.
cd /d "%~dp0AI_Employee_Vault"
C:\Users\LEnovo\AppData\Local\Python\bin\python.exe src\test_gold_tier.py .
echo.
pause
goto menu

:view_needs
cls
echo ============================================================
echo  NEEDS_ACTION FOLDER
echo ============================================================
echo.
dir "%~dp0AI_Employee_Vault\Needs_Action" /b
echo.
pause
goto menu

:view_plans
cls
echo ============================================================
echo  PLANS FOLDER
echo ============================================================
echo.
dir "%~dp0AI_Employee_Vault\Plans" /b
echo.
pause
goto menu

:view_done
cls
echo ============================================================
echo  DONE FOLDER
echo ============================================================
echo.
dir "%~dp0AI_Employee_Vault\Done" /b
echo.
pause
goto menu

:view_audit
cls
echo ============================================================
echo  RECENT AUDIT LOGS
echo ============================================================
echo.
dir "%~dp0AI_Employee_Vault\Logs\Audit" /b 2>nul
if errorlevel 1 echo No audit logs found
echo.
pause
goto menu

:help
cls
echo ============================================================
echo  PERSONAL AI EMPLOYEE - HELP
echo ============================================================
echo.
echo QUICK START:
echo 1. Authenticate: Select option 1
echo 2. Test Qwen: Select option 2
echo 3. Run System: Select option 3 or 4
echo.
echo DOCUMENTATION:
echo - QUICK_START_COMMANDS.md - Full command reference
echo - GOLD_TIER_README.md - Gold Tier documentation
echo - TEST_RESULTS.md - Latest test results
echo.
echo TROUBLESHOOTING:
echo - Qwen not working? Run option 1 to re-authenticate
echo - Python errors? Check requirements.txt installed
echo - MCP errors? Run npm install in each mcp-* folder
echo.
pause
goto menu

:quit
cls
echo.
echo Thank you for using Personal AI Employee - Gold Tier!
echo.
timeout /t 2 >nul
exit
