@echo off
cd /d "%~dp0"
set PY=python
where python >nul 2>&1 || set PY=py
%PY% --version || (echo Python is not installed. Install it from python.org and tick "Add to PATH". & pause & exit /b)
where ffmpeg >nul 2>&1 || winget install -e --id Gyan.FFmpeg
%PY% -m pip install -U flask flask-cors yt-dlp
echo.
echo Starting server... keep this window open while using the site.
%PY% server.py
echo.
echo Server stopped. Read the message above.
pause
