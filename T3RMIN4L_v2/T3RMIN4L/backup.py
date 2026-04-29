"""backup.py — Settings backup and restore for T3RMIN4L."""

import json
import shutil
from pathlib import Path
from datetime import datetime


def _backup_path(settings_path: Path) -> Path:
    return settings_path.parent / "t3rminal_backups"


def create_backup(settings_path: Path) -> Path | None:
    """Copy settings.json into a timestamped backup. Returns backup path or None."""
    if not settings_path.exists():
        return None
    bp = _backup_path(settings_path)
    bp.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = bp / f"settings_{stamp}.json"
    shutil.copy2(settings_path, dest)
    return dest


def list_backups(settings_path: Path) -> list[Path]:
    """Return list of backup files, newest first."""
    bp = _backup_path(settings_path)
    if not bp.exists():
        return []
    files = sorted(bp.glob("settings_*.json"), reverse=True)
    return files


def restore_backup(backup_file: Path, settings_path: Path) -> bool:
    """Overwrite settings.json with a chosen backup. Returns True on success."""
    try:
        shutil.copy2(backup_file, settings_path)
        return True
    except Exception:
        return False


def delete_old_backups(settings_path: Path, keep: int = 10) -> int:
    """Remove oldest backups beyond `keep` limit. Returns count deleted."""
    files = list_backups(settings_path)
    to_delete = files[keep:]
    for f in to_delete:
        f.unlink(missing_ok=True)
    return len(to_delete)


def backup_summary(settings_path: Path) -> list[dict]:
    """Return list of dicts with name, path, size, date for each backup."""
    result = []
    for f in list_backups(settings_path):
        stat = f.stat()
        result.append({
            "name": f.name,
            "path": f,
            "size_kb": round(stat.st_size / 1024, 1),
            "date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        })
    return result
