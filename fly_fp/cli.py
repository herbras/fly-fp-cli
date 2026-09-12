"""CLI entry: fly-fp dry-run | live | demo | type."""

from __future__ import annotations

import argparse
import json
import sys

from fly_fp import __version__
from fly_fp.allowlist import ALLOWED_ACTIONS, Action, parse_action
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
        print(
            json.dumps(
                {
                    "action": log.action.value,
                    "argv": list(log.result.argv),
                    "exit_code": log.result.exit_code,
                    "blocked": log.result.blocked,
                    "dry_run": log.result.dry_run,
                    "reward": log.reward,
                    "sensory": log.sensory,
                },
                indent=2,
            )
        )
    return 0 if not log.result.blocked else 2


def cmd_actions(_: argparse.Namespace) -> int:
    for action, cmd in ALLOWED_ACTIONS.items():
        print(f"{action.value:28}  {' '.join(cmd.argv) or '(idle)'}")
    return 0


def cmd_type(args: argparse.Namespace) -> int:
    action = parse_action(args.action)
    fly = FlyTypist(target_action=action)
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
    p = argparse.ArgumentParser(
        prog="fly-fp",
        description="Fruit-fly reservoir that may only emit allowlisted Founder+ CLI commands.",
    )
    p.add_argument("--brain", default="stub", choices=("stub", "flyai"))
    p.add_argument("--live", action="store_true", help="actually exec fp (still allowlisted)")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo", help="run the 9-goal curriculum")
    d.set_defaults(fn=cmd_demo)

    o = sub.add_parser("once", help="one observation → one action")
    o.add_argument("--stdout", default="")
    o.add_argument("--stderr", default="")
    o.add_argument("--goal", nargs="*")
    o.add_argument("--json", action="store_true")
    o.set_defaults(fn=cmd_once)

    a = sub.add_parser("actions", help="print the allowlist")
    a.set_defaults(fn=cmd_actions)

    t = sub.add_parser("type", help="fly types an allowlisted command key by key")
    t.add_argument("--action", default="skills_list")
    t.add_argument("--delay", type=float, default=0.04)
    t.add_argument("--clear", action="store_true", help="redraw like a cockpit")
    t.set_defaults(fn=cmd_type)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
