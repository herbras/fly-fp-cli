"""Map terminal state to a small sensory vector.

Channels mimic fly pathways only as labels:
  0 sweet     — clean success / useful output
  1 bitter    — error / unknown command
  2 looming   — dangerous text (curl|sh, sudo, rm)
  3 target    — a list or menu is on screen
  4 rest      — empty prompt, idle
  5 hunger    — task not yet satisfied
  6 satiety   — current curriculum goal already hit
  7 noise     — unused reserved channel
"""

from __future__ import annotations

from dataclasses import dataclass, field


N_CHANNELS = 8


@dataclass
class TerminalObs:
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    goal_tokens: tuple[str, ...] = ()
    last_action: str = "idle"
    extra: dict = field(default_factory=dict)


def _clip(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def encode(obs: TerminalObs) -> list[float]:
    text = f"{obs.stdout}\n{obs.stderr}"
    low = text.lower()
    from fly_fp.allowlist import is_forbidden

    errorish = obs.exit_code not in (None, 0) or any(
        w in low
        for w in ("error", "not found", "command not found", "traceback", "denied")
    )
    useful = any(
        w in low
        for w in ("usage", "skill", "guidance", "tutorial", "catalog", "product", "template")
    )
    has_list = low.count("\n") >= 3 or "list" in low
    goal_hit = bool(obs.goal_tokens) and all(t.lower() in low for t in obs.goal_tokens)
    forbidden = is_forbidden(text)

    vec = [0.0] * N_CHANNELS
    vec[0] = _clip((0.7 if useful else 0.0) + (0.3 if obs.exit_code == 0 else 0.0))
    vec[1] = _clip(0.9 if errorish else 0.0)
    vec[2] = _clip(1.0 if forbidden else 0.0)
    vec[3] = _clip(0.8 if has_list else 0.2 if useful else 0.0)
    vec[4] = _clip(0.8 if not text.strip() else 0.1)
    vec[5] = _clip(0.0 if goal_hit else 0.85)
    vec[6] = _clip(1.0 if goal_hit else 0.0)
    vec[7] = 0.05
    if forbidden:
        vec[0] = 0.0
        vec[5] = 0.0
        vec[6] = 0.0
    return vec
