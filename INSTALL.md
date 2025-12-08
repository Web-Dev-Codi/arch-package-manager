# Installation Guide for AUR TUI

This guide covers multiple installation methods for AUR TUI on Arch Linux.

## Prerequisites

- Arch Linux (or Arch-based distribution)
- Python 3.8 or higher
- `yay` (optional, for AUR package support)

## Installation Methods

### Method 1: PKGBUILD Installation (Recommended)

This is the recommended method for Arch Linux as it properly integrates with the package manager.

1. **Download or clone the repository:**
   ```bash
   git clone <repository-url>
   cd aur-tui
   ```

2. **Install dependencies:**
   ```bash
   sudo pacman -S --needed python python-rich python-requests
   ```

3. **Build and install:**
   ```bash
   makepkg -si
   ```

   This will:
   - Build the package
   - Install it system-wide to `/usr/bin/aur-tui`
   - Install desktop entry to `/usr/share/applications/aur-tui.desktop`
   - Install launch script to `/usr/lib/aur-tui/launch.sh`

4. **Verify installation:**
   ```bash
   which aur-tui
   aur-tui  # Should launch the TUI
   ```

### Method 2: Manual Installation Script

For user-level installation without sudo:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd aur-tui
   ```

2. **Run the installation script:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   This will:
   - Install Python dependencies to user directory
   - Create `~/.local/bin/aur-tui` executable
   - Add `~/.local/bin` to PATH (if not already present)
   - Create desktop entry in `~/.local/share/applications/`

3. **Restart your terminal or source your shell config:**
   ```bash
   source ~/.bashrc  # or ~/.zshrc
   ```

4. **Verify:**
   ```bash
   aur-tui
   ```

### Method 3: System-wide Manual Installation

For system-wide installation (requires sudo):

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd aur-tui
   ```

2. **Install system dependencies:**
   ```bash
   sudo pacman -S --needed python python-rich python-requests
   ```

3. **Run installation with system flag:**
   ```bash
   sudo INSTALL_METHOD=system ./install.sh
   ```

   Or manually:
   ```bash
   sudo install -Dm755 arch_pkg_manager.py /usr/lib/aur-tui/arch_pkg_manager.py
   sudo install -Dm755 /dev/stdin /usr/bin/aur-tui << 'EOF'
   #!/bin/bash
   exec python3 /usr/lib/aur-tui/arch_pkg_manager.py "$@"
   EOF
   sudo install -Dm644 aur-tui.desktop /usr/share/applications/aur-tui.desktop
   sudo install -Dm755 launch.sh /usr/lib/aur-tui/launch.sh
   ```

## Post-Installation Setup

### Setting Up Keyboard Shortcuts

#### Option 1: Desktop Entry (GNOME, KDE, XFCE, etc.)

1. Open your desktop environment's keyboard settings
2. Add a custom shortcut
3. Set command to: `aur-tui`
4. Assign your preferred key combination

#### Option 2: Window Manager Configuration

**Hyprland:**
```conf
# ~/.config/hypr/bindings.conf
bind = $mainMod, P, exec, aur-tui

# ~/.config/hypr/windowrules.conf
windowrulev2 = size 1000 700, class:^(aur-tui-manager)$
windowrulev2 = float, class:^(aur-tui-manager)$
windowrulev2 = center, class:^(aur-tui-manager)$
```

**i3wm:**
```conf
# ~/.config/i3/config
bindsym $mod+p exec aur-tui
```

**Sway:**
```conf
# ~/.config/sway/config
bindsym $mod+p exec aur-tui
```

**Openbox:**
```xml
<!-- ~/.config/openbox/rc.xml -->
<keybind key="W-p">
  <action name="Execute">
    <command>aur-tui</command>
  </action>
</keybind>
```

**sxhkd (for X11):**
```conf
# ~/.config/sxhkd/sxhkdrc
super + p
    aur-tui
```

### Verifying Installation

Run these commands to verify everything is set up correctly:

```bash
# Check if command exists
which aur-tui

# Check if it's executable
aur-tui --help  # Should launch the TUI

# Check desktop entry (user installation)
ls ~/.local/share/applications/aur-tui.desktop

# Check desktop entry (system installation)
ls /usr/share/applications/aur-tui.desktop

# Test keyboard shortcut (if configured)
# Press your configured key combination
```

## Uninstallation

### If installed via PKGBUILD:
```bash
sudo pacman -R aur-tui
```

### If installed manually:
```bash
# Remove user installation
rm ~/.local/bin/aur-tui
rm ~/.local/share/applications/aur-tui.desktop

# Remove system installation
sudo rm /usr/bin/aur-tui
sudo rm -rf /usr/lib/aur-tui
sudo rm /usr/share/applications/aur-tui.desktop
```

## Troubleshooting

See the main README.md for troubleshooting tips.
