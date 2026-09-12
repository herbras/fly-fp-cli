"""Hard allowlist. The fly never chooses a raw shell string."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Action(str, Enum):
    IDLE = "idle"
    HELP = "help"
    SKILLS_LIST = "skills_list"
    SKILLS_SEARCH = "skills_search"
    SKILLS_INSTALL_MULAI_JUALAN = "skills_install_mulai_jualan"
    GUIDANCE = "guidance"
    GUIDANCE_TUTORIALS = "guidance_tutorials"
    CATALOG = "catalog"
    PRODUCTS_LIST = "products_list"
    NEW_LIST = "new_list"


@dataclass(frozen=True)
class Command:
    argv: tuple[str, ...]
    expect_tokens: tuple[str, ...]
    label: str


ALLOWED_ACTIONS: dict[Action, Command] = {
    Action.IDLE: Command((), (), "do nothing"),
    Action.HELP: Command(("fp", "--help"), ("usage", "fp", "help"), "fp --help"),
    Action.SKILLS_LIST: Command(
        ("fp", "skills", "list"), ("skill", "list"), "fp skills list"
    ),
    Action.SKILLS_SEARCH: Command(
        ("fp", "skills", "search", "marketing"),
        ("skill", "marketing"),
        "fp skills search marketing",
    ),
    Action.SKILLS_INSTALL_MULAI_JUALAN: Command(
        ("fp", "skills", "install", "mulai-jualan"),
        ("install", "mulai-jualan", "skill"),
        "fp skills install mulai-jualan",
    ),
    Action.GUIDANCE: Command(("fp", "guidance"), ("guidance", "tutorial"), "fp guidance"),
    Action.GUIDANCE_TUTORIALS: Command(
        ("fp", "guidance", "tutorials"),
        ("tutorial", "guidance"),
        "fp guidance tutorials",
    ),
    Action.CATALOG: Command(("fp", "catalog"), ("catalog",), "fp catalog"),
    Action.PRODUCTS_LIST: Command(
        ("fp", "products", "list"), ("product", "list"), "fp products list"
    ),
    Action.NEW_LIST: Command(("fp", "new", "--list"), ("template", "list"), "fp new --list"),
}

FORBIDDEN_SUBSTRINGS = (
    "curl",
    "wget",
    "| sh",
    "|sh",
    "| bash",
    "install.sh",
    "rm -",
    "sudo",
    "chmod",
    "eval",
    "python -c",
    "bash -c",
)


def command_for(action: Action) -> Command:
    return ALLOWED_ACTIONS[action]


def is_forbidden(text: str) -> bool:
    low = text.lower()
    return any(tok in low for tok in FORBIDDEN_SUBSTRINGS)


def parse_action(name: str) -> Action:
    key = name.strip().lower().replace("-", "_")
    return Action(key)
