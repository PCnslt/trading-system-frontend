@echo off
REM API Keys Loader - Batch script for loading all API keys
REM Usage: load-keys.cmd

echo Loading API keys from centralized secrets...

REM Check if PowerShell is available
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: PowerShell is not available.
    exit /b 1
)

REM Run PowerShell script to load keys
powershell -ExecutionPolicy Bypass -Command "& { . '%~dp0api-keys.ps1'; Set-AllApiKeys }"

if %errorlevel% equ 0 (
    echo.
    echo ✅ API keys loaded successfully!
    echo.
    echo Available commands in PowerShell:
    echo   Set-AllApiKeys     - Load keys for current session
    echo   Test-ApiKeys       - Test which keys are set
    echo   Get-ApiKeySummary  - Show masked summary
    echo   Save-ApiKeysToUserEnv - Save permanently
) else (
    echo.
    echo ❌ Failed to load API keys.
    exit /b 1
)