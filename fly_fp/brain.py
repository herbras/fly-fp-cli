"""Brain factory.

stub     = 64 random LIF units (NOT the fly).
malecns  = FlyBrain on MaleCNS v1.0 weights.npz (the actual wiring).
"""

from __future__ import annotations

import math
import random
from typing import Protocol


class BrainLike(Protocol):
    def step(self, sensory: list[float]) -> list[float]: ...
    def reset(self) -> None: ...


class ReservoirBrain:
    """64 leaky units. Use only when MaleCNS weights are not on disk."""

    def __init__(self, n: int = 64, seed: int = 7, dt_tau: float = 0.2):
        rng = random.Random(seed)
        self.n = n
        self.decay = math.exp(-dt_tau)
        self.v = [0.0] * n
        self.w = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for _ in range(6):
                j = rng.randrange(n)
                sign = -1.0 if rng.random() < 0.3 else 1.0
                self.w[i][j] += sign * (0.15 + 0.35 * rng.random())
        for i in range(n):
            s = sum(abs(x) for x in self.w[i]) or 1.0
            self.w[i] = [x / s for x in self.w[i]]
        self.gain = 1.6
        self.tonic = 0.12
        self.noise = 0.03
        self._rng = rng

    def reset(self) -> None:
        self.v = [0.0] * self.n

    def step(self, sensory: list[float]) -> list[float]:
        spikes = [1.0 if v >= 1.0 else 0.0 for v in self.v]
        new_v = []
        for i in range(self.n):
            rec = sum(self.w[i][j] * spikes[j] for j in range(self.n))
            inj = sensory[i] if i < len(sensory) else 0.0
            noise = (self._rng.random() - 0.5) * 2 * self.noise
            v = self.decay * (0.0 if spikes[i] else self.v[i])
            v = v + self.gain * rec + self.tonic + noise + inj
            new_v.append(v)
        self.v = new_v
        return [1.0 if v >= 1.0 else 0.0 for v in self.v]

    def rollout(self, sensory: list[float], steps: int = 12) -> list[float]:
        acc = [0.0] * self.n
        for _ in range(steps):
            spk = self.step(sensory)
            for i, s in enumerate(spk):
                acc[i] += s
        return [x / steps for x in acc]


def make_brain(kind: str = "stub"):
    if kind in ("stub", "reservoir"):
        return ReservoirBrain()
    if kind in ("flyai", "malecns", "male-cns"):
        from fly_fp.malecns import MaleCNSBrain
        return MaleCNSBrain()
    raise ValueError(f"unknown brain kind: {kind}")
