#!/bin/bash

# Launch Arch Package Manager in a terminal window
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set terminal (change to your preferred terminal)
TERMINAL="${TERMINAL:-kitty}"

# Launch in a new terminal window with specific class for Hyprland rules
$TERMINAL --class arch-pkg-manager --title "Arch Package Manager" -e "$SCRIPT_DIR/arch-pkg"
