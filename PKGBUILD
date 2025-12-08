# Maintainer: Your Name <your.email@example.com>
pkgname=aur-tui
pkgver=1.0.0
pkgrel=1
pkgdesc="A terminal-based package manager for Arch Linux and AUR"
arch=('any')
url="https://github.com/yourusername/aur-tui"
license=('MIT')
depends=('python' 'python-rich' 'python-requests' 'pacman')
optdepends=('yay: AUR package support')
# For local builds, copy files to build directory
# For AUR, use git source instead:
# source=("$pkgname::git+https://github.com/yourusername/aur-tui.git")
source=("arch_pkg_manager.py"
        "requirements.txt"
        "launch.sh"
        "aur-tui.desktop")
sha256sums=('SKIP'
            'SKIP'
            'SKIP'
            'SKIP')

package() {
  cd "$srcdir"
  
  # Install Python script
  install -Dm755 arch_pkg_manager.py "$pkgdir/usr/lib/$pkgname/arch_pkg_manager.py"
  
  # Install executable wrapper
  install -Dm755 /dev/stdin "$pkgdir/usr/bin/$pkgname" << 'EOF'
#!/bin/bash
exec python3 /usr/lib/aur-tui/arch_pkg_manager.py "$@"
EOF
  
  # Install desktop entry for keyboard shortcuts
  install -Dm644 aur-tui.desktop "$pkgdir/usr/share/applications/$pkgname.desktop"
  
  # Install launch script
  install -Dm755 launch.sh "$pkgdir/usr/lib/$pkgname/launch.sh"
  
  # Install requirements info
  install -Dm644 requirements.txt "$pkgdir/usr/lib/$pkgname/requirements.txt"
}
