"""
KAIROS Dreamweaver — Installer
Supports: Windows, macOS, Linux
Run with: python install.py  (or double-click install.bat / install.sh)
"""

import os
import sys
import json
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# =============================================================================
#  CONSTANTS
# =============================================================================

APP_NAME        = "KAIROS Dreamweaver"
INSTALL_DIR     = Path(__file__).parent.resolve()
VENV_DIR        = INSTALL_DIR / "venv"
SETTINGS_DIR    = Path.home() / ".kairos-dreamweaver"
SETTINGS_PATH   = SETTINGS_DIR / "settings.json"
MAIN_SCRIPT     = INSTALL_DIR / "dreamweaver.py"

REQUIREMENTS = [
    "langchain-groq",
    "langchain-core",
    "rich",
    "plyer",
    "pystray",
    "Pillow",
    "psutil",
    "python-dotenv",
]

# Startup entry name (Windows registry / Mac plist)
STARTUP_NAME = "KairosDreamweaver"

# Colors
BG        = "#12121f"
SURFACE   = "#1a1a2e"
ACCENT    = "#7c6fcd"
ACCENT_DIM= "#5a4fa0"
TEXT      = "#e0e0f0"
SUBTEXT   = "#8888aa"
ENTRY_BG  = "#0e0e1c"
BORDER    = "#2e2e50"
SUCCESS   = "#4caf82"
DANGER    = "#e05c5c"


# =============================================================================
#  PLATFORM HELPERS
# =============================================================================

def get_python() -> str:
    """Return path to python inside the venv."""
    if sys.platform == "win32":
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python")


def get_pip() -> str:
    if sys.platform == "win32":
        return str(VENV_DIR / "Scripts" / "pip.exe")
    return str(VENV_DIR / "bin" / "pip")


def add_to_startup_windows():
    """Add KAIROS to HKCU Run registry key."""
    import winreg
    python_exe = get_python()
    cmd = f'"{python_exe}" "{MAIN_SCRIPT}"'
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE,
    )
    winreg.SetValueEx(key, STARTUP_NAME, 0, winreg.REG_SZ, cmd)
    winreg.CloseKey(key)


def remove_from_startup_windows():
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE,
        )
        winreg.DeleteValue(key, STARTUP_NAME)
        winreg.CloseKey(key)
    except Exception:
        pass


def add_to_startup_mac():
    """Create a LaunchAgent plist so KAIROS starts on login."""
    launch_agents = Path.home() / "Library" / "LaunchAgents"
    launch_agents.mkdir(parents=True, exist_ok=True)
    plist_path = launch_agents / f"com.kairos.dreamweaver.plist"
    python_exe = get_python()

    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.kairos.dreamweaver</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_exe}</string>
        <string>{MAIN_SCRIPT}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>{Path.home()}/.kairos-dreamweaver/kairos.log</string>
    <key>StandardErrorPath</key>
    <string>{Path.home()}/.kairos-dreamweaver/kairos.log</string>
</dict>
</plist>"""

    plist_path.write_text(plist, encoding="utf-8")
    subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True)


def add_to_startup_linux():
    """Create a .desktop autostart entry."""
    autostart = Path.home() / ".config" / "autostart"
    autostart.mkdir(parents=True, exist_ok=True)
    desktop_path = autostart / "kairos-dreamweaver.desktop"
    python_exe = get_python()

    desktop = f"""[Desktop Entry]
Type=Application
Name=KAIROS Dreamweaver
Exec={python_exe} {MAIN_SCRIPT}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
    desktop_path.write_text(desktop, encoding="utf-8")


def register_startup():
    if sys.platform == "win32":
        add_to_startup_windows()
    elif sys.platform == "darwin":
        add_to_startup_mac()
    else:
        add_to_startup_linux()


# =============================================================================
#  INSTALLER LOGIC
# =============================================================================

def create_venv(log):
    log("Creating virtual environment...")
    subprocess.run(
        [sys.executable, "-m", "venv", str(VENV_DIR)],
        check=True, capture_output=True,
    )
    log("Virtual environment created.")


def install_dependencies(log):
    pip = get_pip()
    log("Installing dependencies (this may take a minute)...")
    for pkg in REQUIREMENTS:
        log(f"  Installing {pkg}...")
        subprocess.run(
            [pip, "install", pkg, "--quiet"],
            check=True, capture_output=True,
        )
    log("All dependencies installed.")


def save_initial_settings(api_key: str):
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    settings = {
        "groq_api_key": api_key.strip(),
        "model_name": "llama-3.3-70b-versatile",
        "wake_hour": 7,
        "idle_timeout_minutes": 10,
        "projects": [],
    }
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def launch_kairos():
    python_exe = get_python()
    subprocess.Popen([python_exe, str(MAIN_SCRIPT)])


# =============================================================================
#  INSTALLER UI
# =============================================================================

class InstallerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} — Installer")
        self.root.geometry("560x620")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # Center
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"560x620+{(sw-560)//2}+{(sh-620)//2}")

        self._build_ui()
        self.root.mainloop()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=ACCENT, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text="  KAIROS Dreamweaver",
            font=("Segoe UI", 18, "bold"),
            bg=ACCENT, fg="#ffffff", anchor="w",
        ).pack(side="left", padx=24, pady=12)
        tk.Label(
            header,
            text="Installer",
            font=("Segoe UI", 10),
            bg=ACCENT, fg="#ddd8ff", anchor="w",
        ).pack(side="left", pady=(22, 0))

        # Body
        body = tk.Frame(self.root, bg=BG, padx=36, pady=20)
        body.pack(fill="both", expand=True)

        # Step 1 — Welcome
        tk.Label(
            body,
            text="Welcome!",
            font=("Segoe UI", 13, "bold"),
            bg=BG, fg=TEXT, anchor="w",
        ).pack(anchor="w")

        tk.Label(
            body,
            text=(
                "KAIROS will install itself and start automatically\n"
                "every time you log in — no manual launching needed."
            ),
            font=("Segoe UI", 9),
            bg=BG, fg=SUBTEXT, anchor="w", justify="left",
        ).pack(anchor="w", pady=(4, 18))

        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=(0, 18))

        # Step 2 — API Key
        tk.Label(
            body,
            text="Your Groq API Key",
            font=("Segoe UI", 10, "bold"),
            bg=BG, fg=ACCENT, anchor="w",
        ).pack(anchor="w")

        tk.Label(
            body,
            text=(
                "KAIROS uses Groq to generate dream reports.\n"
                "Get a free key at console.groq.com"
            ),
            font=("Segoe UI", 9),
            bg=BG, fg=SUBTEXT, anchor="w", justify="left",
        ).pack(anchor="w", pady=(2, 8))

        self.api_var = tk.StringVar()
        api_entry = tk.Entry(
            body,
            textvariable=self.api_var,
            font=("Segoe UI", 10),
            bg=ENTRY_BG, fg=TEXT,
            insertbackground=TEXT,
            relief="flat", bd=8,
            show="*",
        )
        api_entry.pack(fill="x", ipady=8)

        # Show/hide toggle
        self.show_key = tk.BooleanVar(value=False)
        def toggle_show():
            api_entry.config(show="" if self.show_key.get() else "*")
        tk.Checkbutton(
            body,
            text="Show key",
            variable=self.show_key,
            command=toggle_show,
            font=("Segoe UI", 8),
            bg=BG, fg=SUBTEXT,
            activebackground=BG,
            selectcolor=ENTRY_BG,
        ).pack(anchor="e", pady=(2, 16))

        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=(0, 18))

        # Step 3 — Install location info
        tk.Label(
            body,
            text="Install Location",
            font=("Segoe UI", 10, "bold"),
            bg=BG, fg=ACCENT, anchor="w",
        ).pack(anchor="w")

        tk.Label(
            body,
            text=str(INSTALL_DIR),
            font=("Segoe UI", 8),
            bg=ENTRY_BG, fg=SUBTEXT,
            anchor="w", padx=8, pady=6,
        ).pack(fill="x", pady=(4, 4))

        tk.Label(
            body,
            text="Settings saved to: " + str(SETTINGS_DIR),
            font=("Segoe UI", 8),
            bg=BG, fg=SUBTEXT, anchor="w",
        ).pack(anchor="w", pady=(0, 16))

        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=(0, 14))

        # Progress log
        tk.Label(
            body,
            text="Installation Log",
            font=("Segoe UI", 9, "bold"),
            bg=BG, fg=ACCENT, anchor="w",
        ).pack(anchor="w")

        log_frame = tk.Frame(body, bg=ENTRY_BG)
        log_frame.pack(fill="x", pady=(4, 0))

        log_scroll = tk.Scrollbar(log_frame, orient="vertical")
        self.log_text = tk.Text(
            log_frame,
            font=("Consolas", 8),
            bg=ENTRY_BG, fg=SUBTEXT,
            relief="flat", bd=6,
            height=5,
            state="disabled",
            wrap="word",
            yscrollcommand=log_scroll.set,
        )
        log_scroll.config(command=self.log_text.yview)
        log_scroll.pack(side="right", fill="y")
        self.log_text.pack(fill="x")

        # Footer
        footer = tk.Frame(self.root, bg=SURFACE, pady=14, padx=36)
        footer.pack(fill="x", side="bottom")
        tk.Frame(footer, bg=BORDER, height=1).pack(fill="x", side="top", pady=(0, 10))

        self.status_var = tk.StringVar(value="Ready to install.")
        tk.Label(
            footer,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg=SURFACE, fg=SUBTEXT,
        ).pack(side="left")

        self.install_btn = tk.Button(
            footer,
            text="Install & Launch",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT, fg="#ffffff",
            activebackground=ACCENT_DIM,
            relief="flat", bd=0,
            padx=20, pady=8,
            cursor="hand2",
            command=self._start_install,
        )
        self.install_btn.pack(side="right")

    def _log(self, msg: str):
        """Append a line to the log box (thread-safe)."""
        def _append():
            self.log_text.config(state="normal")
            self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.root.after(0, _append)

    def _set_status(self, msg: str, color: str = SUBTEXT):
        self.root.after(0, lambda: self.status_var.set(msg))

    def _start_install(self):
        api_key = self.api_var.get().strip()
        if not api_key:
            messagebox.showerror(
                APP_NAME,
                "Please enter your Groq API key to continue.\n\nGet one free at console.groq.com",
            )
            return

        if not MAIN_SCRIPT.exists():
            messagebox.showerror(
                APP_NAME,
                f"Cannot find dreamweaver.py in:\n{INSTALL_DIR}\n\n"
                "Make sure install.py is in the same folder as dreamweaver.py.",
            )
            return

        self.install_btn.config(state="disabled", text="Installing...")
        self._set_status("Installing...")

        def run():
            try:
                # 1. Create venv
                create_venv(self._log)

                # 2. Install deps
                install_dependencies(self._log)

                # 3. Save settings
                self._log("Saving settings...")
                save_initial_settings(api_key)
                self._log("Settings saved.")

                # 4. Register startup
                self._log("Registering startup entry...")
                register_startup()
                self._log("KAIROS will now start automatically on login.")

                # 5. Done
                self._log("")
                self._log("Installation complete!")
                self._set_status("Done! Launching KAIROS now...", SUCCESS)

                self.root.after(0, self._finish)

            except subprocess.CalledProcessError as e:
                err = e.stderr.decode() if e.stderr else str(e)
                self._log(f"ERROR: {err}")
                self._set_status("Installation failed. See log above.", DANGER)
                self.root.after(0, lambda: self.install_btn.config(
                    state="normal", text="Retry"
                ))
            except Exception as e:
                self._log(f"ERROR: {e}")
                self._set_status("Installation failed. See log above.", DANGER)
                self.root.after(0, lambda: self.install_btn.config(
                    state="normal", text="Retry"
                ))

        threading.Thread(target=run, daemon=True).start()

    def _finish(self):
        self.install_btn.config(
            text="Installed!",
            bg=SUCCESS,
            state="disabled",
        )
        launch_kairos()
        self.root.after(2000, self.root.destroy)


# =============================================================================
#  ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Quick sanity check — needs Python 3.9+
    if sys.version_info < (3, 9):
        print("KAIROS requires Python 3.9 or newer.")
        print(f"You have Python {sys.version}")
        input("Press Enter to exit...")
        sys.exit(1)

    InstallerApp()