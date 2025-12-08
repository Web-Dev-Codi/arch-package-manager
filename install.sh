#!/bin/bash

set -e

echo "🚀 Installing AUR TUI..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first:"
    echo "   sudo pacman -S python"
    exit 1
fi

# Check if running on Arch Linux
if [ ! -f /etc/arch-release ]; then
    echo "⚠️  Warning: This script is designed for Arch Linux"
fi

# Check if yay is installed
if ! command -v yay &> /dev/null; then
    echo "⚠️  Warning: 'yay' is not installed. AUR package search will not work."
    echo "   Install it with: yay -S yay"
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
if command -v pacman &> /dev/null; then
    sudo pacman -S --needed --noconfirm python python-pip python-rich python-requests 2>/dev/null || {
        echo "📦 Installing Python dependencies via pip..."
        pip3 install --user --break-system-packages rich requests 2>/dev/null || pip3 install --user rich requests
    }
else
    echo "📦 Installing Python dependencies via pip..."
    pip3 install --user --break-system-packages rich requests 2>/dev/null || pip3 install --user rich requests
fi

# Determine installation method
INSTALL_METHOD="${INSTALL_METHOD:-system}"

if [ "$INSTALL_METHOD" = "system" ] && [ "$(id -u)" -eq 0 ]; then
    # System-wide installation
    echo "🔧 Installing system-wide..."
    
    # Install Python script
    install -Dm755 arch_pkg_manager.py /usr/lib/aur-tui/arch_pkg_manager.py
    
    # Install executable wrapper
    install -Dm755 /dev/stdin /usr/bin/aur-tui << 'EOF'
#!/bin/bash
exec python3 /usr/lib/aur-tui/arch_pkg_manager.py "$@"
EOF
    
    # Install desktop entry
    install -Dm644 /dev/stdin /usr/share/applications/aur-tui.desktop << 'EOF'
[Desktop Entry]
Name=AUR TUI
Comment=Terminal-based package manager for Arch Linux and AUR
Exec=/usr/bin/aur-tui
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=System;PackageManager;
Keywords=arch;aur;package;manager;tui;
EOF
    
    # Install launch script
    install -Dm755 launch.sh /usr/lib/aur-tui/launch.sh
    
    echo "✅ System-wide installation complete!"
    echo ""
    echo "Usage:"
    echo "  - Run: aur-tui"
    echo "  - Or: /usr/lib/aur-tui/launch.sh"
    echo ""
    
elif [ -d "$HOME/.local/bin" ] || mkdir -p "$HOME/.local/bin" 2>/dev/null; then
    # User installation
    echo "🔧 Installing for user..."
    
    # Ensure ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo "📝 Adding ~/.local/bin to PATH..."
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc" 2>/dev/null || true
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc" 2>/dev/null || true
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    # Create executable wrapper script
    cat > "$HOME/.local/bin/aur-tui" << EOF
#!/bin/bash
exec python3 "$SCRIPT_DIR/arch_pkg_manager.py" "\$@"
EOF
    
    chmod +x "$HOME/.local/bin/aur-tui"
    
    # Install desktop entry for user
    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/aur-tui.desktop" << 'EOF'
[Desktop Entry]
Name=AUR TUI
Comment=Terminal-based package manager for Arch Linux and AUR
Exec=aur-tui
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=System;PackageManager;
Keywords=arch;aur;package;manager;tui;
EOF
    
    # Update launch.sh to use aur-tui
    sed -i 's|arch-pkg|aur-tui|g' launch.sh 2>/dev/null || true
    
    echo "✅ User installation complete!"
    echo ""
    echo "Usage:"
    echo "  - Run: aur-tui"
    echo "  - Or: $HOME/.local/bin/aur-tui"
    echo ""
    echo "Note: If 'aur-tui' command is not found, restart your terminal or run:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
else
    # Fallback: local installation
    echo "🔧 Installing locally..."
    
    cat > "$SCRIPT_DIR/aur-tui" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/arch_pkg_manager.py" "$@"
EOF
    
    chmod +x "$SCRIPT_DIR/aur-tui"
    
    echo "✅ Local installation complete!"
    echo ""
    echo "Usage:"
    echo "  - Run: $SCRIPT_DIR/aur-tui"
    echo "  - Or add $SCRIPT_DIR to your PATH"
    echo ""
fi
