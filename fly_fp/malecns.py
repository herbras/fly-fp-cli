"""MaleCNS v1.0 — the actual wiring, not a toy reservoir.

Loads fly.ai build artifacts:
    $FLY_DATA/weights.npz
    $FLY_DATA/brain.npz

Source: Janelia / Cambridge / Google MaleCNS v1.0 (CC BY 4.0).
Simulator: alextitonis/fly.ai FlyBrain LIF (MIT).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

DATA = Path(os.environ.get("FLY_DATA", Path.home() / "fly-data"))

CHANNEL_TYPES = {
    0: [("Gr64f", None), ("Gr5a", None)],
    1: [("Gr66a", None), ("Gr33a", None)],
    2: [("LPLC2", "L"), ("LC4", "L")],
    3: [("LC10a", "L"), ("LC10", "L")],
    4: [("DNb01", None)],
    5: [("DNg100", None), ("DNa02", None)],
}
READOUT_TYPES = ["descending_neuron", "DNa02", "DNp01", "DNg100", "MDN"]


def data_ready(root: Path | None = None) -> bool:
    root = root or DATA
    return (root / "weights.npz").is_file() and (root / "brain.npz").is_file()


def status() -> dict:
    ready = data_ready()
    info = {
        "fly_data": str(DATA),
        "weights": str(DATA / "weights.npz"),
        "brain_npz": str(DATA / "brain.npz"),
        "ready": ready,
        "flyai_importable": False,
        "neurons": None,
        "note": "",
    }
    try:
        import fly_brain  # noqa: F401
        info["flyai_importable"] = True
    except ImportError:
        info["note"] = "fly.ai not on PYTHONPATH. Clone https://github.com/alextitonis/fly.ai"
    if ready:
        try:
            import numpy as np
            meta = np.load(DATA / "brain.npz", allow_pickle=True)
            info["neurons"] = int(len(meta["cell_type"]))
        except Exception as exc:
            info["note"] = f"brain.npz unreadable: {exc}"
    elif not info["note"]:
        info["note"] = "MaleCNS weights missing. Run: python -m fly_fp.cli fetch-brain"
    return info


def require_import() -> None:
    try:
        import fly_brain  # noqa: F401
    except ImportError:
        raise ImportError(
            "Cannot import fly_brain. Clone https://github.com/alextitonis/fly.ai "
            "set PYTHONPATH, run python build_brain.py"
        ) from None


class MaleCNSBrain:
    """166k LIF neurons, wiring frozen from MaleCNS v1.0."""

    def __init__(self, device: str = "auto"):
        require_import()
        from fly_brain import FlyBrain  # type: ignore
        self._fb = FlyBrain(device=device)
        self.n = int(getattr(self._fb, "n", 0))
        self._cache = {}

    def reset(self) -> None:
        if hasattr(self._fb, "reset"):
            self._fb.reset()

    def _idx(self, types, side):
        key = (tuple(types), side)
        if key in self._cache:
            return self._cache[key]
        idx = None
        for t in types:
            try:
                got = self._fb.cells([t], side=side)
            except Exception:
                continue
            if got is not None and getattr(got, "size", 0):
                idx = got
                break
        self._cache[key] = idx
        return idx

    def step(self, sensory: list[float]) -> list[float]:
        inject = []
        for ch, specs in CHANNEL_TYPES.items():
            if ch >= len(sensory) or sensory[ch] <= 0.02:
                continue
            for typ, side in specs:
                idx = self._idx([typ], side)
                if idx is None or getattr(idx, "size", 0) == 0:
                    continue
                inject.append((idx, float(sensory[ch])))
                break
        fired = self._fb.step(inject=inject or ())
        return self._readout(fired)

    def rollout(self, sensory: list[float], steps: int = 12) -> list[float]:
        acc = None
        for _ in range(max(steps, 1)):
            vec = self.step(sensory)
            if acc is None:
                acc = [0.0] * len(vec)
            for i, x in enumerate(vec):
                acc[i] += x
        n = max(steps, 1)
        return [x / n for x in acc] if acc else [0.0] * 64

    def _readout(self, fired) -> list[float]:
        vec = [0.0] * 64
        try:
            import numpy as np
        except ImportError:
            return vec
        fired_set = None
        if fired is not None:
            try:
                fired_set = set(int(i) for i in np.asarray(fired).ravel().tolist())
            except Exception:
                fired_set = None
        for i, typ in enumerate(READOUT_TYPES):
            idx = self._idx([typ], None)
            if idx is None or getattr(idx, "size", 0) == 0:
                continue
            ids = np.asarray(idx).ravel()
            if fired_set is not None and len(ids):
                hits = sum(1 for k in ids.tolist() if int(k) in fired_set)
                vec[i] = hits / max(len(ids), 1)
            elif hasattr(self._fb, "v"):
                try:
                    vec[i] = float(np.mean(self._fb.v[ids]))
                except Exception:
                    vec[i] = 0.0
        if fired_set is not None:
            vec[8] = min(len(fired_set) / 500.0, 1.0)
        return vec


def fetch_brain(dest: Path | None = None, flyai_dir: Path | None = None) -> int:
    dest = dest or Path.home() / "src" / "fly.ai"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not (dest / "build_brain.py").exists():
        print(f"cloning fly.ai → {dest}")
        rc = os.system(f"git clone --depth 1 https://github.com/alextitonis/fly.ai {dest}")
        if rc != 0:
            print("git clone failed", file=sys.stderr)
            return 1
    print("running build_brain.py (MaleCNS ~1.1 GB if raw missing)")
    rc = os.system(f"{sys.executable} {dest / 'build_brain.py'}")
    if rc != 0:
        print(f"build failed. pip install -r {dest / 'requirements.txt'}", file=sys.stderr)
        return 1
    print(f"PYTHONPATH={dest}")
    print(f"FLY_DATA={DATA}")
    print("ready" if data_ready() else "weights still missing")
    return 0 if data_ready() else 2
