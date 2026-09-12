"""Type allowlisted fp commands one key at a time."""

from __future__ import annotations

from dataclasses import dataclass

from fly_fp.allowlist import Action, is_forbidden
from fly_fp.encoder import TerminalObs, encode
from fly_fp.keyboard import (
    KeyboardState,
    apply_key,
    command_target,
    next_key_for_target,
    sense_keyboard,
)


@dataclass
class TypeTick:
    key: str
    buffer: str
    sense: dict[str, float]
    meaning: str
    spikes: list[float]


def meaning_of(state: KeyboardState) -> str:
    if is_forbidden(state.buffer):
        return "BAHAYA: buffer menyerupai install/pipe. Jangan enter."
    if state.matched_action:
        return f"perintah lengkap: {state.matched_action.value} → {state.buffer.strip()}"
    toks = state.tokens
    if not toks:
        return "buffer kosong. lalat di atas keyboard, belum ngetik."
    if "fp".startswith(toks[0]) and len(toks) == 1 and toks[0] != "fp":
        return f"ngetik binary: {toks[0]!r} → menuju 'fp'"
    if toks[0] != "fp":
        return f"bukan fp ({toks[0]!r}). allowlist menolak."
    known = {
        "skills": "modul skill Founder+",
        "guidance": "modul panduan",
        "catalog": "katalog produk",
        "products": "daftar produk akun",
        "new": "scaffold app",
        "list": "tampilkan daftar",
        "search": "cari skill",
        "install": "pasang skill ke ~/.claude/skills",
        "marketing": "kata kunci marketing",
        "mulai-jualan": "skill mulai-jualan",
        "tutorials": "daftar tutorial",
        "--help": "bantuan CLI",
        "--list": "daftar template",
    }
    bits = [known.get(t, f"token {t!r}") for t in toks]
    if state.prefix_ok:
        return "mengerti: " + " · ".join(bits) + " (masih ngetik)"
    return "prefix menyimpang dari allowlist: " + " ".join(toks)


class FlyTypist:
    def __init__(self, target_action: Action = Action.SKILLS_LIST, brain_kind: str = "stub"):
        from fly_fp.brain import make_brain
        self.brain = make_brain(brain_kind)
        self.state = KeyboardState(target=command_target(target_action))
        self.action = target_action

    def tick(self) -> TypeTick:
        kid = next_key_for_target(self.state)
        if not kid:
            kid = "enter" if self.state.buffer else ""
        if kid:
            apply_key(self.state, kid)
        sense = sense_keyboard(self.state)
        sensory = [
            sense["hand_x"], sense["hand_y"], sense["has_fp"], sense["prefix_ok"],
            sense["forbidden"], sense["done"], sense["progress"], sense["token_count"],
        ]
        obs = encode(TerminalObs(stdout=self.state.buffer))
        mixed = [(sensory[i] + obs[i]) * 0.5 for i in range(8)]
        spikes = self.brain.rollout(mixed, steps=8)
        return TypeTick(kid or "", self.state.buffer, sense, meaning_of(self.state), spikes)

    def type_all(self, max_keys: int = 80) -> list[TypeTick]:
        ticks = []
        for _ in range(max_keys):
            t = self.tick()
            ticks.append(t)
            if t.key == "enter" or t.sense["forbidden"] >= 1.0:
                break
        return ticks
