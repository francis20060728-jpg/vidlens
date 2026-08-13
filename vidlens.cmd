@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "SCRIPT=%SCRIPT_DIR%scripts\vidlens.py"
rem --- Try Python on PATH ---
where python >nul 2>&1 && (
    python "%SCRIPT%" %*
    exit /b %ERRORLEVEL%
)
where python3 >nul 2>&1 && (
    python3 "%SCRIPT%" %*
    exit /b %ERRORLEVEL%
)
where py >nul 2>&1 && (
    py "%SCRIPT%" %*
    exit /b %ERRORLEVEL%
)

rem --- Check common conda/miniconda locations (fast, no disk scan) ---
for %%P in (
    "%USERPROFILE%\miniconda3\python.exe"
    "%USERPROFILE%\anaconda3\python.exe"
    "%USERPROFILE%\miniforge3\python.exe"
    "C:\miniconda3\python.exe"
    "C:\anaconda3\python.exe"
    "C:\ProgramData\miniconda3\python.exe"
    "C:\ProgramData\anaconda3\python.exe"
    "D:\miniconda3\python.exe"
    "D:\anaconda3\python.exe"
    "F:\miniconda3\python.exe"
    "F:\anaconda3\python.exe"
) do (
    if exist "%%~P" (
        "%%~P" "%SCRIPT%" %*
        exit /b %ERRORLEVEL%
    )
)
rem --- Check conda environments via CONDA_PREFIX ---
if defined CONDA_PREFIX (
    if exist "%CONDA_PREFIX%\python.exe" (
        "%CONDA_PREFIX%\python.exe" "%SCRIPT%" %*
        exit /b %ERRORLEVEL%
    )
)

echo ERROR: Python not found. Install Python 3 or add it to PATH. 1>&2
exit /b 1
