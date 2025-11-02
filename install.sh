#!/bin/bash

set -e

echo "🚀 Installing Arch Package Manager..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first:"
    echo "   sudo pacman -S python"
    exit 1
fi

# Check if yay is installed
if ! command -v yay &> /dev/null; then
    echo "⚠️  Warning: 'yay' is not installed. AUR package search will not work."
    echo "   Install it with: sudo pacman -S yay"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists, skipping creation."
else
    python3 -m venv venv
fi

# Activate and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create executable wrapper script
echo "🔧 Creating executable..."
cat > "$SCRIPT_DIR/arch-pkg" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
python "$SCRIPT_DIR/arch_pkg_manager.py"
EOF

chmod +x "$SCRIPT_DIR/arch-pkg"

# Create symlink in ~/.local/bin if it exists
if [ -d "$HOME/.local/bin" ]; then
    echo "🔗 Creating symlink in ~/.local/bin..."
    ln -sf "$SCRIPT_DIR/arch-pkg" "$HOME/.local/bin/arch-pkg"
    echo "✓ You can now run 'arch-pkg' from anywhere!"
else
    echo "📝 Note: Add $SCRIPT_DIR to your PATH to run 'arch-pkg' from anywhere"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  - Run: $SCRIPT_DIR/arch-pkg"
if [ -d "$HOME/.local/bin" ]; then
    echo "  - Or: arch-pkg (from anywhere)"
fi
echo "  - Or press SUPER ALT + P (after reloading Hyprland)"
echo ""
