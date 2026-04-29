"""settings.py — Persistent app state for T3RMIN4L v2.
Stores: last theme, window size, recent background, and custom theme registry.
PyInstaller-safe: all paths resolve relative to the executable or script location.
"""

import json
import sys
from pathlib import Path


def _app_dir() -> Path:
    """Return the directory containing the executable or main script.
    Works correctly whether running as 'python main.py' or a PyInstaller .exe.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller bundles everything; executable lives here
        return Path(sys.executable).parent
    return Path(__file__).parent


def _state_path() -> Path:
    return _app_dir() / "t3rminal_state.json"


def _themes_dir() -> Path:
    d = _app_dir() / "themes"
    d.mkdir(exist_ok=True)
    return d


# ── Public API ────────────────────────────────────────────────────────────────

def load() -> dict:
    """Load persisted app state. Returns defaults if file missing or corrupt."""
    defaults = {
        "last_theme":       None,
        "window_geometry":  "1100x700",
        "recent_bg":        None,
        "custom_themes":    [],   # list of filenames inside themes/
    }
    path = _state_path()
    if not path.exists():
        return defaults
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults so new keys are always present
        return {**defaults, **data}
    except Exception:
        return defaults


def save(state: dict) -> bool:
    try:
        with open(_state_path(), "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return True
    except Exception:
        return False


# ── Custom theme persistence ──────────────────────────────────────────────────

def themes_dir() -> Path:
    return _themes_dir()


def _safe_filename(name: str) -> str:
    """Convert theme name to a safe filename."""
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip()
    return (safe or "theme") + ".json"


def save_custom_theme(scheme: dict) -> bool:
    """Write a custom theme JSON to themes/. Overwrites if same name exists."""
    try:
        dest = _themes_dir() / _safe_filename(scheme.get("name", "theme"))
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(scheme, f, indent=4)
        return True
    except Exception:
        return False


def delete_custom_theme(name: str) -> bool:
    """Delete a custom theme file by theme name."""
    try:
        path = _themes_dir() / _safe_filename(name)
        if path.exists():
            path.unlink()
        return True
    except Exception:
        return False


def load_all_custom_themes() -> list[dict]:
    """Load every valid .json scheme from the themes/ folder."""
    result = []
    seen_names: set[str] = set()
    for f in sorted(_themes_dir().glob("*.json")):
        try:
            with open(f, "r", encoding="utf-8-sig") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and "name" in data:
                name = data["name"]
                if name not in seen_names:
                    seen_names.add(name)
                    result.append(data)
        except Exception:
            continue
    return result


def rename_custom_theme(old_name: str, new_name: str, scheme: dict) -> bool:
    """Rename a custom theme: delete old file, write new one."""
    delete_custom_theme(old_name)
    scheme["name"] = new_name
    return save_custom_theme(scheme)
