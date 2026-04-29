"""themes.py — Windows Terminal settings.json reader/writer for T3RMIN4L v2."""

import json
import os
import re
from pathlib import Path
from typing import Optional

import backup

HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
REQUIRED_COLOR_KEYS = {"background", "foreground"}


# ── Locate settings.json ─────────────────────────────────────────────────────

def find_settings_path() -> Optional[Path]:
    local_app = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        Path(local_app) / "Packages" / "Microsoft.WindowsTerminal_8wekyb3d8bbwe" / "LocalState" / "settings.json",
        Path(local_app) / "Packages" / "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe" / "LocalState" / "settings.json",
        Path(local_app) / "Microsoft" / "Windows Terminal" / "settings.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


# ── Read / Write ─────────────────────────────────────────────────────────────

def load_settings(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_settings(path: Path, settings: dict, make_backup: bool = True) -> bool:
    try:
        if make_backup:
            backup.create_backup(path)
            backup.delete_old_backups(path, keep=10)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception:
        return False


# ── Validation ────────────────────────────────────────────────────────────────

def validate_scheme(scheme: dict) -> list[str]:
    """Return list of validation errors. Empty = valid."""
    errors = []
    if "name" not in scheme or not scheme["name"].strip():
        errors.append("Missing or empty 'name' field.")
    for key, val in scheme.items():
        if key == "name":
            continue
        if isinstance(val, str) and val.startswith("#"):
            if not HEX_RE.match(val):
                errors.append(f"Invalid hex color for '{key}': {val!r}")
    for key in REQUIRED_COLOR_KEYS:
        if key not in scheme:
            errors.append(f"Missing required field: '{key}'")
    return errors


# ── Scheme CRUD ───────────────────────────────────────────────────────────────

def list_schemes(settings: dict) -> list[dict]:
    return settings.get("schemes", [])


def get_scheme_by_name(settings: dict, name: str) -> Optional[dict]:
    for s in list_schemes(settings):
        if s.get("name") == name:
            return s
    return None


def add_or_update_scheme(settings: dict, scheme: dict) -> dict:
    schemes = settings.setdefault("schemes", [])
    for i, s in enumerate(schemes):
        if s.get("name") == scheme["name"]:
            schemes[i] = scheme
            return settings
    schemes.append(scheme)
    return settings


def remove_scheme(settings: dict, name: str) -> dict:
    settings["schemes"] = [s for s in settings.get("schemes", []) if s.get("name") != name]
    return settings


def duplicate_scheme(settings: dict, name: str) -> Optional[dict]:
    """Clone a scheme with ' (Copy)' appended. Returns new scheme or None."""
    original = get_scheme_by_name(settings, name)
    if not original:
        return None
    copy = dict(original)
    base = name.removesuffix(" (Copy)")
    new_name = f"{base} (Copy)"
    # Avoid collision
    existing = {s.get("name") for s in list_schemes(settings)}
    n = 2
    candidate = new_name
    while candidate in existing:
        candidate = f"{base} (Copy {n})"
        n += 1
    copy["name"] = candidate
    add_or_update_scheme(settings, copy)
    return copy


def rename_scheme(settings: dict, old_name: str, new_name: str) -> bool:
    """Rename a scheme in settings. Returns True on success."""
    new_name = new_name.strip()
    if not new_name or new_name == old_name:
        return False
    existing = {s.get("name") for s in list_schemes(settings)}
    if new_name in existing:
        return False
    for s in settings.get("schemes", []):
        if s.get("name") == old_name:
            s["name"] = new_name
            return True
    return False


# ── Apply to profile ──────────────────────────────────────────────────────────

def apply_scheme_to_default_profile(settings: dict, scheme_name: str,
                                     profile_overrides: Optional[dict] = None) -> dict:
    defaults = settings.setdefault("profiles", {}).setdefault("defaults", {})
    defaults["colorScheme"] = scheme_name
    if profile_overrides:
        if "font" in profile_overrides:
            defaults.setdefault("font", {}).update(profile_overrides["font"])
        if "opacity" in profile_overrides:
            defaults["opacity"] = profile_overrides["opacity"]
    return settings


# ── Background ────────────────────────────────────────────────────────────────

def apply_background(settings: dict, image_path: str, opacity: float = 0.5,
                     stretch: str = "uniformToFill", alignment: str = "center",
                     blur: bool = False, acrylic: bool = False) -> dict:
    defaults = settings.setdefault("profiles", {}).setdefault("defaults", {})
    defaults["backgroundImage"] = image_path
    defaults["backgroundImageOpacity"] = max(0.0, min(1.0, opacity))
    defaults["backgroundImageStretchMode"] = stretch
    defaults["backgroundImageAlignment"] = alignment
    if blur:
        defaults["backgroundImageBlur"] = True
    else:
        defaults.pop("backgroundImageBlur", None)
    if acrylic:
        defaults["useAcrylic"] = True
        defaults["acrylicOpacity"] = max(0.0, min(1.0, opacity))
    else:
        defaults.pop("useAcrylic", None)
        defaults.pop("acrylicOpacity", None)
    return settings


def remove_background(settings: dict) -> dict:
    defaults = settings.setdefault("profiles", {}).setdefault("defaults", {})
    for key in ("backgroundImage", "backgroundImageOpacity", "backgroundImageStretchMode",
                "backgroundImageAlignment", "backgroundImageBlur"):
        defaults.pop(key, None)
    return settings


# ── Import / Export ───────────────────────────────────────────────────────────

def export_scheme(scheme: dict, dest_path: Path) -> bool:
    try:
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(scheme, f, indent=4)
        return True
    except Exception:
        return False


def import_scheme_file(src_path: Path) -> tuple[Optional[dict], list[str]]:
    """Returns (scheme, errors). errors is empty on success."""
    try:
        with open(src_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "name" not in data:
            return None, ["File does not contain a valid color scheme (missing 'name')."]
        errors = validate_scheme(data)
        if errors:
            return None, errors
        return data, []
    except json.JSONDecodeError as e:
        return None, [f"JSON parse error: {e}"]
    except Exception as e:
        return None, [str(e)]


# ── Built-in themes ───────────────────────────────────────────────────────────

BUNDLED_THEMES = [
    {
        "name": "T3RMIN4L Dark",
        "background": "#0a0a0f", "foreground": "#e8e8f0",
        "cursorColor": "#00ffcc", "selectionBackground": "#2a2a4a",
        "black": "#000000", "red": "#ff5555", "green": "#50fa7b",
        "yellow": "#f1fa8c", "blue": "#6272a4", "purple": "#bd93f9",
        "cyan": "#8be9fd", "white": "#f8f8f2",
        "brightBlack": "#44475a", "brightRed": "#ff6e6e", "brightGreen": "#69ff94",
        "brightYellow": "#ffffa5", "brightBlue": "#d6acff", "brightPurple": "#ff92df",
        "brightCyan": "#a4ffff", "brightWhite": "#ffffff",
    },
    {
        "name": "Cyber Neon",
        "background": "#05050d", "foreground": "#d0d0ff",
        "cursorColor": "#ff00ff", "selectionBackground": "#1a0033",
        "black": "#000000", "red": "#ff2244", "green": "#00ff88",
        "yellow": "#ffee00", "blue": "#3388ff", "purple": "#cc44ff",
        "cyan": "#00ccff", "white": "#ccccee",
        "brightBlack": "#333344", "brightRed": "#ff4466", "brightGreen": "#22ffaa",
        "brightYellow": "#ffff44", "brightBlue": "#55aaff", "brightPurple": "#dd66ff",
        "brightCyan": "#22ddff", "brightWhite": "#eeeeff",
    },
    {
        "name": "Midnight Frost",
        "background": "#0d1117", "foreground": "#c9d1d9",
        "cursorColor": "#58a6ff", "selectionBackground": "#1f3558",
        "black": "#0d1117", "red": "#ff7b72", "green": "#3fb950",
        "yellow": "#d29922", "blue": "#58a6ff", "purple": "#bc8cff",
        "cyan": "#39c5cf", "white": "#b1bac4",
        "brightBlack": "#484f58", "brightRed": "#ffa198", "brightGreen": "#56d364",
        "brightYellow": "#e3b341", "brightBlue": "#79c0ff", "brightPurple": "#d2a8ff",
        "brightCyan": "#56d4dd", "brightWhite": "#f0f6fc",
    },
    {
        "name": "Amber Terminal",
        "background": "#0c0800", "foreground": "#ffb000",
        "cursorColor": "#ffdd00", "selectionBackground": "#2a1a00",
        "black": "#000000", "red": "#cc4400", "green": "#88aa00",
        "yellow": "#ffaa00", "blue": "#aa6600", "purple": "#cc7700",
        "cyan": "#aa8800", "white": "#ddaa00",
        "brightBlack": "#443300", "brightRed": "#ff6600", "brightGreen": "#aadd00",
        "brightYellow": "#ffcc00", "brightBlue": "#cc8800", "brightPurple": "#ffaa00",
        "brightCyan": "#ddbb00", "brightWhite": "#ffee00",
    },
    {
        "name": "Crimson Void",
        "background": "#0d0007", "foreground": "#f8c8d0",
        "cursorColor": "#ff2255", "selectionBackground": "#3a0015",
        "black": "#0d0007", "red": "#ff2255", "green": "#aa3344",
        "yellow": "#ff6677", "blue": "#882233", "purple": "#cc1144",
        "cyan": "#dd4466", "white": "#f8c8d0",
        "brightBlack": "#440011", "brightRed": "#ff5577", "brightGreen": "#cc4455",
        "brightYellow": "#ff8899", "brightBlue": "#aa3344", "brightPurple": "#ee2255",
        "brightCyan": "#ff6688", "brightWhite": "#ffffff",
    },
    {
        "name": "Arctic Pulse",
        "background": "#050d12", "foreground": "#cceeff",
        "cursorColor": "#00ddff", "selectionBackground": "#0a2233",
        "black": "#050d12", "red": "#ff6b6b", "green": "#00e5cc",
        "yellow": "#ffe066", "blue": "#00aaff", "purple": "#9988ff",
        "cyan": "#00ddff", "white": "#cceeff",
        "brightBlack": "#1a3344", "brightRed": "#ff9999", "brightGreen": "#33ffee",
        "brightYellow": "#ffee99", "brightBlue": "#44ccff", "brightPurple": "#bbaaff",
        "brightCyan": "#66eeff", "brightWhite": "#eeffff",
    },
    {
        "name": "Matrix Green",
        "background": "#000d00", "foreground": "#00ff41",
        "cursorColor": "#00ff41", "selectionBackground": "#003300",
        "black": "#000d00", "red": "#007700", "green": "#00ff41",
        "yellow": "#00cc33", "blue": "#005500", "purple": "#009922",
        "cyan": "#00dd33", "white": "#00ff41",
        "brightBlack": "#003300", "brightRed": "#00aa00", "brightGreen": "#33ff66",
        "brightYellow": "#00ff66", "brightBlue": "#007700", "brightPurple": "#00cc44",
        "brightCyan": "#00ff55", "brightWhite": "#ccffcc",
    },
    {
        "name": "Violet Core",
        "background": "#080010", "foreground": "#ddc8ff",
        "cursorColor": "#cc88ff", "selectionBackground": "#220044",
        "black": "#080010", "red": "#ff44aa", "green": "#aa44ff",
        "yellow": "#dd88ff", "blue": "#7722ff", "purple": "#cc44ff",
        "cyan": "#aa66ff", "white": "#ddc8ff",
        "brightBlack": "#331155", "brightRed": "#ff66bb", "brightGreen": "#cc66ff",
        "brightYellow": "#eeb8ff", "brightBlue": "#9955ff", "brightPurple": "#dd66ff",
        "brightCyan": "#cc99ff", "brightWhite": "#ffffff",
    },
    {
        "name": "Obsidian Glass",
        "background": "#0a0a0a", "foreground": "#d4d4d4",
        "cursorColor": "#ffffff", "selectionBackground": "#264f78",
        "black": "#0a0a0a", "red": "#f44747", "green": "#4ec994",
        "yellow": "#ce9178", "blue": "#569cd6", "purple": "#c586c0",
        "cyan": "#4fc1ff", "white": "#d4d4d4",
        "brightBlack": "#555555", "brightRed": "#f44747", "brightGreen": "#4ec994",
        "brightYellow": "#dcdcaa", "brightBlue": "#9cdcfe", "brightPurple": "#c586c0",
        "brightCyan": "#4fc1ff", "brightWhite": "#ffffff",
    },
    {
        "name": "Retro DOS",
        "background": "#000080", "foreground": "#aaaaaa",
        "cursorColor": "#aaaaaa", "selectionBackground": "#0000aa",
        "black": "#000000", "red": "#aa0000", "green": "#00aa00",
        "yellow": "#aa5500", "blue": "#0000aa", "purple": "#aa00aa",
        "cyan": "#00aaaa", "white": "#aaaaaa",
        "brightBlack": "#555555", "brightRed": "#ff5555", "brightGreen": "#55ff55",
        "brightYellow": "#ffff55", "brightBlue": "#5555ff", "brightPurple": "#ff55ff",
        "brightCyan": "#55ffff", "brightWhite": "#ffffff",
    },
]

BUNDLED_NAMES = {t["name"] for t in BUNDLED_THEMES}
