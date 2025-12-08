#!/bin/bash
# Verification script for AUR TUI installation

echo "🔍 Verifying AUR TUI installation..."
echo ""

ERRORS=0

# Check if aur-tui command exists
if command -v aur-tui &> /dev/null; then
    echo "✅ aur-tui command found: $(which aur-tui)"
else
    echo "❌ aur-tui command not found in PATH"
    ERRORS=$((ERRORS + 1))
fi

# Check if Python script exists
if [ -f "/usr/lib/aur-tui/arch_pkg_manager.py" ] || [ -f "$(dirname "$(which aur-tui 2>/dev/null)")/../lib/aur-tui/arch_pkg_manager.py" ] || [ -f "./arch_pkg_manager.py" ]; then
    echo "✅ Python script found"
else
    echo "⚠️  Python script location unclear"
fi

# Check Python dependencies
echo ""
echo "📦 Checking Python dependencies..."
if python3 -c "import rich" 2>/dev/null; then
    echo "✅ rich library installed"
else
    echo "❌ rich library not found"
    ERRORS=$((ERRORS + 1))
fi

if python3 -c "import requests" 2>/dev/null; then
    echo "✅ requests library installed"
else
    echo "❌ requests library not found"
    ERRORS=$((ERRORS + 1))
fi

# Check desktop entry
echo ""
echo "🖥️  Checking desktop entry..."
if [ -f "/usr/share/applications/aur-tui.desktop" ] || [ -f "$HOME/.local/share/applications/aur-tui.desktop" ]; then
    echo "✅ Desktop entry found"
else
    echo "⚠️  Desktop entry not found (optional)"
fi

# Check yay (optional)
echo ""
echo "🔧 Checking optional dependencies..."
if command -v yay &> /dev/null; then
    echo "✅ yay found (AUR support enabled)"
else
    echo "⚠️  yay not found (AUR support disabled)"
fi

# Summary
echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ Installation verification complete! All critical components found."
    echo ""
    echo "Try running: aur-tui"
else
    echo "❌ Installation verification found $ERRORS error(s)."
    echo "Please run ./install.sh to fix issues."
    exit 1
fi
