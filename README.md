# Arch Package Manager TUI

A beautiful terminal-based package manager for Arch Linux that searches both official repositories and the AUR, with Hyprland integration.

## Features

- 🔍 Search official Arch repositories with **instant results**
- ⚡ **Lightning-fast** local filtering - no lag, no waiting
- 🔤 **Case-insensitive** search with exact letter matching
- ⌨️ Keyboard-driven terminal interface
- 📦 One-keypress package installation
- 📄 Full package details display (description, dependencies, licenses, etc.)
- 💾 **Smart caching** - package details loaded once and cached
- 📊 Real-time installation output streaming
- 🎨 Clean TUI with colored output
- 📜 Scrollable package details panel
- 🪟 Hyprland integration with floating, centered terminal window
- 🚀 Standalone executable - no system Python pollution

## Prerequisites

- Python 3.8+
- Arch Linux
- `yay` (for AUR support - optional)
- A terminal emulator (default: kitty)
- Hyprland (for keybinding integration)

## Installation

1. **Run the installation script:**
   ```bash
   cd /home/webdevcodi/arch-package-manager
   ./install.sh
   ```

   This will:
   - Create a Python virtual environment
   - Install dependencies (rich library)
   - Create the `arch-pkg` executable
   - Create a symlink in `~/.local/bin` (if it exists)

2. **Hyprland is already configured:**
   - Keybinding: `SUPER SHIFT + P` → launches arch-pkg
   - Window rules: Terminal opens centered, floating, and pinned on top

3. **Reload Hyprland:**
   ```bash
   hyprctl reload
   ```
   Or press `SUPER + Shift + R`

## Usage

### Opening the App

- **With Hyprland keybinding:** Press `SUPER SHIFT + P`
- **From terminal:** Run `arch-pkg` (if ~/.local/bin is in your PATH)
- **Manual launch:** Run `./arch-pkg` from the project directory

### Using the App

1. **Search:** Start typing package name (minimum 2 characters)
2. **Navigate:** Use `↑` and `↓` arrow keys to browse results
3. **View Details:** See full package information in the details panel
4. **Scroll Details:** Use `Page Up` / `Page Down` to scroll through package details
5. **Install:** Press `Enter` on selected package
6. **Watch:** See real-time installation output
7. **Close:** Press `Esc` to exit

### Keyboard Shortcuts

- **Type** - Search packages in real-time
- **↑ / ↓ / j / k** - Navigate package list
- **Page Up / Page Down** - Scroll package details panel
- **Enter** - Install selected package
- **Backspace** - Delete search characters
- **Esc / q** - Exit application

## Configuration

### Change Keybinding

Edit `~/.config/hypr/bindings.conf`:
```conf
bind = $mainMod, P, exec, arch-pkg
```

Change `$mainMod` (currently SUPER SHIFT) or `P` to your preference.

### Change Window Size

Edit `~/.config/hypr/windowrules.conf`:
```conf
windowrulev2 = size 1000 700, class:^(arch-pkg-manager)$
```

Change `1000 700` to your preferred width and height.

### Change Terminal Emulator

Edit `launch.sh`:
```bash
TERMINAL="${TERMINAL:-kitty}"
```

Change `kitty` to your preferred terminal (e.g., `alacritty`, `foot`, `wezterm`).

## Troubleshooting

### "rich" module not found
- Run the installation script: `./install.sh`
- Ensure you're using the `arch-pkg` wrapper (not running Python directly)

### AUR packages don't show up
- Install `yay`: `sudo pacman -S yay`
- Check `yay` is in your PATH: `which yay`

### Window doesn't float/center
- Ensure Hyprland configuration is loaded: `hyprctl reload`
- Check window rules are applied: `hyprctl clients | grep arch-pkg-manager`
- Verify terminal is launching with correct class: check `launch.sh`

### Packages won't install
- Ensure you have sudo privileges
- You'll be prompted for password during installation (this is normal)
- For AUR packages, ensure `yay` is installed

### Terminal doesn't open
- Check your terminal emulator is installed: `which kitty`
- Change terminal in `launch.sh` if needed

## Security Note

This app requires sudo access to install packages. For automatic installation without password prompts, you may need to configure sudoers. Use with caution:

```bash
# Add to /etc/sudoers (use visudo):
your_username ALL=(ALL) NOPASSWD: /usr/bin/pacman
```

Alternatively, you'll be prompted for your password during installation.

## License

MIT License - Feel free to modify and distribute.
