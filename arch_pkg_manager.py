#!/usr/bin/env python3
"""
Arch Package Manager TUI
A terminal-based package manager for Arch Linux and AUR
"""

import subprocess
import sys
import re
from typing import List, Tuple, Optional, Dict
import shutil
from functools import lru_cache
import threading
import requests

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich import box
except ImportError:
    print("Error: 'rich' library not found.")
    print("Please run the installation script: ./install.sh")
    sys.exit(1)

import curses
from curses import wrapper


class Package:
    def __init__(self, name: str, version: str, repo: str, description: str, source: str):
        self.name = name
        self.version = version
        self.repo = repo
        self.description = description
        self.source = source
        self.details = None  # Cache for detailed info


class ArchPackageManager:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.all_packages: List[Package] = []  # All available packages (cached)
        self.filtered_packages: List[Package] = []  # Currently filtered/displayed packages
        self.selected_idx = 0
        self.search_query = ""
        self.state = "search"  # search, installing, complete
        self.output_lines = []
        self.output_scroll_offset = 0
        self.install_success = False
        self.details_scroll_offset = 0
        self.db_loaded = False
        self.details_cache: Dict[str, dict] = {}  # Cache for package details
        # AUR search state
        self.aur_results: List[Package] = []
        self.aur_thread: Optional[threading.Thread] = None
        self.aur_pending = False
        self.aur_last_query = ""
        self.aur_loading = False
        
        # Initialize colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)      # Header
        curses.init_pair(2, curses.COLOR_GREEN, -1)     # Official repo
        curses.init_pair(3, curses.COLOR_YELLOW, -1)    # AUR
        curses.init_pair(4, curses.COLOR_WHITE, -1)     # Normal text
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Selected
        curses.init_pair(6, curses.COLOR_RED, -1)       # Error
        
        # Hide cursor
        curses.curs_set(0)
        
        # Set timeout for getch
        self.stdscr.timeout(100)
        
        # Load package database on init (in background)
        self.load_package_database()
        
    def load_package_database(self):
        """Load all packages once for fast local filtering"""
        if self.db_loaded:
            return
            
        results = []
        # Load package names from pacman database using faster method
        try:
            # Use expac for much faster package list (if available)
            if shutil.which('expac'):
                pacman_output = subprocess.run(
                    ['expac', '-S', '%r\t%n\t%v'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                for line in pacman_output.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            repo = parts[0]
                            name = parts[1]
                            version = parts[2]
                            # Description will be loaded lazily when displaying
                            results.append(Package(name, version, repo, "", 'official'))
            else:
                # Fallback to pacman -Sl if expac not available
                pacman_output = subprocess.run(
                    ['pacman', '-Sl'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                for line in pacman_output.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            repo = parts[0]
                            name = parts[1]
                            version = parts[2]
                            results.append(Package(name, version, repo, "", 'official'))
        except Exception as e:
            # If loading fails, continue with empty list
            pass
        
        self.all_packages = results
        self.db_loaded = True
        
    @lru_cache(maxsize=5000)
    def get_package_description_cached(self, package_name: str, source: str) -> str:
        """Get package description with caching"""
        try:
            if source == 'official':
                result = subprocess.run(
                    ['pacman', '-Si', package_name],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
            else:
                result = subprocess.run(
                    ['yay', '-Si', package_name],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
            
            # Extract description
            for line in result.stdout.split('\n'):
                if line.startswith('Description'):
                    return line.split(':', 1)[1].strip()
        except:
            pass
        return ""
    
    def filter_packages(self, query: str) -> List[Package]:
        """Fast local filtering of packages - case insensitive exact letter matching"""
        if not query:
            return []
        
        query_lower = query.lower()
        filtered = []
        
        for pkg in self.all_packages:
            # Case-insensitive matching: check if query is in package name
            if query_lower in pkg.name.lower():
                filtered.append(pkg)
                if len(filtered) >= 100:  # Limit results for performance
                    break
        
        return filtered

    def start_aur_search(self, query: str):
        """Fetch AUR results for the current query in the background using the AUR RPC API."""
        # Clear if no query
        if not query:
            self.aur_results = []
            return
        
        # If a previous AUR search is running, mark pending and queue latest query
        if self.aur_thread and self.aur_thread.is_alive():
            self.aur_pending = True
            self.aur_last_query = query
            return
        
        captured_query = query
        q_lower = captured_query.lower()
        
        def worker():
            self.aur_loading = True
            results: List[Package] = []
            try:
                url = f"https://aur.archlinux.org/rpc/?v=5&type=search&by=name&arg={captured_query}"
                resp = requests.get(url, timeout=4)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get('results', [])[:200]:
                        name = item.get('Name', '')
                        version = item.get('Version', '')
                        desc = item.get('Description', '') or ""
                        # Enforce our exact letter, case-insensitive match locally
                        if q_lower in name.lower():
                            results.append(Package(name, version, 'aur', desc, 'aur'))
                            if len(results) >= 100:
                                break
            except Exception:
                # Ignore network errors silently; keep previous AUR results
                pass
            
            # Only apply if user hasn't changed the query since this started
            if captured_query == self.search_query:
                self.aur_results = results
                # Merge local and AUR results, limit to 100
                local = self.filter_packages(self.search_query)
                take_from_aur = max(0, 100 - len(local))
                self.filtered_packages = local + results[:take_from_aur]
                self.selected_idx = 0
            self.aur_loading = False
            
            # Handle pending search
            if self.aur_pending:
                self.aur_pending = False
                self.start_aur_search(self.aur_last_query)
        
        self.aur_last_query = query
        self.aur_thread = threading.Thread(target=worker, daemon=True)
        self.aur_thread.start()
    
    def get_package_details(self, package: Package) -> dict:
        """Fetch detailed package information with caching"""
        # Check cache first
        cache_key = f"{package.source}:{package.name}"
        if cache_key in self.details_cache:
            return self.details_cache[cache_key]
        
        details = {
            'description': package.description,
            'url': '',
            'licenses': '',
            'depends': '',
            'optional_deps': '',
            'conflicts': '',
            'provides': '',
            'installed_size': '',
            'packager': '',
            'build_date': '',
            'install_date': '',
            # AUR-specific fields
            'votes': '',
            'popularity': '',
            'maintainer': '',
            'first_submitted': '',
            'last_updated': '',
            'aur_url': ''
        }
        
        try:
            if package.source == 'official':
                # Use pacman -Si for official packages
                result = subprocess.run(
                    ['pacman', '-Si', package.name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                output = result.stdout
            else:
                # Use yay -Si for AUR packages
                result = subprocess.run(
                    ['yay', '-Si', package.name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                output = result.stdout
                # Set AUR URL
                details['aur_url'] = f'https://aur.archlinux.org/packages/{package.name}'
            
            # Parse the output
            for line in output.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Description':
                        details['description'] = value
                    elif key == 'URL':
                        details['url'] = value
                    elif key == 'Licenses':
                        details['licenses'] = value
                    elif key == 'Depends On':
                        details['depends'] = value
                    elif key == 'Optional Deps':
                        details['optional_deps'] = value
                    elif key == 'Conflicts With':
                        details['conflicts'] = value
                    elif key == 'Provides':
                        details['provides'] = value
                    elif key == 'Installed Size':
                        details['installed_size'] = value
                    elif key == 'Packager':
                        details['packager'] = value
                    elif key == 'Build Date':
                        details['build_date'] = value
                    elif key == 'Install Date':
                        details['install_date'] = value
                    # AUR-specific fields
                    elif key == 'Votes':
                        details['votes'] = value
                    elif key == 'Popularity':
                        details['popularity'] = value
                    elif key == 'Maintainer':
                        details['maintainer'] = value
                    elif key == 'First Submitted':
                        details['first_submitted'] = value
                    elif key == 'Last Updated':
                        details['last_updated'] = value
        except Exception:
            pass
        
        # Cache the details
        self.details_cache[cache_key] = details
        return details
    
    def install_package(self, package: Package):
        """Install a package and capture output"""
        self.state = "installing"
        self.output_lines = []
        self.output_scroll_offset = 0
        self.current_package = package
        self.stdscr.clear()
        
        if package.source == 'official':
            cmd = ['sudo', 'pacman', '-S', '--noconfirm', package.name]
        else:
            cmd = ['yay', '-S', '--noconfirm', package.name]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.output_lines.append(line.rstrip())
                    # Auto-scroll to bottom while installing
                    height, _ = self.stdscr.getmaxyx()
                    visible_lines = height - 7
                    self.output_scroll_offset = max(0, len(self.output_lines) - visible_lines)
                    self.draw_install_screen(package)
            
            process.wait()
            self.install_success = (process.returncode == 0)
            
        except Exception as e:
            self.output_lines.append(f"\nError: {str(e)}")
            self.install_success = False
        
        self.state = "complete"
        self.draw_install_screen(package)
    
    def draw_header(self):
        """Draw the header"""
        height, width = self.stdscr.getmaxyx()
        header = "🔍 ARCH PACKAGE MANAGER"
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(0, (width - len(header)) // 2, header)
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        
    def draw_search_screen(self):
        """Draw the search interface"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        self.draw_header()
        
        # Search bar  
        db_status = f" [{len(self.all_packages)} pkgs loaded]" if self.db_loaded else " [loading pkgs...]"
        aur_status = " | AUR: loading" if self.aur_loading else ""
        self.stdscr.addstr(2, 2, "Search: ", curses.color_pair(4) | curses.A_BOLD)
        self.stdscr.addstr(2, 10, self.search_query + "_", curses.color_pair(1))
        self.stdscr.addstr(2, 10 + len(self.search_query) + 2, db_status + aur_status, curses.color_pair(4) | curses.A_DIM)
        
        # Draw line separator
        self.stdscr.addstr(3, 0, "─" * width)
        
        # Calculate split point (35% for list, 65% for details)
        available_height = height - 5  # Header + search bar + separator + footer
        list_height = int(available_height * 0.35)
        if list_height < 5:
            list_height = 5
        desc_start = 4 + list_height
        
        # Results
        if self.filtered_packages:
            self.stdscr.addstr(4, 2, f"Found {len(self.filtered_packages)} packages", curses.color_pair(4))
            
            start_line = 6
            # The details separator is drawn at row (desc_start - 1), so last usable list row is (desc_start - 2)
            list_end_row = desc_start - 2
            visible_lines = max(0, list_end_row - start_line + 1)
            
            # Calculate scroll offset (ensure selected row is visible and within bounds)
            max_scroll = max(0, len(self.filtered_packages) - visible_lines)
            scroll_offset = min(max(self.selected_idx - visible_lines + 1, 0), max_scroll)
            
            for i, pkg in enumerate(self.filtered_packages[scroll_offset:scroll_offset + visible_lines]):
                actual_idx = i + scroll_offset
                y = start_line + i
                
                if y > list_end_row:
                    break
                
                # Highlight selected
                if actual_idx == self.selected_idx:
                    self.stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
                    prefix = "► "
                else:
                    prefix = "  "
                
                # Repo tag
                repo_color = curses.color_pair(2) if pkg.source == 'official' else curses.color_pair(3)
                repo_tag = f"[{pkg.repo}]"
                
                # Package name and version
                line = f"{prefix}{pkg.name} {pkg.version}"
                if len(line) > width - 12:
                    line = line[:width-15] + "..."
                
                self.stdscr.addstr(y, 2, line)
                
                if actual_idx == self.selected_idx:
                    self.stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
                
                # Add repo tag
                self.stdscr.addstr(y, width - len(repo_tag) - 2, repo_tag, repo_color)
            
            # Description panel (separate section)
            self.stdscr.addstr(desc_start - 1, 0, "─" * width)
            self.stdscr.addstr(desc_start, 2, "PACKAGE DETAILS", curses.color_pair(1) | curses.A_BOLD)
            
            if self.selected_idx < len(self.filtered_packages):
                selected_pkg = self.filtered_packages[self.selected_idx]
                
                # Fetch detailed info if not cached
                if selected_pkg.details is None:
                    selected_pkg.details = self.get_package_details(selected_pkg)
                
                details = selected_pkg.details
                desc_visible_lines = height - desc_start - 3
                
                # Build all detail lines first
                all_lines = []
                
                def format_detail(label: str, value: str):
                    if not value or value == 'None':
                        return []
                    
                    lines = []
                    label_text = f"{label}: "
                    
                    # Word wrap value
                    value_lines = []
                    words = value.split()
                    current_text = ""
                    max_width = width - 6 - len(label_text)
                    
                    for word in words:
                        if len(current_text) + len(word) + 1 <= max_width:
                            current_text += (" " if current_text else "") + word
                        else:
                            if current_text:
                                value_lines.append(current_text)
                            current_text = word
                    if current_text:
                        value_lines.append(current_text)
                    
                    # First line with label
                    if value_lines:
                        lines.append(('label', label_text, value_lines[0]))
                        # Additional lines
                        indent = " " * len(label_text)
                        for line in value_lines[1:]:
                            lines.append(('indent', indent, line))
                    
                    return lines
                
                # Build all lines
                all_lines.extend(format_detail("Description", details['description']))
                all_lines.extend(format_detail("URL", details['url']))
                
                # AUR-specific fields
                if selected_pkg.source == 'aur':
                    all_lines.extend(format_detail("AUR Page", details['aur_url']))
                    all_lines.extend(format_detail("Votes", details['votes']))
                    all_lines.extend(format_detail("Popularity", details['popularity']))
                    all_lines.extend(format_detail("Maintainer", details['maintainer']))
                    all_lines.extend(format_detail("First Submitted", details['first_submitted']))
                    all_lines.extend(format_detail("Last Updated", details['last_updated']))
                
                all_lines.extend(format_detail("Licenses", details['licenses']))
                all_lines.extend(format_detail("Depends On", details['depends']))
                all_lines.extend(format_detail("Optional Deps", details['optional_deps']))
                all_lines.extend(format_detail("Conflicts", details['conflicts']))
                all_lines.extend(format_detail("Provides", details['provides']))
                all_lines.extend(format_detail("Installed Size", details['installed_size']))
                all_lines.extend(format_detail("Packager", details['packager']))
                all_lines.extend(format_detail("Build Date", details['build_date']))
                all_lines.extend(format_detail("Install Date", details['install_date']))
                
                # Apply scroll offset
                total_lines = len(all_lines)
                max_scroll = max(0, total_lines - desc_visible_lines)
                self.details_scroll_offset = max(0, min(self.details_scroll_offset, max_scroll))
                
                # Display visible lines
                visible_lines = all_lines[self.details_scroll_offset:self.details_scroll_offset + desc_visible_lines]
                for i, line_data in enumerate(visible_lines):
                    y_pos = desc_start + 1 + i
                    if y_pos >= height - 1:
                        break
                    
                    if line_data[0] == 'label':
                        _, label_text, value_text = line_data
                        self.stdscr.addstr(y_pos, 4, label_text, curses.color_pair(1))
                        self.stdscr.addstr(y_pos, 4 + len(label_text), value_text, curses.color_pair(4))
                    else:  # indent
                        _, indent, value_text = line_data
                        self.stdscr.addstr(y_pos, 4, indent + value_text, curses.color_pair(4))
                
                # Show scroll indicator if needed
                if total_lines > desc_visible_lines:
                    scroll_info = f" [{self.details_scroll_offset + 1}-{min(self.details_scroll_offset + desc_visible_lines, total_lines)}/{total_lines}] "
                    self.stdscr.addstr(desc_start - 1, width - len(scroll_info) - 1, scroll_info, curses.color_pair(4) | curses.A_DIM)
        
        # Footer
        footer = "↑↓ List | PgUp/PgDn Details | Enter Install | Esc/q Exit"
        self.stdscr.addstr(height - 1, (width - len(footer)) // 2, footer, curses.color_pair(4) | curses.A_DIM)
        
        self.stdscr.refresh()
    
    def draw_install_screen(self, package: Package):
        """Draw the installation progress screen with scrollable output"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        self.draw_header()
        
        # Installing header
        status = f"Installing {package.name}..."
        self.stdscr.addstr(2, 2, status, curses.color_pair(1) | curses.A_BOLD)
        
        # Draw line separator
        self.stdscr.addstr(3, 0, "─" * width)
        
        # Output
        start_line = 4
        visible_lines = height - start_line - 3
        
        # Calculate which lines to show based on scroll offset
        total_lines = len(self.output_lines)
        max_scroll = max(0, total_lines - visible_lines)
        self.output_scroll_offset = max(0, min(self.output_scroll_offset, max_scroll))
        
        # Show lines from scroll offset
        start_idx = self.output_scroll_offset
        end_idx = min(start_idx + visible_lines, total_lines)
        display_lines = self.output_lines[start_idx:end_idx]
        
        # Check if there's a sudo password prompt in recent output
        sudo_prompt = None
        for line in self.output_lines[-5:]:  # Check last 5 lines
            if '[sudo]' in line.lower() and 'password' in line.lower():
                sudo_prompt = line.strip()
                break
        
        for i, line in enumerate(display_lines):
            y = start_line + i
            if y >= height - 3:  # Leave room for sudo prompt
                break
            
            # Skip sudo password lines from regular output (they'll be shown at bottom)
            if '[sudo]' in line.lower() and 'password' in line.lower():
                continue
            
            # Truncate long lines
            if len(line) > width - 4:
                line = line[:width-7] + "..."
            
            self.stdscr.addstr(y, 2, line, curses.color_pair(4))
        
        # Display sudo password prompt at the bottom in green if present
        if sudo_prompt and self.state == "installing":
            prompt_y = height - 2
            self.stdscr.addstr(prompt_y, 2, "─" * (width - 4))
            self.stdscr.addstr(prompt_y + 1, 2, sudo_prompt, curses.color_pair(2) | curses.A_BOLD)
        
        # Scroll indicator
        if total_lines > visible_lines:
            scroll_info = f" [{start_idx + 1}-{end_idx}/{total_lines}] ↑↓ to scroll "
            self.stdscr.addstr(3, width - len(scroll_info) - 1, scroll_info, curses.color_pair(4) | curses.A_DIM)
        
        # Status footer
        if self.state == "complete":
            if self.install_success:
                msg = f"✓ {package.name} installed successfully! Press s to search again, Esc/q to close."
                color = curses.color_pair(2)
            else:
                msg = f"✗ Failed to install {package.name}. Press s to search again, Esc/q to close."
                color = curses.color_pair(6)

            # Safely fit message into available width
            max_width = max(0, width - 4)  # 2-char left padding and some right margin
            if max_width > 0 and len(msg) > max_width:
                msg = msg[: max_width - 3] + "..."
            if max_width > 0:
                self.stdscr.addstr(height - 1, 2, msg[:max_width], color | curses.A_BOLD)
        
        self.stdscr.refresh()
    
    def run(self):
        """Main application loop"""
        while True:
            if self.state == "search":
                self.draw_search_screen()
                
                key = self.stdscr.getch()
                
                # Handle multiple key formats
                if key == 27 or key == ord('q'):  # ESC or q
                    break
                elif key == curses.KEY_DOWN or key == ord('j'):  # Down or j
                    if self.filtered_packages:
                        self.selected_idx = min(self.selected_idx + 1, len(self.filtered_packages) - 1)
                        self.details_scroll_offset = 0  # Reset scroll when changing selection
                elif key == curses.KEY_UP or key == ord('k'):  # Up or k
                    if self.filtered_packages:
                        self.selected_idx = max(self.selected_idx - 1, 0)
                        self.details_scroll_offset = 0  # Reset scroll when changing selection
                elif key == curses.KEY_NPAGE:  # Page Down - scroll details
                    self.details_scroll_offset += 1
                elif key == curses.KEY_PPAGE:  # Page Up - scroll details
                    self.details_scroll_offset = max(0, self.details_scroll_offset - 1)
                elif key == 10 or key == curses.KEY_ENTER:  # Enter
                    if self.filtered_packages:
                        selected_pkg = self.filtered_packages[self.selected_idx]
                        self.install_package(selected_pkg)
                elif key == curses.KEY_BACKSPACE or key == 127 or key == 263 or key == 8:
                    if self.search_query:
                        self.search_query = self.search_query[:-1]
                        # Instant local filter
                        self.filtered_packages = self.filter_packages(self.search_query)
                        self.selected_idx = 0
                        self.details_scroll_offset = 0
                        # Kick off AUR search
                        self.start_aur_search(self.search_query)
                    else:
                        # Clear results when query empty
                        self.filtered_packages = []
                        self.start_aur_search("")
                elif key != -1 and 32 <= key <= 126:  # Printable characters
                    self.search_query += chr(key)
                    # Instant local filter
                    self.filtered_packages = self.filter_packages(self.search_query)
                    self.selected_idx = 0
                    self.details_scroll_offset = 0
                    # Kick off AUR search
                    self.start_aur_search(self.search_query)
            
            elif self.state == "installing" or self.state == "complete":
                # Get the current package (we need to store it)
                if hasattr(self, 'current_package'):
                    self.draw_install_screen(self.current_package)
                
                key = self.stdscr.getch()
                
                # Scroll output in install screen
                if key == curses.KEY_DOWN or key == ord('j'):
                    self.output_scroll_offset += 1
                elif key == curses.KEY_UP or key == ord('k'):
                    self.output_scroll_offset = max(0, self.output_scroll_offset - 1)
                elif key == curses.KEY_NPAGE:  # Page Down
                    height, _ = self.stdscr.getmaxyx()
                    visible_lines = height - 7
                    self.output_scroll_offset += visible_lines
                elif key == curses.KEY_PPAGE:  # Page Up
                    height, _ = self.stdscr.getmaxyx()
                    visible_lines = height - 7
                    self.output_scroll_offset = max(0, self.output_scroll_offset - visible_lines)
                
                if key == 27 or key == ord('q'):  # ESC or q
                    if self.state == "complete":
                        break
                elif key == ord('s') and self.state == "complete":
                    # Return to search view to perform another search
                    self.state = "search"
                    self.output_lines = []
                    self.output_scroll_offset = 0
                    # Refresh filter and (optionally) AUR search for current query
                    self.filtered_packages = self.filter_packages(self.search_query)
                    self.start_aur_search(self.search_query)


def main(stdscr):
    app = ArchPackageManager(stdscr)
    app.run()


if __name__ == "__main__":
    wrapper(main)
