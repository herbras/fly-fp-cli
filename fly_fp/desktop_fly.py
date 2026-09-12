"""DesktopFly is the embodied connectome we point people at.

Not vendored here. Upstream:
  https://github.com/DenisSergeevitch/desktop-fly

FlyWire brain + MaleCNS v1.0 locomotor extract (~1045 neurons).
No token. Not fly.ai.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

UPSTREAM = "https://github.com/DenisSergeevitch/desktop-fly"
DEFAULT_CLONE = Path(os.environ.get("DESKTOP_FLY_HOME", Path.home() / "src" / "desktop-fly"))


def status(root: Path | None = None) -> dict:
    root = root or DEFAULT_CLONE
    build = root / "build.sh"
    app = root / "DesktopFly"
    win = root / "windows" / "package.json"
    return {
        "upstream": UPSTREAM,
        "clone": str(root),
        "cloned": (root / ".git").is_dir() or build.is_file() or win.is_file(),
        "macos_build_script": build.is_file(),
        "macos_binary": app.is_file() or (root / "DesktopFly.app").exists(),
        "windows_port": win.is_file(),
        "git_on_path": shutil.which("git") is not None,
        "note": "clone + ./build.sh on macOS 13+, or windows/ npm start. Desktop pet, not an fp subprocess.",
    }


def print_howto() -> None:
    print(f"upstream  {UPSTREAM}")
    print()
    print("macOS 13+:")
    print(f"  git clone {UPSTREAM} ~/src/desktop-fly")
    print("  cd ~/src/desktop-fly && ./build.sh && ./DesktopFly")
    print()
    print("Windows 10/11:")
    print("  cd desktop-fly/windows && npm install && npm start")
    print()
    print("Data: FlyWire (female brain) + MaleCNS locomotor extract.")
    print("fly-fp stays a separate allowlisted CLI. The fly does not exec fp.")
