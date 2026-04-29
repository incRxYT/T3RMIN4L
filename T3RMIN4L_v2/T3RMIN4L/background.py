"""background.py — Background image handling for T3RMIN4L."""

from pathlib import Path
from typing import Optional
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

SUPPORTED_STATIC = {".png", ".jpg", ".jpeg"}
SUPPORTED_GIF    = {".gif"}
SUPPORTED_ALL    = SUPPORTED_STATIC | SUPPORTED_GIF

STRETCH_MODES = ["uniformToFill", "fill", "uniform", "none"]
ALIGNMENT_OPTIONS = [
    "center", "topLeft", "top", "topRight",
    "left", "right", "bottomLeft", "bottom", "bottomRight"
]


def is_supported(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_ALL


def is_gif(path: Path) -> bool:
    return path.suffix.lower() == ".gif"


def extract_gif_first_frame(gif_path: Path, out_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Extract the first frame of a GIF and save as PNG.
    Windows Terminal does not support animated GIFs; only the first frame will be used.
    Returns path to the extracted PNG, or None on failure.
    """
    if not PIL_AVAILABLE:
        return None
    try:
        out_dir = out_dir or gif_path.parent
        out_path = out_dir / (gif_path.stem + "_frame0.png")
        with Image.open(gif_path) as img:
            img.seek(0)
            frame = img.convert("RGBA")
            frame.save(out_path, "PNG")
        return out_path
    except Exception:
        return None


def validate_image(path: Path) -> tuple[bool, str]:
    """
    Validate that an image file is usable as a terminal background.
    Returns (valid, message).
    """
    if not path.exists():
        return False, "File does not exist."
    if path.suffix.lower() not in SUPPORTED_ALL:
        return False, f"Unsupported format '{path.suffix}'. Use PNG, JPG, or GIF."
    if not PIL_AVAILABLE:
        # Can't deep-validate without Pillow — allow it
        return True, "OK (Pillow not installed; basic validation only)"
    try:
        with Image.open(path) as img:
            img.verify()
        return True, "OK"
    except Exception as e:
        return False, f"Image error: {e}"


def get_image_info(path: Path) -> Optional[dict]:
    """Return basic image metadata dict, or None if unavailable."""
    if not PIL_AVAILABLE or not path.exists():
        return None
    try:
        with Image.open(path) as img:
            info = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "is_animated": getattr(img, "n_frames", 1) > 1,
                "frames": getattr(img, "n_frames", 1),
            }
        return info
    except Exception:
        return None


def build_background_config(image_path: Path,
                             opacity: float = 0.5,
                             stretch: str = "uniformToFill",
                             alignment: str = "center",
                             blur: bool = False,
                             acrylic: bool = False) -> dict:
    """
    Build the profile-level background config dict for Windows Terminal.
    If image is a GIF, transparently extracts first frame.
    Returns dict with 'config' and optional 'warning'.
    """
    warning = None
    actual_path = image_path

    if is_gif(image_path):
        extracted = extract_gif_first_frame(image_path)
        if extracted:
            actual_path = extracted
            warning = (
                "⚠  Windows Terminal does not support animated GIFs.\n"
                "   The first frame has been extracted and will be used as a static background."
            )
        else:
            warning = (
                "⚠  Windows Terminal does not support animated GIFs.\n"
                "   Could not extract first frame — install Pillow for GIF support."
            )

    config = {
        "backgroundImage": actual_path.as_posix(),
        "backgroundImageOpacity": round(max(0.0, min(1.0, opacity)), 2),
        "backgroundImageStretchMode": stretch if stretch in STRETCH_MODES else "uniformToFill",
        "backgroundImageAlignment": alignment if alignment in ALIGNMENT_OPTIONS else "center",
    }
    if blur:
        config["backgroundImageBlur"] = True
    if acrylic:
        config["useAcrylic"] = True
        config["acrylicOpacity"] = round(max(0.0, min(1.0, opacity)), 2)

    return {"config": config, "warning": warning}
