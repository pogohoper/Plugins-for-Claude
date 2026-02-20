#!/bin/bash
# TTS Plugin installer for Claude Code
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== TTS Plugin for Claude Code ==="
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install -q edge-tts pygame 2>/dev/null || python3 -m pip install -q edge-tts pygame 2>/dev/null || pip install -q edge-tts pygame 2>/dev/null || pip3 install -q edge-tts pygame || { echo "Warning: Could not install dependencies automatically. Please install manually: pip install edge-tts pygame"; }
echo "  Done."
echo ""

echo "Plugin ready!"
