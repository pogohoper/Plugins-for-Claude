#!/bin/bash
# TTS Plugin installer for Claude Code
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== TTS Plugin for Claude Code ==="
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -q edge-tts pygame
echo "  Done."
echo ""

# Show how to use
echo "Plugin ready! To use it, run Claude Code with:"
echo ""
echo "  claude --plugin-dir \"$SCRIPT_DIR\""
echo ""
echo "Or add it permanently to your settings by adding this to"
echo "~/.claude/settings.json under \"plugins\":"
echo ""
echo "  \"$SCRIPT_DIR\""
echo ""
echo "Then use: /tts Hello world"
