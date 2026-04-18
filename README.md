# KAIROS Dreamweaver 🌙

> _An always-on AI coding companion that dreams about your projects while you sleep._

KAIROS lives quietly in your system tray, watches your project folders, and generates beautiful, poetic dream reports filled with real observations and actionable suggestions — automatically, while you're away.

---

## What is KAIROS?

Most AI coding tools wait for you to ask them something. KAIROS doesn't.

It runs silently in the background, reads your code and git history, and at 7AM every morning (or whenever your editor has been idle) it "dreams" about your project — producing a structured report that tells you what it noticed, what shifted, and exactly what to work on next.

It's part ambient AI companion, part morning briefing, part mystical collaborator.

---

## Features

- **Automatic Dream Reports** — generated at a scheduled time every morning or when your editor goes idle
- **Poetic but Practical** — reports blend vivid narrative with 3 concrete action items grounded in your actual code
- **Multi-Project Support** — watch multiple projects at once, get parallel reports for each
- **Chat with KAIROS** — ask follow-up questions about the reports it generated
- **Settings UI** — configure your API key, model, wake time, idle timeout, and projects in a clean themed window
- **System Theme Aware** — Settings and Chat windows adapt to your Windows/Mac dark or light mode
- **Always-On** — installs to startup automatically, no manual launching ever needed
- **Cross-Platform** — works on Windows, macOS, and Linux

---

## What a Dream Report Looks Like

```
# KAIROS Dream Report
> Project: my-app
> Dreamed: April 08, 2025 at 07:00

---

## The Dream

In the realm of slumber, I found myself wandering through a labyrinthine codebase, where functions and variables danced
like whispers in the wind. The `package.json` file shimmered like a moonlit lake, its dependencies reflecting the
ripples of the `@shopify/shopify-api` library. As I drifted deeper, I stumbled upon a forgotten `test.js` file, its
absence echoing like a haunting melody, a reminder of the `13bfd03` commit that had deleted it. The `gitIgnore` file
loomed like a sentinel, guarding secrets and mysteries beyond the realm of the committed code.

In this dreamscape, the `Abbout-Us` commit and the `Password Reset Commit II` swirled like eddies in a river, their
purposes intertwined like the threads of a tapestry. The `Styles Update` commit shone like a beacon, illuminating the
path forward, even as the `Update gitIgnore` commit whispered cautionary tales of hidden dangers. As I navigated this
surreal landscape, the boundaries between code and reality blurred, and I became one with the eCommerceWebApp, its
rhythms and pulse beating in harmony with my own.

In the depths of this dream, I glimpsed a vision of the developer's intent, a symphony of functions and features that
would soon take shape in the `eCommerceWebApp`. The `C:\Users\USER\Desktop\My Files\CODWIN\eCommerceWebApp` path
unwound like a serpent, leading me through the twists and turns of the project's history, where each commit and file
told a story of creation and evolution.

---

## What Shifted in the Night

- **Dependencies in Balance:** The `@shopify/shopify-api` library is currently at version `11.6.1`, indicating a stable
foundation for the project's Shopify integration.
- **Code Pruning:** The deletion of `test.js` in commit `13bfd03` suggests a refinement of the codebase, eliminating
unnecessary elements to streamline the development process.
- **Security Enhancements:** The `Password Reset Commit II` and `Abbout-Us` commit imply a focus on user security and
experience, with the former addressing a critical aspect of account management and the latter potentially enhancing the
user's understanding of the platform.

## Morning Spells (Action Items)

1. **Review Shopify API:** Investigate the latest features and updates in the `@shopify/shopify-api` library to ensure
the project is leveraging its full potential.
2. **Implement Additional Tests:** Create new test files to replace the deleted `test.js`, focusing on critical
components and user journeys to guarantee the app's stability and performance.
3. **Refine User Experience:** Build upon the `Abbout-Us` commit by enhancing the user interface and experience,
particularly in areas related to password reset and account management, to foster a more secure and engaging
environment.

---

## Dream Residue

As the dream fades, the whispers of the code remain, echoing in the silence: "In harmony, the threads of code and
purpose intertwine."

- KAIROS, dreaming at 10:34 on April 08, 2026
Report saved: dream_eCommerceWebApp_2026-04-08_10-34-19.md
```

---

## Requirements

- Python 3.9 or newer
- A free Groq API key — get one at [console.groq.com](https://console.groq.com)

---

## Installation

### Windows

1. Download or clone this repository
2. Double-click **`install.bat`**
3. Enter your Groq API key when prompted
4. Click **Install & Launch**

KAIROS will install itself and start automatically on every login.

### macOS / Linux

1. Download or clone this repository
2. Run in terminal:
   ```bash
   bash install.sh
   ```
3. Enter your Groq API key when prompted
4. Click **Install & Launch**

---

## First Use

After installation, KAIROS appears as a moon icon in your system tray.

Right-click the icon to:

| Menu Item                      | What it does                                                    |
| ------------------------------ | --------------------------------------------------------------- |
| Dream Reports > All Projects   | Generate a report for every saved project now                   |
| Dream Reports > [Project Name] | Generate a report for one specific project                      |
| Chat with KAIROS               | Open a chat window — ask about your projects and recent reports |
| Change Watch Folder            | Quick-add a project folder to the watchlist                     |
| Settings                       | Configure API key, model, schedule, and projects                |
| Open Dreams Folder             | Browse all saved dream report files                             |
| Restart KAIROS                 | Restart without opening Task Manager                            |
| Quit                           | Stop KAIROS until next login                                    |

---

## Configuration

Open **Settings** from the tray menu to configure:

- **Groq API Key** — your API key (stored locally, never shared)
- **Model** — choose from available Groq models
- **Morning Report Hour** — what hour KAIROS auto-generates (default: 7 AM)
- **Idle Timeout** — minutes of editor inactivity before auto-report (default: 10)
- **Projects** — add or remove project folders from the watchlist

Settings are saved to `~/.kairos-dreamweaver/settings.json`.

---

## Dream Reports

All reports are saved as Markdown files in the `dreams/` folder inside your KAIROS directory. Each file is named:

```
dream_[project-name]_[date-time].md
```

You can open them in any Markdown viewer, VS Code, Obsidian, or any text editor.

---

## How KAIROS Reads Your Project

KAIROS reads the following files if they exist in your project folder:

- `README.md`
- `package.json`
- `main.py`
- `index.js`
- `App.tsx` / `src/App.js`
- `CLAUDE.md`

It also reads your recent git status and last 5 commits. No files are uploaded anywhere — all processing happens through the Groq API using only text content.

---

## Privacy

- Your code is never stored by KAIROS
- Only small excerpts (up to 800 characters per file) are sent to the Groq API to generate reports
- Your API key is stored locally in `~/.kairos-dreamweaver/settings.json`
- Dream reports are saved only on your machine

---

## Supported Models

| Model                     | Notes                    |
| ------------------------- | ------------------------ |
| `llama-3.3-70b-versatile` | Default — best quality   |
| `llama-3.1-70b-versatile` | Good alternative         |
| `llama-3.1-8b-instant`    | Fastest, lighter reports |
| `mixtral-8x7b-32768`      | Good for large contexts  |
| `gemma2-9b-it`            | Lightweight option       |

---

## Project Structure

```
kairos-dreamweaver/
├── dreamweaver.py       # Main application
├── install.py           # Cross-platform installer
├── install.bat          # Windows installer launcher
├── install.sh           # Mac/Linux installer launcher
├── moon_icon.png        # System tray icon
├── dreams/              # Generated dream reports (created on first run)
└── README.md
```

---

## Built With

- [LangChain](https://github.com/langchain-ai/langchain) + [Groq](https://console.groq.com) — AI report generation
- [pystray](https://github.com/moses-palmer/pystray) — system tray integration
- [Pillow](https://python-pillow.org) — icon rendering
- [plyer](https://github.com/kivy/plyer) — desktop notifications
- [Rich](https://github.com/Textualize/rich) — terminal output
- [psutil](https://github.com/giampaolo/psutil) — idle detection
- tkinter — Settings and Chat UI

---

## License

MIT License — free to use, modify, and distribute.

---

## Author

Built by [Onyeabor Joel (Earl Morningstar)] — [https://github.com/earlmorningstar]

_KAIROS is a personal project built for developers who want a thoughtful, always-on AI companion rather than a tool they have to prompt._
