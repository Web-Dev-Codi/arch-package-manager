# AUR TUI

A beautiful terminal-based package manager for Arch Linux that searches both official repositories and the AUR, with keyboard shortcut support.

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
- 🪟 Window manager integration with floating, centered terminal window
- 🚀 Proper Arch Linux package installation support

## Prerequisites

- Python 3.8+
- Arch Linux
- `yay` (for AUR support - optional)
- A terminal emulator (default: kitty)

## Installation

### Method 1: Using PKGBUILD (Recommended for Arch Linux)

1. **Clone or download this repository:**
   ```bash
   git clone https://github.com/Web-Dev-Codi/arch-package-manager
   cd arch-package-manager
   ```

2. **Build and install the package:**
   ```bash
   makepkg -si
   ```

   This will:
   - Install all dependencies automatically
   - Install `aur-tui` system-wide to `/usr/bin/aur-tui`
   - Create a desktop entry for keyboard shortcuts
   - Set up proper file permissions

3. **Verify installation:**
   ```bash
   which aur-tui
   aur-tui --help  # Should launch the TUI
   ```

### Method 2: Using install.sh (Manual Installation)

1. **Run the installation script:**
   ```bash
   git clone https://github.com/Web-Dev-Codi/arch-package-manager
   cd arch-package-manager
   chmod +x install.sh
   ./install.sh
   ```

   This will:
   - Install Python dependencies
   - Create the `aur-tui` executable in `~/.local/bin`
   - Add `~/.local/bin` to your PATH (if needed)
   - Create a desktop entry for keyboard shortcuts

2. **If `aur-tui` command is not found:**
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   # Or restart your terminal
   ```

### Method 3: System-wide Installation (Requires sudo)

```bash
sudo INSTALL_METHOD=system ./install.sh
```

This installs `aur-tui` to `/usr/bin/aur-tui` system-wide.

## Usage

### Opening the App

- **From terminal:** Run `aur-tui`
- **Using desktop entry:** Launch "AUR TUI" from your application menu
- **Using keyboard shortcut:** Configure a keybinding (see Configuration section)

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

### Setting Up Keyboard Shortcuts

#### For Hyprland

Edit `~/.config/hypr/bindings.conf`:
```conf
bind = $mainMod, P, exec, aur-tui
# Or use the launch script for window management:
bind = $mainMod, P, exec, /usr/lib/aur-tui/launch.sh
```

For window rules, edit `~/.config/hypr/windowrules.conf`:
```conf
windowrulev2 = size 1000 700, class:^(aur-tui-manager)$
windowrulev2 = float, class:^(aur-tui-manager)$
windowrulev2 = center, class:^(aur-tui-manager)$
```

#### For i3wm

Edit `~/.config/i3/config`:
```conf
bindsym $mod+p exec aur-tui
```

#### For Sway

Edit `~/.config/sway/config`:
```conf
bindsym $mod+p exec aur-tui
```

#### For X11 (using sxhkd or similar)

Edit `~/.config/sxhkd/sxhkdrc`:
```conf
super + p
    aur-tui
```

#### Using Desktop Entry

The desktop entry (`aur-tui.desktop`) allows you to set keyboard shortcuts through your desktop environment's settings (GNOME, KDE, XFCE, etc.).

### Change Terminal Emulator

Edit `launch.sh`:
```bash
TERMINAL="${TERMINAL:-kitty}"
```

Change `kitty` to your preferred terminal (e.g., `alacritty`, `foot`, `wezterm`).

## Troubleshooting

### "aur-tui: command not found"
- Ensure `~/.local/bin` is in your PATH: `echo $PATH | grep local`
- Add to PATH: `export PATH="$HOME/.local/bin:$PATH"` (add to `~/.bashrc` or `~/.zshrc`)
- Or reinstall using PKGBUILD method for system-wide installation

### "rich" module not found
- Install dependencies: `pip install rich requests`
- Or reinstall using the install script: `./install.sh`
- For system-wide: `sudo pacman -S python-rich python-requests`

### AUR packages don't show up
- Install `yay`: `sudo pacman -S yay` (or from AUR manually)
- Check `yay` is in your PATH: `which yay`
- Verify yay works: `yay -V`

### Window doesn't float/center (Hyprland)
- Ensure Hyprland configuration is loaded: `hyprctl reload`
- Check window rules are applied: `hyprctl clients | grep aur-tui-manager`
- Verify terminal is launching with correct class: check `launch.sh`
- Update window class in `launch.sh` if needed

### Packages won't install
- Ensure you have sudo privileges
- You'll be prompted for password during installation (this is normal)
- For AUR packages, ensure `yay` is installed
- Check pacman database is up to date: `sudo pacman -Sy`

### Terminal doesn't open
- Check your terminal emulator is installed: `which kitty`
- Change terminal in `launch.sh` if needed: `TERMINAL=alacritty ./launch.sh`
- Or set environment variable: `export TERMINAL=your-terminal`

### Keyboard shortcut doesn't work
- Verify `aur-tui` command works: `which aur-tui && aur-tui --version`
- Check desktop entry exists: `ls ~/.local/share/applications/aur-tui.desktop` or `/usr/share/applications/aur-tui.desktop`
- For window managers, ensure config is reloaded
- For desktop environments, check keyboard shortcuts in settings

## Security Note

This app requires sudo access to install packages. For automatic installation without password prompts, you may need to configure sudoers. Use with caution:

```bash
# Add to /etc/sudoers (use visudo):
your_username ALL=(ALL) NOPASSWD: /usr/bin/pacman
```

Alternatively, you'll be prompted for your password during installation.

## License

MIT License - Feel free to modify and distribute.
