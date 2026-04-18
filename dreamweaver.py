import os
import sys
import json
import time
import datetime
import psutil
import threading
import subprocess
import pystray
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from rich.console import Console
from plyer import notification
from PIL import Image, ImageDraw

load_dotenv()
console = Console()


# =============================================================================
#  SETTINGS
# =============================================================================

SETTINGS_PATH = Path.home() / ".kairos-dreamweaver" / "settings.json"

DEFAULT_SETTINGS = {
    "groq_api_key": os.getenv("GROQ_API_KEY", ""),
    "model_name": "llama-3.3-70b-versatile",
    "wake_hour": 7,
    "idle_timeout_minutes": 10,
    "projects": [],
}

MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]


def load_settings() -> dict:
    SETTINGS_PATH.parent.mkdir(exist_ok=True, parents=True)
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_SETTINGS, **data}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    SETTINGS_PATH.parent.mkdir(exist_ok=True, parents=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


# =============================================================================
#  THEME DETECTION
# =============================================================================

def is_dark_mode() -> bool:
    try:
        if sys.platform == "win32":
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        elif sys.platform == "darwin":
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
            )
            return "Dark" in result.stdout
    except Exception:
        pass
    return False


def get_theme_colors(dark: bool) -> dict:
    if dark:
        return {
            "bg":         "#12121f",
            "surface":    "#1a1a2e",
            "card":       "#1e1e35",
            "accent":     "#7c6fcd",
            "accent_dim": "#5a4fa0",
            "text":       "#e0e0f0",
            "subtext":    "#8888aa",
            "entry_bg":   "#0e0e1c",
            "border":     "#2e2e50",
            "btn_fg":     "#ffffff",
            "success":    "#4caf82",
            "danger":     "#e05c5c",
        }
    else:
        return {
            "bg":         "#f4f4f8",
            "surface":    "#ffffff",
            "card":       "#eaeaf5",
            "accent":     "#5b4fcf",
            "accent_dim": "#4a3fbf",
            "text":       "#1a1a2e",
            "subtext":    "#555575",
            "entry_bg":   "#ffffff",
            "border":     "#c8c8e0",
            "btn_fg":     "#ffffff",
            "success":    "#2e7d52",
            "danger":     "#c0392b",
        }


# =============================================================================
#  SETTINGS WINDOW
# =============================================================================

def show_settings_window():
    settings = load_settings()
    dark = is_dark_mode()
    c = get_theme_colors(dark)

    projects = list(settings.get("projects", []))

    root = tk.Tk()
    root.title("KAIROS  -  Settings")
    root.geometry("520x600")
    root.resizable(True, True)
    root.minsize(480, 500)
    root.configure(bg=c["bg"])
    root.attributes("-topmost", True)

    # Center on screen
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"520x600+{(sw - 520) // 2}+{(sh - 600) // 2}")

    # ------------------------------------------------------------------
    # Header  (fixed — never scrolls)
    # ------------------------------------------------------------------
    header = tk.Frame(root, bg=c["accent"], height=56)
    header.pack(fill="x", side="top")
    header.pack_propagate(False)
    tk.Label(
        header,
        text="  KAIROS  -  Settings",
        font=("Segoe UI", 14, "bold"),
        bg=c["accent"],
        fg="#ffffff",
        anchor="w",
    ).pack(side="left", padx=22, pady=14)

    # ------------------------------------------------------------------
    # Footer  (packed BEFORE canvas so it is always visible)
    # ------------------------------------------------------------------
    footer = tk.Frame(root, bg=c["surface"], pady=12, padx=24)
    footer.pack(fill="x", side="bottom")

    tk.Frame(footer, bg=c["border"], height=1).pack(fill="x", side="top", pady=(0, 10))

    status_var = tk.StringVar()
    tk.Label(
        footer,
        textvariable=status_var,
        font=("Segoe UI", 9),
        bg=c["surface"],
        fg=c["success"],
    ).pack(side="left")

    def on_cancel():
        root.destroy()

    def on_save():
        try:
            new_settings = {
                "groq_api_key": api_var.get().strip(),
                "model_name": model_var.get(),
                "wake_hour": int(wake_var.get()),
                "idle_timeout_minutes": int(idle_var.get()),
                "projects": projects,
            }
            save_settings(new_settings)
            status_var.set("Saved!  Restart KAIROS for changes to take effect.")
            root.after(2500, root.destroy)
        except Exception as e:
            messagebox.showerror("KAIROS", f"Could not save settings:\n{e}")

    tk.Button(
        footer,
        text="Cancel",
        font=("Segoe UI", 10),
        bg=c["card"], fg=c["text"],
        activebackground=c["border"],
        relief="flat", bd=0,
        padx=16, pady=7,
        cursor="hand2",
        command=on_cancel,
    ).pack(side="right", padx=(8, 0))

    tk.Button(
        footer,
        text="Save Settings",
        font=("Segoe UI", 10, "bold"),
        bg=c["accent"], fg=c["btn_fg"],
        activebackground=c["accent_dim"],
        relief="flat", bd=0,
        padx=16, pady=7,
        cursor="hand2",
        command=on_save,
    ).pack(side="right")

    # ------------------------------------------------------------------
    # Scrollable canvas  (sits between header and footer)
    # ------------------------------------------------------------------
    canvas_frame = tk.Frame(root, bg=c["bg"])
    canvas_frame.pack(fill="both", expand=True, side="top")

    canvas = tk.Canvas(canvas_frame, bg=c["bg"], highlightthickness=0, bd=0)
    vscroll = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vscroll.set)

    vscroll.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    body = tk.Frame(canvas, bg=c["bg"])
    body_window = canvas.create_window((0, 0), window=body, anchor="nw")

    def on_body_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event):
        canvas.itemconfig(body_window, width=event.width)

    body.bind("<Configure>", on_body_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    pad = tk.Frame(body, bg=c["bg"], padx=28, pady=10)
    pad.pack(fill="x")

    # ------------------------------------------------------------------
    # Helper widgets
    # ------------------------------------------------------------------
    def section_label(text):
        tk.Label(
            pad, text=text,
            font=("Segoe UI", 9, "bold"),
            bg=c["bg"], fg=c["accent"],
        ).pack(anchor="w", pady=(16, 3))
        tk.Frame(pad, bg=c["border"], height=1).pack(fill="x", pady=(0, 10))

    def make_entry(label, show=None):
        tk.Label(
            pad, text=label, font=("Segoe UI", 9),
            bg=c["bg"], fg=c["subtext"],
        ).pack(anchor="w")
        var = tk.StringVar()
        tk.Entry(
            pad, textvariable=var, font=("Segoe UI", 10),
            bg=c["entry_bg"], fg=c["text"],
            insertbackground=c["text"],
            relief="flat", bd=6, show=show or "",
        ).pack(fill="x", ipady=6, pady=(2, 2))
        tk.Frame(pad, bg=c["border"], height=1).pack(fill="x", pady=(0, 8))
        return var

    def make_spinbox(label, from_, to_):
        tk.Label(
            pad, text=label, font=("Segoe UI", 9),
            bg=c["bg"], fg=c["subtext"],
        ).pack(anchor="w")
        var = tk.IntVar()
        tk.Spinbox(
            pad, from_=from_, to=to_, textvariable=var,
            font=("Segoe UI", 10), bg=c["entry_bg"], fg=c["text"],
            buttonbackground=c["card"], relief="flat", bd=6,
            insertbackground=c["text"],
        ).pack(fill="x", ipady=5, pady=(2, 2))
        tk.Frame(pad, bg=c["border"], height=1).pack(fill="x", pady=(0, 8))
        return var

    def make_dropdown(label, choices):
        tk.Label(
            pad, text=label, font=("Segoe UI", 9),
            bg=c["bg"], fg=c["subtext"],
        ).pack(anchor="w")
        var = tk.StringVar()
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "K.TCombobox",
            fieldbackground=c["entry_bg"], background=c["entry_bg"],
            foreground=c["text"], selectbackground=c["accent"],
            selectforeground="#ffffff", arrowcolor=c["accent"],
        )
        ttk.Combobox(
            pad, textvariable=var, values=choices, state="readonly",
            style="K.TCombobox", font=("Segoe UI", 10),
        ).pack(fill="x", ipady=5, pady=(2, 2))
        tk.Frame(pad, bg=c["border"], height=1).pack(fill="x", pady=(0, 8))
        return var

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    section_label("API Configuration")
    api_var = make_entry("Groq API Key", show="*")
    api_var.set(settings.get("groq_api_key", ""))

    model_var = make_dropdown("Model", MODELS)
    current_model = settings.get("model_name", MODELS[0])
    model_var.set(current_model if current_model in MODELS else MODELS[0])

    section_label("Schedule")
    wake_var = make_spinbox("Morning report hour  (0 = midnight,  7 = 7 AM)", 0, 23)
    wake_var.set(settings.get("wake_hour", 7))

    idle_var = make_spinbox("Idle timeout in minutes before auto-report", 1, 120)
    idle_var.set(settings.get("idle_timeout_minutes", 10))

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------
    section_label("Projects")

    tk.Label(
        pad,
        text="KAIROS will dream about each project below.",
        font=("Segoe UI", 9),
        bg=c["bg"], fg=c["subtext"],
    ).pack(anchor="w", pady=(0, 6))

    list_frame = tk.Frame(pad, bg=c["entry_bg"])
    list_frame.pack(fill="x", pady=(0, 6))

    proj_scroll = tk.Scrollbar(list_frame, orient="vertical", bg=c["card"])
    project_listbox = tk.Listbox(
        list_frame,
        font=("Segoe UI", 9),
        bg=c["entry_bg"], fg=c["text"],
        selectbackground=c["accent"], selectforeground="#ffffff",
        relief="flat", bd=8, height=4,
        activestyle="none",
        yscrollcommand=proj_scroll.set,
    )
    proj_scroll.config(command=project_listbox.yview)
    proj_scroll.pack(side="right", fill="y")
    project_listbox.pack(fill="x", expand=True)

    def refresh_listbox():
        project_listbox.delete(0, tk.END)
        for p in projects:
            project_listbox.insert(tk.END, f"  {p['name']}   -   {p['path']}")

    refresh_listbox()

    proj_btn_row = tk.Frame(pad, bg=c["bg"])
    proj_btn_row.pack(fill="x", pady=(6, 0))

    def add_project():
        folder = filedialog.askdirectory(title="Select Project Folder", parent=root)
        if not folder:
            return
        name = simpledialog.askstring(
            "Project Name",
            "Give this project a short name:",
            initialvalue=Path(folder).name,
            parent=root,
        )
        if not name or not name.strip():
            return
        projects.append({"name": name.strip(), "path": str(Path(folder).resolve())})
        refresh_listbox()

    def remove_project():
        selected = project_listbox.curselection()
        if not selected:
            messagebox.showinfo("KAIROS", "Select a project from the list first.", parent=root)
            return
        idx = selected[0]
        confirmed = messagebox.askyesno(
            "Remove Project",
            f"Remove '{projects[idx]['name']}' from KAIROS?\n\nNo files will be deleted.",
            parent=root,
        )
        if confirmed:
            projects.pop(idx)
            refresh_listbox()

    tk.Button(
        proj_btn_row,
        text="+ Add Project",
        font=("Segoe UI", 9, "bold"),
        bg=c["accent"], fg=c["btn_fg"],
        activebackground=c["accent_dim"],
        relief="flat", bd=0, padx=14, pady=6,
        cursor="hand2", command=add_project,
    ).pack(side="left")

    tk.Button(
        proj_btn_row,
        text="- Remove Selected",
        font=("Segoe UI", 9),
        bg=c["card"], fg=c["danger"],
        activebackground=c["border"],
        relief="flat", bd=0, padx=14, pady=6,
        cursor="hand2", command=remove_project,
    ).pack(side="left", padx=(10, 0))

    tk.Label(
        pad,
        text="Restart KAIROS after adding or removing projects.",
        font=("Segoe UI", 8),
        bg=c["bg"], fg=c["subtext"],
    ).pack(anchor="w", pady=(10, 20))

    root.mainloop()


# =============================================================================
#  CHAT WINDOW
# =============================================================================

def show_chat_window():
    settings = load_settings()
    dark = is_dark_mode()
    c = get_theme_colors(dark)

    api_key = settings.get("groq_api_key") or os.getenv("GROQ_API_KEY", "")
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
    llm = ChatGroq(
        model=settings.get("model_name", "llama-3.3-70b-versatile"),
        temperature=0.8,
        max_tokens=2800,
    )

    # ------------------------------------------------------------------
    # Load recent dream reports as memory context
    # ------------------------------------------------------------------
    def load_dream_context() -> str:
        dreams_folder = Path.cwd() / "dreams"
        if not dreams_folder.exists():
            return "No dream reports found yet."
        reports = sorted(dreams_folder.glob("dream_*.md"), key=os.path.getmtime, reverse=True)
        if not reports:
            return "No dream reports found yet."
        # Load the 3 most recent reports
        context_parts = []
        for report in reports[:3]:
            try:
                text = report.read_text(encoding="utf-8", errors="ignore")
                context_parts.append(f"=== {report.name} ===\n{text[:2000]}")
            except Exception:
                pass
        return "\n\n".join(context_parts)

    dream_context = load_dream_context()

    SYSTEM_PROMPT = f"""You are KAIROS, a mystical AI coding companion who dreams about the developer's projects.

You have recently generated dream reports for the developer's projects. Here are your most recent dream reports:

{dream_context}

When the developer asks about their projects, their code, action items, or anything you dreamed about:
- Answer based on the dream reports above
- Stay in character as KAIROS — mystical, poetic, but practical
- Reference specific details from the reports when relevant
- If asked for more action items, draw from what you observed in the reports
- If asked about something not in the reports, say so honestly but stay in character

You remember everything you dreamed. The developer can ask you follow-up questions about any project."""

    # Conversation history for multi-turn chat
    conversation_history = []

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    root = tk.Tk()
    root.title("Chat with KAIROS")
    root.geometry("680x520")
    root.configure(bg=c["bg"])
    root.attributes("-topmost", True)

    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"680x520+{(sw - 680) // 2}+{(sh - 520) // 2}")

    header = tk.Frame(root, bg=c["accent"], height=56)
    header.pack(fill="x", side="top")
    header.pack_propagate(False)
    tk.Label(
        header,
        text="  Chat with KAIROS",
        font=("Segoe UI", 14, "bold"),
        bg=c["accent"], fg="#ffffff", anchor="w",
    ).pack(side="left", padx=22, pady=14)

    input_frame = tk.Frame(root, bg=c["surface"], pady=10, padx=12)
    input_frame.pack(fill="x", side="bottom")
    tk.Frame(input_frame, bg=c["border"], height=1).pack(fill="x", side="top", pady=(0, 8))

    input_var = tk.StringVar()
    entry = tk.Entry(
        input_frame, textvariable=input_var,
        font=("Segoe UI", 10),
        bg=c["entry_bg"], fg=c["text"],
        insertbackground=c["text"],
        relief="flat", bd=6,
    )
    entry.pack(side="left", fill="x", expand=True, ipady=8)

    chat_frame = tk.Frame(root, bg=c["bg"])
    chat_frame.pack(fill="both", expand=True, padx=12, pady=(8, 0))

    chat_scroll = tk.Scrollbar(chat_frame, orient="vertical")
    chat_text = tk.Text(
        chat_frame,
        font=("Segoe UI", 10),
        bg=c["surface"], fg=c["text"],
        relief="flat", bd=0,
        wrap="word",
        state="disabled",
        yscrollcommand=chat_scroll.set,
    )
    chat_scroll.config(command=chat_text.yview)
    chat_scroll.pack(side="right", fill="y")
    chat_text.pack(fill="both", expand=True)

    chat_text.tag_config("user",     foreground=c["accent"],  font=("Segoe UI", 10, "bold"))
    chat_text.tag_config("kairos",   foreground=c["success"],  font=("Segoe UI", 10))
    chat_text.tag_config("thinking", foreground=c["subtext"], font=("Segoe UI", 9, "italic"))
    chat_text.tag_config("error",    foreground=c["danger"],   font=("Segoe UI", 10))

    def append(text, tag):
        chat_text.config(state="normal")
        chat_text.insert("end", text, tag)
        chat_text.config(state="disabled")
        chat_text.see("end")
        chat_text.update_idletasks()

    def remove_last_line():
        chat_text.config(state="normal")
        chat_text.delete("end-2l linestart", "end-1l linestart")
        chat_text.config(state="disabled")

    def send_message(event=None):
        user_text = input_var.get().strip()
        if not user_text:
            return
        input_var.set("")
        entry.focus_set()

        conversation_history.append({"role": "user", "content": user_text})
        append(f"You: {user_text}\n\n", "user")
        append("KAIROS is thinking...\n\n", "thinking")

        def call_llm():
            try:
                from langchain_core.messages import SystemMessage
                messages = [SystemMessage(content=SYSTEM_PROMPT)]
                for turn in conversation_history:
                    if turn["role"] == "user":
                        messages.append(HumanMessage(content=turn["content"]))
                    else:
                        from langchain_core.messages import AIMessage
                        messages.append(AIMessage(content=turn["content"]))

                response = llm.invoke(messages)
                ai_text = response.content.strip()
                conversation_history.append({"role": "assistant", "content": ai_text})

                root.after(0, lambda: [
                    remove_last_line(),
                    append(f"KAIROS: {ai_text}\n\n", "kairos"),
                ])
            except Exception as e:
                root.after(0, lambda: [
                    remove_last_line(),
                    append(f"Error: {e}\n\n", "error"),
                ])

        threading.Thread(target=call_llm, daemon=True).start()

    send_btn = tk.Button(
        input_frame,
        text="Send",
        font=("Segoe UI", 10, "bold"),
        bg=c["accent"], fg="#ffffff",
        activebackground=c["accent_dim"],
        relief="flat", bd=0,
        padx=20, pady=8,
        cursor="hand2",
        command=send_message,
    )
    send_btn.pack(side="right", padx=(10, 0))

    entry.bind("<Return>", send_message)
    root.after(100, entry.focus_set)

    # Greet the user so they know KAIROS has context
    project_names = [p["name"] for p in settings.get("projects", [])]
    if project_names:
        greeting = f"I've been dreaming about {', '.join(project_names)}. Ask me anything about your projects."
    else:
        greeting = "I've been dreaming about your work. Ask me anything about your projects."
    append(f"KAIROS: {greeting}\n\n", "kairos")

    root.mainloop()


# =============================================================================
#  MAIN APP
# =============================================================================

class KairosDreamweaver:
    def __init__(self):
        self.settings = load_settings()

        api_key = self.settings.get("groq_api_key") or os.getenv("GROQ_API_KEY", "")
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key

        self.llm = ChatGroq(
            model=self.settings.get("model_name", "llama-3.3-70b-versatile"),
            temperature=0.8,
            max_tokens=2800,
        )
        self.last_activity = time.time()
        self.is_running = True
        self.watch_folder = Path.cwd()
        self.dreams_folder = Path.cwd() / "dreams"
        self.dreams_folder.mkdir(exist_ok=True, parents=True)

    # ------------------------------------------------------------------
    # Context helpers
    # ------------------------------------------------------------------

    def get_git_info(self, folder: Path) -> str:
        try:
            status = subprocess.check_output(
                ["git", "-C", str(folder), "status", "--short"],
                stderr=subprocess.DEVNULL, timeout=3,
            ).decode()
            log = subprocess.check_output(
                ["git", "-C", str(folder), "log", "--oneline", "-5"],
                stderr=subprocess.DEVNULL, timeout=3,
            ).decode()
            return f"Recent Git Status:\n{status}\nRecent Commits:\n{log}"
        except Exception:
            return "No git repository detected."

    def read_key_files(self, folder: Path) -> str:
        content = []
        key_files = [
            "README.md", "package.json", "CLAUDE.md",
            "index.js", "App.tsx", "main.py", "src/App.js",
        ]
        for file in key_files:
            file_path = folder / file
            if file_path.exists():
                try:
                    text = file_path.read_text(encoding="utf-8", errors="ignore")
                    content.append(f"--- {file} ---\n{text[:800]}...\n")
                except Exception:
                    pass
        return "\n".join(content) if content else "No key files found."

    def get_project_context(self, folder: Path) -> str:
        git_info = self.get_git_info(folder)
        files = self.read_key_files(folder)
        return (
            f"Project Path: {folder}\n"
            f"{git_info}\n"
            f"Key Files Content:\n{files}"
        )

    def update_context(self):
        self.project_context = self.get_project_context(self.watch_folder)

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    def save_dream_report(self, report_text: str, project_folder: Path):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            project_name = project_folder.name
            filename = self.dreams_folder / f"dream_{project_name}_{timestamp}.md"

            header = "# KAIROS Dream Report\n"
            header += f"> **Project:** `{project_folder}`\n"
            header += f"> **Dreamed:** {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}\n\n"
            header += "---\n\n"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(header + report_text)

            console.print(f"[dim]Report saved: {filename.name}[/dim]")
            notification.notify(
                title="KAIROS Dream Report Ready",
                message=f"New dream for '{project_name}' is waiting for you.",
                timeout=8,
            )
        except Exception as e:
            console.print(f"[red]Save error: {e}[/red]")

    def generate_dream_report(self, auto=False, folder: Path = None):
        target = folder or self.watch_folder
        context = self.get_project_context(target)
        now_str = datetime.datetime.now().strftime("%H:%M on %B %d, %Y")
        auto_line = "This vision arrived automatically at dawn." if auto else ""

        prompt = f"""
You are KAIROS, a mystical AI coding companion who dreams about the developer's project while they rest.

Project context: {context}

Write a dream report in this EXACT markdown structure:

---

## The Dream

Write 2-3 paragraphs of vivid, surreal, poetic narrative. Reference real filenames,
function names, or git commits from the project context above. Make it feel like
an actual dream - abstract but grounded in their real code.

---

## What Shifted in the Night

List exactly 3 observations about the project's current state. Be specific and
insightful, referencing real details from the code or git history.

- **[Observation title]:** One sentence of detail.
- **[Observation title]:** One sentence of detail.
- **[Observation title]:** One sentence of detail.

---

## Morning Spells (Action Items)

List exactly 3 concrete, actionable suggestions the developer can act on today.
Each must reference something real from the project.

1. **[Action title]:** Clear one-sentence instruction with a specific file or area to focus on.
2. **[Action title]:** Clear one-sentence instruction with a specific file or area to focus on.
3. **[Action title]:** Clear one-sentence instruction with a specific file or area to focus on.

---

## Dream Residue

One final short, poetic, mysterious closing line. Like a fortune cookie written by a poet.

---

- KAIROS, dreaming at {now_str}

{auto_line}
"""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            full_report = response.content
            console.print(
                f"\n[bold magenta]KAIROS DREAM REPORT - {target.name}[/bold magenta]\n"
                + full_report
            )
            self.save_dream_report(full_report, target)
        except Exception as e:
            console.print(f"[red]Report generation failed for {target.name}: {e}[/red]")

    def generate_all_reports(self, auto=False):
        projects = load_settings().get("projects", [])

        if not projects:
            console.print("[yellow]No projects configured. Dreaming about current folder...[/yellow]")
            threading.Thread(
                target=self.generate_dream_report,
                kwargs={"auto": auto},
                daemon=True,
            ).start()
            return

        console.print(f"[bold cyan]Dreaming about {len(projects)} project(s) in parallel...[/bold cyan]")
        for p in projects:
            path = Path(p["path"])
            if path.exists():
                threading.Thread(
                    target=self.generate_dream_report,
                    kwargs={"auto": auto, "folder": path},
                    daemon=True,
                ).start()
            else:
                console.print(f"[yellow]Skipping '{p['name']}' - folder not found: {path}[/yellow]")

    # ------------------------------------------------------------------
    # Change Watch Folder — FIX: added focus_force so dialog is interactive
    # ------------------------------------------------------------------

    def change_watch_folder(self):
            script = (
                "import tkinter as tk;"
                "from tkinter import filedialog;"
                "root = tk.Tk();"
                "root.withdraw();"
                "root.attributes('-topmost', True);"
                "root.focus_force();"
                "folder = filedialog.askdirectory(title='KAIROS: Select Project Folder');"
                "print(folder);"
                "root.destroy();"
            )
            try:
                result = subprocess.run(
                    [sys.executable, "-c", script],
                    capture_output=True, text=True, timeout=60,
                )
                folder = result.stdout.strip()
                if folder:
                    new_path = Path(folder).resolve()
                    if new_path.exists():
                        self.watch_folder = new_path
                        console.print(f"[bold green]Now watching: {self.watch_folder}[/bold green]")

                        # Persist to settings.json so it survives restart
                        current_settings = load_settings()
                        projects = current_settings.get("projects", [])
                        existing_paths = [p["path"] for p in projects]
                        if str(new_path) not in existing_paths:
                            projects.append({
                                "name": new_path.name,
                                "path": str(new_path),
                            })
                            current_settings["projects"] = projects
                            save_settings(current_settings)
                            console.print(f"[dim]Project '{new_path.name}' saved to settings.[/dim]")
                    else:
                        console.print("[red]Folder not found![/red]")
                else:
                    console.print("[yellow]No folder selected.[/yellow]")
            except Exception as e:
                console.print(f"[red]Folder picker failed: {e}[/red]")

    def open_settings(self):
        subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--settings"]
        )

    def restart(self):
        console.print("[yellow]Restarting KAIROS...[/yellow]")
        self.is_running = False
        subprocess.Popen([sys.executable, str(Path(__file__).resolve())])
        os._exit(0)

    # ------------------------------------------------------------------
    # Background daemon
    # ------------------------------------------------------------------

    def background_daemon(self):
        while self.is_running:
            try:
                s = load_settings()
                wake_hour = s.get("wake_hour", 7)
                idle_minutes = s.get("idle_timeout_minutes", 10)

                now = datetime.datetime.now()
                if now.hour == wake_hour and now.minute == 0:
                    self.generate_all_reports(auto=True)

                idle = all(
                    "code" not in p.info["name"].lower()
                    and "cursor" not in p.info["name"].lower()
                    and "vscode" not in p.info["name"].lower()
                    for p in psutil.process_iter(["name"])
                )
                if idle and time.time() - self.last_activity > idle_minutes * 60:
                    self.generate_all_reports(auto=True)
                    self.last_activity = time.time()
            except Exception:
                pass
            time.sleep(60)


# =============================================================================
#  TRAY MENU BUILDER
# =============================================================================

def build_tray_menu(dw: KairosDreamweaver) -> pystray.Menu:
    projects = load_settings().get("projects", [])

    report_items = [
        pystray.MenuItem(
            "All Projects",
            lambda icon, item: threading.Thread(
                target=dw.generate_all_reports, daemon=True
            ).start(),
        ),
    ]

    if projects:
        report_items.append(pystray.Menu.SEPARATOR)
        for p in projects:
            path = Path(p["path"])
            name = p["name"]

            def make_report_action(_path=path):
                def action(icon, item):
                    threading.Thread(
                        target=dw.generate_dream_report,
                        kwargs={"folder": _path},
                        daemon=True,
                    ).start()
                return action

            report_items.append(pystray.MenuItem(name, make_report_action()))

    def chat_action(icon, item):
        subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--chat"]
        )

    return pystray.Menu(
        pystray.MenuItem("Dream Reports", pystray.Menu(*report_items)),
        pystray.MenuItem("Chat with KAIROS", chat_action),
        pystray.MenuItem("Change Watch Folder", lambda icon, item: dw.change_watch_folder()),
        pystray.MenuItem("Settings", lambda icon, item: dw.open_settings()),
        pystray.MenuItem("Open Dreams Folder", lambda icon, item: os.startfile(str(dw.dreams_folder))),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Restart KAIROS", lambda icon, item: dw.restart()),
        pystray.MenuItem("Quit", lambda icon, item: icon.stop()),
    )


# =============================================================================
#  ICON
# =============================================================================

def create_image():
    try:
        img = Image.open(Path(__file__).parent / "moon_icon.png").convert("RGBA")
        img = img.resize((64, 64), Image.LANCZOS)
        return img
    except Exception:
        size = 64
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((0, 0, size, size), fill=(15, 15, 35, 255))
        draw.ellipse((8, 8, 56, 56), fill=(255, 223, 100, 255))
        draw.ellipse((18, 5, 62, 54), fill=(15, 15, 35, 255))
        draw.arc((8, 8, 56, 56), start=120, end=300, fill=(255, 245, 180, 200), width=2)
        draw.point((12, 14), fill=(255, 255, 255, 255))
        draw.point((10, 28), fill=(255, 255, 200, 180))
        draw.point((18, 52), fill=(255, 255, 255, 200))
        draw.point((6, 44), fill=(200, 220, 255, 160))
        return image


# =============================================================================
#  ENTRY POINT
# =============================================================================

def main():
    dw = KairosDreamweaver()
    threading.Thread(target=dw.background_daemon, daemon=True).start()

    menu = build_tray_menu(dw)
    icon = pystray.Icon("KAIROS", create_image(), "KAIROS Dreamweaver", menu)
    console.print("[bold cyan]KAIROS is now running in the system tray![/bold cyan]")
    icon.run()


if __name__ == "__main__":
    if "--settings" in sys.argv:
        show_settings_window()
        sys.exit(0)
    elif "--chat" in sys.argv:
        show_chat_window()
        sys.exit(0)
    main()
