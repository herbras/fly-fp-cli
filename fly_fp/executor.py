"""Run allowlisted fp commands only. Never a pipe, never curl."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass

from fly_fp.allowlist import (
    ALLOWED_ACTIONS,
    Action,
    Command,
    command_for,
    is_forbidden,
)


@dataclass
class ExecResult:
    action: Action
    argv: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
    blocked: bool = False
    skipped: bool = False
    dry_run: bool = False


class SafeExecutor:
    def __init__(
        self,
        dry_run: bool = True,
        timeout: float = 30.0,
        fp_bin: str | None = None,
    ):
        self.dry_run = dry_run
        self.timeout = timeout
        self.fp_bin = fp_bin or shutil.which("fp")

    def run(self, action: Action) -> ExecResult:
        if action is Action.IDLE:
            return ExecResult(action, (), 0, "", "", skipped=True, dry_run=self.dry_run)

        cmd: Command = command_for(action)
        joined = " ".join(cmd.argv)
        if is_forbidden(joined):
            return ExecResult(action, cmd.argv, 126, "", "blocked by allowlist", blocked=True)

        if cmd.argv and cmd.argv[0] != "fp":
            return ExecResult(action, cmd.argv, 126, "", "binary must be fp", blocked=True)

        if self.dry_run:
            tokens = " ".join(cmd.expect_tokens)
            preview = f"[dry-run] {' '.join(cmd.argv)}\n{cmd.label}\n{tokens}\n"
            return ExecResult(action, cmd.argv, 0, preview, "", dry_run=True)

        binary = self.fp_bin or "fp"
        argv = (binary,) + cmd.argv[1:]
        env = os.environ.copy()
        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
                shell=False,
            )
        except FileNotFoundError:
            return ExecResult(
                action,
                argv,
                127,
                "",
                "fp not installed. On the HOST run:\n"
                "  curl -fsSL https://academy.founderplus.id/install.sh | sh\n"
                "The fly is not allowed to run that itself.",
            )
        except subprocess.TimeoutExpired:
            return ExecResult(action, argv, 124, "", "timed out", blocked=True)

        out, err = proc.stdout or "", proc.stderr or ""
        if is_forbidden(out) or is_forbidden(err):
            return ExecResult(action, argv, 126, "", "output contained forbidden text", blocked=True)
        return ExecResult(action, argv, proc.returncode, out, err)
