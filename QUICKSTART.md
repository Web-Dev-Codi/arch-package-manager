# Quick Start Guide

## Installation (Choose One Method)

### Quick Install (Recommended)
```bash
git clone <repository-url>
cd aur-tui
chmod +x install.sh
./install.sh
```

### PKGBUILD Install (For Arch Linux)
```bash
git clone <repository-url>
cd aur-tui
makepkg -si
```

## Usage

### Launch the App
```bash
aur-tui
```

### Set Up Keyboard Shortcut

**For Hyprland:**
Add to `~/.config/hypr/bindings.conf`:
```conf
bind = $mainMod, P, exec, aur-tui
```

**For i3wm/Sway:**
Add to `~/.config/i3/config` or `~/.config/sway/config`:
```conf
bindsym $mod+p exec aur-tui
```

**For Desktop Environments:**
- Open Keyboard Settings
- Add Custom Shortcut
- Command: `aur-tui`
- Set your preferred key combination

## Verify Installation
```bash
./verify-install.sh
```

## Troubleshooting

If `aur-tui` command not found:
```bash
export PATH="$HOME/.local/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc for permanent fix
```

For more details, see [INSTALL.md](INSTALL.md) and [README.md](README.md).
