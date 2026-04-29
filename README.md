# T3RMIN4L v2

> Lightweight Windows Terminal theme manager — browse, create, preview, and apply themes without touching a config file.

![Python](https://img.shields.io/badge/Python-3.11+-00ffcc?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-6272a4?style=flat-square&logo=windows&logoColor=white)
![UI](https://img.shields.io/badge/UI-customtkinter-bd93f9?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-50fa7b?style=flat-square)

---

## What's New in v2

- **10 built-in themes** — T3RMIN4L Dark, Cyber Neon, Midnight Frost, Amber Terminal, Crimson Void, Arctic Pulse, Matrix Green, Violet Core, Obsidian Glass, Retro DOS
- **Persistent custom themes** — survive restarts and reboots, stored as JSON in `themes/`
- **Duplicate & Rename** — clone any theme or rename custom ones in one click
- **Theme validation** — invalid colors and missing fields are caught before applying
- **App state persistence** — remembers last selected theme, window size, and recent background
- **PyInstaller EXE support** — compile to a standalone `.exe` with one command
- **Split sidebar** — built-in and custom themes in separate sections
- **Improved import** — full validation with clear error messages on failure

---

## Install

```bash
git clone https://github.com/yourusername/T3RMIN4L.git
cd T3RMIN4L
pip install -r requirements.txt
python main.py
```

---

## Build as EXE

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

The generated `dist/main.exe` can be renamed to `T3RMIN4L.exe` and distributed.  
It preserves saved themes, backups, and settings — all stored next to the executable.

> **Note:** After building, copy your `themes/` folder next to the `.exe` so custom themes persist.

---

## Project Structure

```
T3RMIN4L/
├── main.py          — Entry point, PyInstaller-safe
├── ui.py            — Full UI (customtkinter)
├── themes.py        — settings.json CRUD, validation, 10 built-in themes
├── quicktheme.py    — CSS-like theme parser
├── background.py    — Background image handling (PNG/JPG/GIF)
├── backup.py        — Timestamped backup and restore
├── settings.py      — Persistent app state + custom theme file management
├── requirements.txt
├── README.md
└── themes/          — Custom themes stored here as .json files
```

---

## Quick Theme Syntax

```
background: #0a0a0f;
foreground: #e8e8f0;
cursor: #00ffcc;
selection: #2a2a4a;
black: #000000;   red:    #ff5555;
green: #50fa7b;   yellow: #f1fa8c;
blue:  #6272a4;   purple: #bd93f9;
cyan:  #8be9fd;   white:  #f8f8f2;
font: Cascadia Code;
opacity: 85;
```

---

## Built-in Themes

| Theme | Style |
|-------|-------|
| T3RMIN4L Dark | Deep navy, cyan accent |
| Cyber Neon | Black, electric magenta/green |
| Midnight Frost | GitHub Dark, blue tones |
| Amber Terminal | Retro amber monochrome |
| Crimson Void | Deep red, rose tones |
| Arctic Pulse | Ice blue, teal accents |
| Matrix Green | Classic green-on-black |
| Violet Core | Deep purple, violet accents |
| Obsidian Glass | VS Code Dark+ inspired |
| Retro DOS | Classic blue DOS palette |

---

## Custom Theme Persistence

Custom themes created via Quick Theme or imported from files are saved to `themes/` as individual `.json` files.

They survive:
- App restarts
- System reboots
- EXE rebuilds (as long as `themes/` folder stays next to the executable)

---

## Background Images

| Format | Support |
|--------|---------|
| PNG | ✅ Full |
| JPG / JPEG | ✅ Full |
| GIF | ⚠️ First frame extracted automatically |

Controls: opacity, stretch mode, alignment, blur, acrylic.

---

## Backups

- Auto-backup before every save
- Up to 10 backups kept
- One-click restore from Backup Manager
- Location: `%LOCALAPPDATA%\...\LocalState\t3rminal_backups\`

---

## settings.json Locations (auto-detected)

| Edition | Path |
|---------|------|
| Stable | `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json` |
| Preview | `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json` |
| Unpackaged | `%LOCALAPPDATA%\Microsoft\Windows Terminal\settings.json` |

---

## License

MIT
