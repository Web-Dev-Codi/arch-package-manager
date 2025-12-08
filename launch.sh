#!/bin/bash

# Launch AUR TUI in a terminal window
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set terminal (change to your preferred terminal)
TERMINAL="${TERMINAL:-kitty}"

# Check if aur-tui is in PATH
if command -v aur-tui &> /dev/null; then
    AUR_TUI_CMD="aur-tui"
else
    # Fallback to local script
    AUR_TUI_CMD="$SCRIPT_DIR/aur-tui"
    if [ ! -f "$AUR_TUI_CMD" ]; then
        AUR_TUI_CMD="$SCRIPT_DIR/arch_pkg_manager.py"
    fi
fi

# Launch in a new terminal window with specific class for Hyprland rules
$TERMINAL --class aur-tui-manager --title "AUR TUI" -e "$AUR_TUI_CMD"
