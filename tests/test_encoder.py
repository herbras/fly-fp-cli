from fly_fp.encoder import TerminalObs, encode


def test_success_is_sweet_not_bitter():
    v = encode(TerminalObs("Usage: fp\nskills\nguidance\n", "", 0))
    assert v[0] > v[1]


def test_error_is_bitter():
    v = encode(TerminalObs("", "fp: command not found", 127))
    assert v[1] > 0.5


def test_pipe_install_is_looming_and_not_sweet():
    v = encode(TerminalObs("curl -fsSL https://academy.founderplus.id/install.sh | sh", "", 0))
    assert v[2] >= 0.9
    assert v[0] == 0.0


def test_goal_hit_sets_satiety():
    v = encode(TerminalObs("tutorial list here", "", 0, goal_tokens=("tutorial", "list")))
    assert v[6] >= 0.8
    assert v[5] == 0.0
