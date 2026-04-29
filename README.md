# T3RMIN4L

> A lightweight Windows Terminal theme manager. Browse, create, preview, and apply themes — without ever touching a config file.

![Python](https://img.shields.io/badge/Python-3.11+-00ffcc?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-6272a4?style=flat-square&logo=windows&logoColor=white)
![UI](https://img.shields.io/badge/UI-customtkinter-bd93f9?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-50fa7b?style=flat-square)

---

## What is T3RMIN4L?

T3RMIN4L is a desktop app for Windows that lets you manage color themes for [Windows Terminal](https://aka.ms/terminal) through a clean, dark GUI — no manual JSON editing required.

**Features at a glance:**

-  **Theme Manager** — browse, apply, remove, import, and export color schemes
-  **Quick Theme** — write themes in a simple CSS-like syntax and preview them live
-  **Background Support** — set PNG/JPG/GIF backgrounds with opacity, blur, stretch, alignment, and acrylic controls
-  **Auto Backup** — every save creates a timestamped backup; restore any previous state in one click
-  **Live Preview** — see exactly how your theme looks before applying it

---

## Screenshots

> *Add screenshots here.*

---

## Requirements

- Python **3.11+**
- Windows **10 or 11**
- [Windows Terminal](https://aka.ms/terminal) installed

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/T3RMIN4L.git
cd T3RMIN4L

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

> **Note:** If you get a `not writeable` pip warning, use `pip install --user -r requirements.txt`

---

## Project Structure

```
T3RMIN4L/
├── main.py          — Entry point
├── ui.py            — Full UI (customtkinter)
├── themes.py        — settings.json reader/writer, scheme CRUD
├── quicktheme.py    — CSS-like theme parser and validator
├── background.py    — Background image handling
├── backup.py        — Timestamped backup and restore
├── requirements.txt
├── README.md
└── themes/          — Drop .json scheme files here to import
```

---

## Quick Theme Syntax

T3RMIN4L includes a built-in theme editor with a simple, readable syntax:

```
background: #0a0a0f;
foreground: #e8e8f0;
cursor: #00ffcc;
selection: #2a2a4a;

black:   #000000;    red:    #ff5555;
green:   #50fa7b;    yellow: #f1fa8c;
blue:    #6272a4;    purple: #bd93f9;
cyan:    #8be9fd;    white:  #f8f8f2;

font: Cascadia Code;
opacity: 85;
```

Type it in the Quick Theme panel, hit **Preview** to see it live, then **Save Theme** to add it to your library.

**Supported keys:** `background`, `foreground`, `cursor`, `selection`, all 16 ANSI colors (`black` → `white`, `brightBlack` → `brightWhite`), `font`, `opacity`.

---

## Background Images

| Format | Support |
|--------|---------|
| PNG | Full support |
| JPG / JPEG |  Full support |
| GIF | Animations not supported by Windows Terminal — T3RMIN4L extracts the first frame automatically |

Controls available: **opacity**, **blur**, **stretch mode**, **alignment**, **acrylic effect**.

---

## Backups

Every time you apply or save a change, T3RMIN4L backs up your `settings.json` automatically.

- Up to **10 backups** are kept (oldest pruned automatically)
- Restore any backup from the **Backups panel** in one click
- Backup location: `%LOCALAPPDATA%\...\LocalState\t3rminal_backups\`

---

## settings.json — Auto-detected Locations

| Edition | Path |
|---------|------|
| Stable | `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json` |
| Preview | `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json` |
| Unpackaged | `%LOCALAPPDATA%\Microsoft\Windows Terminal\settings.json` |

T3RMIN4L checks all three locations and uses whichever exists.

---

## Built-in Themes

| Name | Style |
|------|-------|
| T3RMIN4L Dark | Deep navy, cyan accents |
| Cyber Neon | Pure black, electric magenta/green |
| Midnight Frost | GitHub Dark-inspired, blue tones |
| Amber Terminal | Retro amber monochrome |

Built-in themes cannot be removed. Custom themes can be deleted, exported, or edited at any time.

---

## Importing Community Themes

1. Download any `.json` Windows Terminal color scheme (from [windowsterminalthemes.dev](https://windowsterminalthemes.dev))
2. Click **↑ Import** in the sidebar, or drop the file into the `themes/` folder
3. The theme appears in your list immediately

---

## Notes

- Changes take effect after **restarting Windows Terminal**
- T3RMIN4L only writes to `profiles.defaults` and `schemes` — your profiles list is never touched
- Tested on Windows 11 with Windows Terminal 1.19+

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `customtkinter` | Modern dark UI framework |
| `Pillow` | Image validation and GIF frame extraction |

---

## License

MIT — do whatever you want with it.
