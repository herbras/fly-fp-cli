"""Fly brain → Founder+ CLI wrapper."""

__version__ = "0.1.0"

from fly_fp.allowlist import Action, ALLOWED_ACTIONS, command_for
from fly_fp.encoder import TerminalObs, encode
from fly_fp.brain import ReservoirBrain
from fly_fp.decoder import LinearReadout
from fly_fp.executor import SafeExecutor, ExecResult
from fly_fp.loop import FlyOperator

__all__ = [
    "Action",
    "ALLOWED_ACTIONS",
    "command_for",
    "TerminalObs",
    "encode",
    "ReservoirBrain",
    "LinearReadout",
    "SafeExecutor",
    "ExecResult",
    "FlyOperator",
]
