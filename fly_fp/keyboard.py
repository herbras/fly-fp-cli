"""QWERTY body for the fly.

The connectome does not contain letters. This module is the body:
each key is a spatial contact, the line buffer is what the fly sees
on the terminal, and token parse is how it knows whether the string
means an allowlisted fp command or garbage / danger.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from fly_fp.allowlist import ALLOWED_ACTIONS, Action, is_forbidden


ROWS = (
    list("1234567890-="),
    list("qwertyuiop"),
    list("asdfghjkl"),
    list("zxcvbnm"),
)

SPECIAL = ("space", "enter", "backspace", "quote", "dash")

KEY_ALIAS = {
    " ": "space",
    "\n": "enter",
    "-": "dash",
    "_": "dash",
    '"': "quote",
    "'": "quote",
}


def key_id(ch: str) -> str:
    if ch in KEY_ALIAS:
        return KEY_ALIAS[ch]
    return ch.lower()


def key_xy(kid: str) -> tuple[float, float]:
    if kid == "space":
        return 0.45, 0.92
    if kid == "enter":
        return 0.96, 0.55
    if kid == "backspace":
        return 0.96, 0.12
    if kid == "quote":
        return 0.88, 0.38
    if kid == "dash":
        return 0.90, 0.08
    for y, row in enumerate(ROWS):
        if kid in row:
            x = row.index(kid) / max(len(row) - 1, 1)
            return x, y / 3.0
    return 0.5, 0.5


@dataclass
class KeyboardState:
    buffer: str = ""
    last_key: str = ""
    last_xy: tuple[float, float] = (0.5, 0.5)
    target: str = ""
    history: list[str] = field(default_factory=list)

    @property
    def tokens(self) -> list[str]:
        return [t for t in self.buffer.replace("\n", " ").split(" ") if t]

    @property
    def prefix_ok(self) -> bool:
        if not self.buffer:
            return True
        if is_forbidden(self.buffer):
            return False
        line = self.buffer.split("\n")[0]
        return any(
            cmd.label.startswith(line) or line.startswith("fp")
            for cmd in ALLOWED_ACTIONS.values()
            if cmd.label
        )

    @property
    def matched_action(self) -> Action | None:
        line = self.buffer.strip()
        for action, cmd in ALLOWED_ACTIONS.items():
            if cmd.label and line == cmd.label:
                return action
        return None


def sense_keyboard(state: KeyboardState) -> dict[str, float]:
    x, y = state.last_xy
    buf = state.buffer
    return {
        "hand_x": x,
        "hand_y": y,
        "has_fp": 1.0 if buf.startswith("fp") else 0.0,
        "token_count": min(len(state.tokens) / 5.0, 1.0),
        "prefix_ok": 1.0 if state.prefix_ok else 0.0,
        "forbidden": 1.0 if is_forbidden(buf) else 0.0,
        "done": 1.0 if state.matched_action else 0.0,
        "progress": _progress(state),
    }


def _progress(state: KeyboardState) -> float:
    if not state.target:
        return 0.0
    n = 0
    for a, b in zip(state.buffer, state.target):
        if a != b:
            break
        n += 1
    return n / max(len(state.target), 1)


def next_key_for_target(state: KeyboardState) -> str:
    t = state.target
    b = state.buffer
    if not t:
        return "enter" if b else ""
    if is_forbidden(b) or (b and not t.startswith(b) and not b.startswith(t[: len(b)])):
        return "backspace" if b else ""
    if b == t:
        return "enter"
    if t.startswith(b):
        return key_id(t[len(b)])
    return "backspace"


def apply_key(state: KeyboardState, kid: str) -> KeyboardState:
    if kid == "backspace":
        state.buffer = state.buffer[:-1]
        ch = "backspace"
    elif kid == "enter":
        state.buffer += "\n"
        ch = "enter"
    elif kid == "space":
        state.buffer += " "
        ch = "space"
    elif kid == "dash":
        state.buffer += "-"
        ch = "dash"
    elif kid == "quote":
        state.buffer += '"'
        ch = "quote"
    elif len(kid) == 1:
        state.buffer += kid
        ch = kid
    else:
        ch = kid
    state.last_key = ch
    state.last_xy = key_xy(ch if ch != "backspace" else "backspace")
    state.history.append(ch)
    return state


def command_target(action: Action) -> str:
    return ALLOWED_ACTIONS[action].label
