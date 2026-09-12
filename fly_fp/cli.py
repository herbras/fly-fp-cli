"""CLI entry: fly-fp demo | type | desktop-fly | brain."""

from __future__ import annotations

import argparse
import json
import sys

from fly_fp import __version__
from fly_fp.allowlist import ALLOWED_ACTIONS, parse_action
from fly_fp.curriculum import CURRICULUM_GOALS
from fly_fp.encoder import TerminalObs
from fly_fp.loop import FlyOperator
from fly_fp.tui import render_cockpit
from fly_fp.typer import FlyTypist


def _print_log(log) -> None:
    res = log.result
    flag = "BLOCKED" if res.blocked else ("DRY" if res.dry_run else "LIVE")
    print(f"  [{flag}] {log.action.value:28}  reward={log.reward:+.2f}  exit={res.exit_code}")
    preview = (res.stdout or res.stderr).strip().splitlines()
    if preview:
        print(f"           {preview[0][:100]}")


def cmd_demo(args: argparse.Namespace) -> int:
    op = FlyOperator(brain_kind=args.brain, dry_run=not args.live)
    print(f"fly-fp {__version__}  brain={args.brain}  dry_run={op.dry_run}")
    print("install fp on the HOST only:")
    print("  curl -fsSL https://academy.founderplus.id/install.sh | sh")
    print()
    for title, expected, tokens in CURRICULUM_GOALS:
        print(f"goal: {title}  (want {expected.value})")
        logs = op.run_goal(tokens, TerminalObs(goal_tokens=tokens))
        for log in logs:
            _print_log(log)
        print()
    return 0


def cmd_once(args: argparse.Namespace) -> int:
    op = FlyOperator(brain_kind=args.brain, dry_run=not args.live)
    obs = TerminalObs(stdout=args.stdout or "", stderr=args.stderr or "", goal_tokens=tuple(args.goal or ()))
    log = op.step(obs)
    _print_log(log)
    if args.json:
        print(json.dumps({"action": log.action.value, "argv": list(log.result.argv), "exit_code": log.result.exit_code, "blocked": log.result.blocked, "dry_run": log.result.dry_run, "reward": log.reward}, indent=2))
    return 0 if not log.result.blocked else 2


def cmd_actions(_: argparse.Namespace) -> int:
    for action, cmd in ALLOWED_ACTIONS.items():
        print(f"{action.value:28}  {' '.join(cmd.argv) or '(idle)'}")
    return 0


def cmd_desktop(_: argparse.Namespace) -> int:
    from fly_fp.desktop_fly import print_howto, status
    st = status()
    for k, v in st.items():
        print(f"{k:20} {v}")
    print()
    print_howto()
    return 0 if st["cloned"] else 1


def cmd_brain(_: argparse.Namespace) -> int:
    from fly_fp.malecns import status
    st = status()
    for k, v in st.items():
        print(f"{k:20} {v}")
    print("note: default embodied brain is DesktopFly, not fly.ai")
    return 0


def cmd_fetch(_: argparse.Namespace) -> int:
    print("fetch-brain (fly.ai) is deprecated. Use:")
    print("  python -m fly_fp.cli desktop-fly")
    return 2


def cmd_type(args: argparse.Namespace) -> int:
    fly = FlyTypist(target_action=parse_action(args.action), brain_kind=args.brain)
    delay = max(args.delay, 0.0)
    last = None
    for tick in fly.type_all():
        last = tick
        frame = render_cockpit(tick.buffer, tick.meaning, tick.key, tick.spikes, fly.state)
        print("\033[2J\033[H" + frame if args.clear else frame)
        print()
        if delay:
            import time
            time.sleep(delay)
    if last and last.sense.get("done"):
        print(f"typed: {fly.state.buffer.strip()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="fly-fp")
    p.add_argument("--brain", default="stub", choices=("stub", "malecns", "flyai"))
    p.add_argument("--live", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo").set_defaults(fn=cmd_demo)
    o = sub.add_parser("once")
    o.add_argument("--stdout", default="")
    o.add_argument("--stderr", default="")
    o.add_argument("--goal", nargs="*")
    o.add_argument("--json", action="store_true")
    o.set_defaults(fn=cmd_once)
    sub.add_parser("actions").set_defaults(fn=cmd_actions)
    t = sub.add_parser("type")
    t.add_argument("--action", default="skills_list")
    t.add_argument("--delay", type=float, default=0.04)
    t.add_argument("--clear", action="store_true")
    t.set_defaults(fn=cmd_type)
    sub.add_parser("desktop-fly").set_defaults(fn=cmd_desktop)
    sub.add_parser("brain").set_defaults(fn=cmd_brain)
    sub.add_parser("fetch-brain").set_defaults(fn=cmd_fetch)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
