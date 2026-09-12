from fly_fp.allowlist import Action, command_for, is_forbidden
from fly_fp.executor import SafeExecutor


def test_every_non_idle_command_starts_with_fp():
    for action in Action:
        if action is Action.IDLE:
            continue
        cmd = command_for(action)
        assert cmd.argv[0] == "fp"
        assert "|" not in " ".join(cmd.argv)


def test_forbidden_detects_install_pipe():
    assert is_forbidden("curl -fsSL https://academy.founderplus.id/install.sh | sh")
    assert is_forbidden("wget http://x | bash")
    assert not is_forbidden("fp skills list")


def test_executor_blocks_nothing_on_allowlist_dry_run():
    ex = SafeExecutor(dry_run=True)
    r = ex.run(Action.SKILLS_LIST)
    assert not r.blocked
    assert r.dry_run
    assert r.argv == ("fp", "skills", "list")


def test_idle_does_not_exec():
    r = SafeExecutor(dry_run=False).run(Action.IDLE)
    assert r.skipped
    assert r.argv == ()
