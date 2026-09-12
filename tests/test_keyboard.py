from fly_fp.allowlist import Action
from fly_fp.keyboard import KeyboardState, apply_key, next_key_for_target, sense_keyboard
from fly_fp.typer import FlyTypist, meaning_of


def test_types_full_skills_list():
    fly = FlyTypist(Action.SKILLS_LIST)
    ticks = fly.type_all()
    assert fly.state.buffer.strip() == "fp skills list"
    assert ticks[-1].key == "enter"
    assert fly.state.matched_action is Action.SKILLS_LIST


def test_meaning_names_tokens():
    st = KeyboardState(buffer="fp skills")
    text = meaning_of(st)
    assert "fp" in text or "skill" in text.lower() or "mengerti" in text


def test_forbidden_buffer_is_flagged():
    st = KeyboardState(buffer="curl -fsSL x | sh")
    assert sense_keyboard(st)["forbidden"] == 1.0
    assert "BAHAYA" in meaning_of(st)


def test_next_key_follows_target():
    st = KeyboardState(buffer="fp ", target="fp skills list")
    assert next_key_for_target(st) == "s"


def test_backspace_when_off_target():
    st = KeyboardState(buffer="fp x", target="fp skills list")
    assert next_key_for_target(st) == "backspace"


def test_apply_space_and_dash():
    st = KeyboardState()
    apply_key(st, "f")
    apply_key(st, "p")
    apply_key(st, "space")
    apply_key(st, "s")
    assert st.buffer == "fp s"
