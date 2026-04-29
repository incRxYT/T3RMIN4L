"""main.py — T3RMIN4L v2 entry point. PyInstaller-compatible."""

import sys
import os
from pathlib import Path


def _ensure_themes_dir():
    """Create themes/ next to executable/script if it doesn't exist."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    (base / "themes").mkdir(exist_ok=True)


def main():
    try:
        import customtkinter  # noqa: F401
    except ImportError:
        print("customtkinter is not installed.\nRun:  pip install -r requirements.txt")
        sys.exit(1)

    _ensure_themes_dir()

    from ui import T3RMINAL
    app = T3RMINAL()
    app.mainloop()


if __name__ == "__main__":
    main()
