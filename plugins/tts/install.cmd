@echo off
REM TTS Plugin installer for Claude Code

echo === TTS Plugin for Claude Code ===
echo.

echo Installing Python dependencies...
pip install -q edge-tts pygame
echo   Done.
echo.

echo Plugin ready! To use it, run Claude Code with:
echo.
echo   claude --plugin-dir "%~dp0"
echo.
echo Or add it permanently to your settings by adding the path
echo to ~/.claude/settings.json under "plugins":
echo.
echo   "%~dp0"
echo.
echo Then use: /tts Hello world
