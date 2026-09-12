"""ASCII cockpit: terminal + tiny activity + keyboard under the fly."""

from __future__ import annotations

from fly_fp.keyboard import ROWS, KeyboardState


_KEY_W = {
    "space": "[      space      ]",
    "enter": "[enter]",
    "backspace": "[bksp]",
}


def render_keyboard(state: KeyboardState) -> str:
    lit = state.last_key
    lines = ["\u250c\u2500 FLY KEYBOARD \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510"]
    for row in ROWS:
        cell = []
        for k in row:
            if k == lit:
                cell.append(f"[{k.upper()}]")
            else:
                cell.append(f" {k} ")
        lines.append("\u2502 " + "".join(cell).ljust(40) + "\u2502")
    space = _KEY_W["space"]
    if lit == "space":
        space = "[****** SPACE ******]"
    enter = "[ENTER]" if lit == "enter" else "[enter]"
    bk = "[BKSP]" if lit == "backspace" else "[bksp]"
    lines.append(f"\u2502 {bk}  {space}  {enter}".ljust(41) + "\u2502")
    lines.append("\u2514" + "\u2500" * 40 + "\u2518")
    return "\n".join(lines)


def render_activity(spikes: list[float], width: int = 32) -> str:
    if not spikes:
        return ""
    n = min(len(spikes), 16)
    rows = []
    for i in range(n):
        bar = int(spikes[i] * width)
        rows.append("\u2588" * bar + "\u00b7" * (4 - min(bar, 4)))
    return "cns " + " ".join(rows[:8])


def render_cockpit(buffer: str, meaning: str, key: str, spikes: list[float], state: KeyboardState) -> str:
    shown = buffer.replace("\n", "\u21b5")
    return "\n".join(
        [
            "ETHARD  CONNECTOME > FLY > KEYBOARD > FP",
            "fly@dev:~/founderplus $ " + shown + "\u2588",
            f"next key: {key or '\u2014'}    meaning: {meaning}",
            render_activity(spikes),
            render_keyboard(state),
        ]
    )
