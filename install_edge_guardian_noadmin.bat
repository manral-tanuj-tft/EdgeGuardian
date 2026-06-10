@echo off
REM ============================================================
REM  Edge Guardian - one-time setup (NO ADMIN NEEDED)
REM  Drops a hidden launcher in your personal Startup folder so
REM  the guardian runs silently at every login.
REM  Just double-click this file. No "Run as administrator".
REM ============================================================

setlocal

set "SCRIPT_DIR=%~dp0"
set "PYW_PATH=%SCRIPT_DIR%edge_guardian.pyw"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "LAUNCHER=%STARTUP%\EdgeGuardian.vbs"

REM --- Find pythonw.exe (no-console Python launcher) ---
for /f "delims=" %%i in ('where pythonw.exe 2^>nul') do set "PYTHONW=%%i" & goto :found
echo Could not find pythonw.exe on your PATH.
echo Install Python (and tick "Add Python to PATH"), then re-run this.
pause
exit /b 1
:found

echo Using pythonw : %PYTHONW%
echo Using script  : %PYW_PATH%
echo Startup folder: %STARTUP%
echo.

REM --- Write a tiny VBS that launches pythonw fully hidden (window style 0) ---
> "%LAUNCHER%" echo Set s = CreateObject("WScript.Shell")
>>"%LAUNCHER%" echo s.Run """%PYTHONW%"" ""%PYW_PATH%""", 0, False

if exist "%LAUNCHER%" (
    echo Installed launcher: %LAUNCHER%
    echo Starting it now too...
    cscript //nologo "%LAUNCHER%" >nul 2>&1
    echo Done. It will also start automatically at your next login.
) else (
    echo Failed to write the launcher. Check folder permissions.
)

echo.
echo To remove it later, just delete this file:
echo   %LAUNCHER%
echo (or run:  del "%LAUNCHER%" )
pause
endlocal
