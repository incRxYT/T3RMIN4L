# T3RMIN4L

> Lightweight Windows Terminal theme manager.

```
T3RMIN4L/
├── main.py          — Entry point
├── ui.py            — Full UI (customtkinter)
├── themes.py        — settings.json read/write, scheme management
├── quicktheme.py    — CSS-like theme parser and validator
├── background.py    — Background image handling (PNG/JPG/GIF)
├── backup.py        — Settings backup and restore
├── requirements.txt
├── README.md
└── themes/          — Drop .json theme files here to auto-import
```

---

## Requirements

- Python 3.11+
- Windows 10 / 11
- Windows Terminal installed

---

## Install

```bash
pip install -r requirements.txt
python main.py
```

---

## Quick Theme Syntax

Create themes with a simple CSS-like syntax:

```
background: #0a0a0f;
foreground: #e8e8f0;
cursor: #00ffcc;
selection: #2a2a4a;
black: #000000;
red: #ff5555;
green: #50fa7b;
yellow: #f1fa8c;
blue: #6272a4;
purple: #bd93f9;
cyan: #8be9fd;
white: #f8f8f2;
font: Cascadia Code;
opacity: 85;
```

**Supported keys:** all 16 ANSI colors, `brightBlack` through `brightWhite`, `background`, `foreground`, `cursor` (alias for `cursorColor`), `selection` (alias for `selectionBackground`), `font`, `opacity`.

---

## Background Images

- **PNG / JPG** — fully supported, applied directly.
- **GIF** — Windows Terminal does not render animations. T3RMIN4L automatically extracts the first frame and uses it as a static PNG. A warning is shown in the UI.

Background controls: opacity, stretch mode, alignment, blur, acrylic effect.

---

## Theme Import / Export

- **Import** — load any `.json` Windows Terminal color scheme file.
- **Export** — save the selected scheme to a `.json` file.
- Drop `.json` files into the `themes/` folder for manual import via the Import button.

---

## Backups

T3RMIN4L creates a timestamped backup of `settings.json` before every save.  
Up to 10 backups are kept. Restore any backup from the Backups panel.

Backup location: `%LOCALAPPDATA%\Packages\...\LocalState\t3rminal_backups\`

---

## settings.json Location (auto-detected)

| Edition | Path |
|---|---|
| Stable | `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json` |
| Preview | `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json` |
| Unpackaged | `%LOCALAPPDATA%\Microsoft\Windows Terminal\settings.json` |

---

## Notes

- Changes take effect after restarting Windows Terminal.
- T3RMIN4L never modifies your profiles list — it only writes to `profiles.defaults` and `schemes`.
- Built-in themes (T3RMIN4L Dark, Cyber Neon, Midnight Frost, Amber Terminal) cannot be removed.
