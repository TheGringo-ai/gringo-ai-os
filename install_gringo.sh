#!/bin/bash
"""
GRINGO System Integration Installer
Installs GRINGO as a system-wide command on macOS
"""

echo "🤖 GRINGO System Integration Installer"
echo "======================================"

# Get the current directory (where GRINGO is located)
GRINGO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GRINGO_SCRIPT="$GRINGO_DIR/gringo"

echo "📍 GRINGO Location: $GRINGO_DIR"

# Check if gringo script exists
if [ ! -f "$GRINGO_SCRIPT" ]; then
    echo "❌ Error: gringo script not found at $GRINGO_SCRIPT"
    exit 1
fi

# Create a symbolic link in /usr/local/bin (requires sudo)
echo "🔗 Creating system-wide symbolic link..."
if sudo ln -sf "$GRINGO_SCRIPT" /usr/local/bin/gringo; then
    echo "✅ Successfully installed gringo command system-wide"
    echo "   You can now use 'gringo' from anywhere in the terminal"
else
    echo "❌ Failed to create system-wide link"
    echo "   You can still use gringo by running: $GRINGO_SCRIPT"
fi

# Add to shell profile for PATH (backup method)
echo ""
echo "🔧 Setting up shell integration..."

# Detect shell and add to appropriate profile
if [ "$SHELL" = "/bin/zsh" ] || [ "$SHELL" = "/usr/bin/zsh" ]; then
    PROFILE="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [ "$SHELL" = "/bin/bash" ] || [ "$SHELL" = "/usr/bin/bash" ]; then
    PROFILE="$HOME/.bash_profile"
    SHELL_NAME="bash"
else
    PROFILE="$HOME/.profile"
    SHELL_NAME="shell"
fi

# Add alias and PATH to profile
echo "" >> "$PROFILE"
echo "# GRINGO AI Assistant Integration" >> "$PROFILE"
echo "export GRINGO_HOME=\"$GRINGO_DIR\"" >> "$PROFILE"
echo "alias gringo=\"$GRINGO_SCRIPT\"" >> "$PROFILE"
echo "" >> "$PROFILE"

echo "✅ Added GRINGO integration to $PROFILE"
echo "   Restart your terminal or run: source $PROFILE"

# Test the installation
echo ""
echo "🧪 Testing installation..."
if command -v gringo >/dev/null 2>&1; then
    echo "✅ gringo command is available system-wide"
    gringo help | head -5
else
    echo "⚠️  gringo command not yet available (restart terminal)"
    echo "   Test with: $GRINGO_SCRIPT help"
fi

echo ""
echo "🎉 GRINGO Installation Complete!"
echo ""
echo "📋 Quick Start:"
echo "   gringo help                          - Show all commands"
echo "   gringo file create test.py \"print('hi')\" - Create a file"
echo "   gringo code review main.py           - Review code"
echo "   gringo duplicates ~/Downloads        - Find duplicates"
echo "   gringo agents                        - List AI agents"
echo ""
echo "🔗 Streamlit UI: http://localhost:8502"
echo ""
