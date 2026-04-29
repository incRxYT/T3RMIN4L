"""themes.py — Windows Terminal settings.json reader/writer for T3RMIN4L."""

import json
import os
from pathlib import Path
from typing import Optional

import backup


# ── Locate settings.json ────────────────────────────────────────────────────

def find_settings_path() -> Optional[Path]:
    """Return the first existing Windows Terminal settings.json path."""
    local_app = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        # Stable
        Path(local_app) / "Packages" / "Microsoft.WindowsTerminal_8wekyb3d8bbwe" / "LocalState" / "settings.json",
        # Preview
        Path(local_app) / "Packages" / "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe" / "LocalState" / "settings.json",
        # Unpackaged
        Path(local_app) / "Microsoft" / "Windows Terminal" / "settings.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


# ── Read / Write helpers ─────────────────────────────────────────────────────

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


# ── Color Schemes ────────────────────────────────────────────────────────────

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


# ── Apply Theme to Profile ───────────────────────────────────────────────────

def apply_scheme_to_default_profile(settings: dict, scheme_name: str,
                                     profile_overrides: Optional[dict] = None) -> dict:
    """Set colorScheme on the default profile and optionally font/opacity."""
    profiles = settings.setdefault("profiles", {})
    defaults = profiles.setdefault("defaults", {})
    defaults["colorScheme"] = scheme_name
    if profile_overrides:
        if "font" in profile_overrides:
            defaults.setdefault("font", {}).update(profile_overrides["font"])
        if "opacity" in profile_overrides:
            defaults["opacity"] = profile_overrides["opacity"]
    return settings


# ── Background ───────────────────────────────────────────────────────────────

def apply_background(settings: dict, image_path: str,
                     opacity: float = 0.5,
                     stretch: str = "uniformToFill",
                     alignment: str = "center",
                     blur: bool = False,
                     acrylic: bool = False) -> dict:
    """Apply background image settings to the default profile."""
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


# ── Export ───────────────────────────────────────────────────────────────────

def export_scheme(scheme: dict, dest_path: Path) -> bool:
    try:
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(scheme, f, indent=4)
        return True
    except Exception:
        return False


def import_scheme_file(src_path: Path) -> Optional[dict]:
    try:
        with open(src_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        if isinstance(data, dict) and "name" in data:
            return data
        return None
    except Exception:
        return None


# ── Built-in bundled themes ──────────────────────────────────────────────────

BUNDLED_THEMES = [
    {
        "name": "T3RMIN4L Dark",
        "background": "#0a0a0f",
        "foreground": "#e8e8f0",
        "cursorColor": "#00ffcc",
        "selectionBackground": "#2a2a4a",
        "black": "#000000", "red": "#ff5555", "green": "#50fa7b",
        "yellow": "#f1fa8c", "blue": "#6272a4", "purple": "#bd93f9",
        "cyan": "#8be9fd", "white": "#f8f8f2",
        "brightBlack": "#44475a", "brightRed": "#ff6e6e", "brightGreen": "#69ff94",
        "brightYellow": "#ffffa5", "brightBlue": "#d6acff", "brightPurple": "#ff92df",
        "brightCyan": "#a4ffff", "brightWhite": "#ffffff",
    },
    {
        "name": "Cyber Neon",
        "background": "#05050d",
        "foreground": "#d0d0ff",
        "cursorColor": "#ff00ff",
        "selectionBackground": "#1a0033",
        "black": "#000000", "red": "#ff2244", "green": "#00ff88",
        "yellow": "#ffee00", "blue": "#3388ff", "purple": "#cc44ff",
        "cyan": "#00ccff", "white": "#ccccee",
        "brightBlack": "#333344", "brightRed": "#ff4466", "brightGreen": "#22ffaa",
        "brightYellow": "#ffff44", "brightBlue": "#55aaff", "brightPurple": "#dd66ff",
        "brightCyan": "#22ddff", "brightWhite": "#eeeeff",
    },
    {
        "name": "Midnight Frost",
        "background": "#0d1117",
        "foreground": "#c9d1d9",
        "cursorColor": "#58a6ff",
        "selectionBackground": "#1f3558",
        "black": "#0d1117", "red": "#ff7b72", "green": "#3fb950",
        "yellow": "#d29922", "blue": "#58a6ff", "purple": "#bc8cff",
        "cyan": "#39c5cf", "white": "#b1bac4",
        "brightBlack": "#484f58", "brightRed": "#ffa198", "brightGreen": "#56d364",
        "brightYellow": "#e3b341", "brightBlue": "#79c0ff", "brightPurple": "#d2a8ff",
        "brightCyan": "#56d4dd", "brightWhite": "#f0f6fc",
    },
    {
        "name": "Amber Terminal",
        "background": "#0c0800",
        "foreground": "#ffb000",
        "cursorColor": "#ffdd00",
        "selectionBackground": "#2a1a00",
        "black": "#000000", "red": "#cc4400", "green": "#88aa00",
        "yellow": "#ffaa00", "blue": "#aa6600", "purple": "#cc7700",
        "cyan": "#aa8800", "white": "#ddaa00",
        "brightBlack": "#443300", "brightRed": "#ff6600", "brightGreen": "#aadd00",
        "brightYellow": "#ffcc00", "brightBlue": "#cc8800", "brightPurple": "#ffaa00",
        "brightCyan": "#ddbb00", "brightWhite": "#ffee00",
    },
]
