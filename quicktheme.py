"""quicktheme.py — CSS-like theme syntax parser and validator for T3RMIN4L."""

import re

# Keys accepted in Quick Theme syntax and their WT JSON mapping
COLOR_KEYS = {
    "background", "foreground", "cursor", "cursorColor",
    "selectionBackground", "selection",
    "black", "red", "green", "yellow", "blue", "purple", "cyan", "white",
    "brightBlack", "brightRed", "brightGreen", "brightYellow",
    "brightBlue", "brightPurple", "brightCyan", "brightWhite",
}

# Aliases → canonical WT field names
ALIASES = {
    "cursor":     "cursorColor",
    "selection":  "selectionBackground",
}

NON_COLOR_KEYS = {"font", "opacity"}

HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def _normalize_hex(value: str) -> str:
    """Expand 3-digit hex to 6-digit."""
    v = value.strip()
    if HEX_RE.match(v):
        if len(v) == 4:  # #rgb
            r, g, b = v[1], v[2], v[3]
            return f"#{r}{r}{g}{g}{b}{b}"
        return v
    return v


def parse_quick_theme(text: str) -> tuple[dict, list[str]]:
    """
    Parse CSS-like Quick Theme syntax into a dict of validated fields.
    Returns (parsed_dict, error_list). errors is empty on full success.
    """
    parsed = {}
    errors = []

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("//") or line.startswith("#!"):
            continue
        if ":" not in line:
            errors.append(f"Line {lineno}: missing ':' — {raw!r}")
            continue

        key_raw, _, val_raw = line.partition(":")
        key = key_raw.strip().rstrip(";").strip()
        val = val_raw.strip().rstrip(";").strip()

        if not key or not val:
            errors.append(f"Line {lineno}: empty key or value — {raw!r}")
            continue

        # Resolve alias
        canonical = ALIASES.get(key, key)

        if canonical in COLOR_KEYS:
            norm = _normalize_hex(val)
            if not HEX_RE.match(norm):
                errors.append(f"Line {lineno}: '{key}' expects a hex color, got {val!r}")
                continue
            parsed[canonical] = norm

        elif key == "font":
            parsed["font"] = val

        elif key == "opacity":
            try:
                op = int(val)
                if not 0 <= op <= 100:
                    raise ValueError
                parsed["opacity"] = op
            except ValueError:
                errors.append(f"Line {lineno}: 'opacity' must be 0–100, got {val!r}")

        else:
            errors.append(f"Line {lineno}: unknown key '{key}'")

    return parsed, errors


def to_wt_scheme(name: str, parsed: dict) -> dict:
    """Convert parsed Quick Theme dict to a Windows Terminal color scheme JSON object."""
    scheme = {"name": name}

    color_map = {
        "black":        "black",
        "red":          "red",
        "green":        "green",
        "yellow":       "yellow",
        "blue":         "blue",
        "purple":       "purple",
        "cyan":         "cyan",
        "white":        "white",
        "brightBlack":  "brightBlack",
        "brightRed":    "brightRed",
        "brightGreen":  "brightGreen",
        "brightYellow": "brightYellow",
        "brightBlue":   "brightBlue",
        "brightPurple": "brightPurple",
        "brightCyan":   "brightCyan",
        "brightWhite":  "brightWhite",
        "background":       "background",
        "foreground":       "foreground",
        "cursorColor":      "cursorColor",
        "selectionBackground": "selectionBackground",
    }

    for key, wt_key in color_map.items():
        if key in parsed:
            scheme[wt_key] = parsed[key]

    return scheme


def quick_theme_to_profile_overrides(parsed: dict) -> dict:
    """Return profile-level overrides (font, opacity) from a parsed theme."""
    overrides = {}
    if "font" in parsed:
        overrides["font"] = {"face": parsed["font"]}
    if "opacity" in parsed:
        overrides["opacity"] = parsed["opacity"]
    return overrides


EXAMPLE_THEME = """\
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
brightBlack: #44475a;
brightRed: #ff6e6e;
brightGreen: #69ff94;
brightYellow: #ffffa5;
brightBlue: #d6acff;
brightPurple: #ff92df;
brightCyan: #a4ffff;
brightWhite: #ffffff;
font: Cascadia Code;
opacity: 85;\
"""
