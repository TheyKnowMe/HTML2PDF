@echo off
echo.
echo ===========================================
echo    PDF Konverter wird gestartet...
echo ===========================================
echo.

REM Wechselt in das Verzeichnis, in dem diese Batch-Datei liegt
cd /d "%~dp0"

echo Python-App wird gestartet. Bitte warten Sie, bis der Server laeuft...
REM Startet die Python-App in einem neuen Konsolenfenster
start "PDF Konverter Server" cmd /k python app.py

echo Warte 5 Sekunden, damit der Server hochfahren kann...
timeout /t 5 /nobreak > nul

echo Oeffne die Web-Oberflaeche im Standardbrowser...
start http://127.0.0.1:5000

echo.
echo Fertig! Der Server laeuft im anderen Fenster.
echo Sie koennen dieses Fenster jetzt schliessen.
pause