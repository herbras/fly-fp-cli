from fly_fp.desktop_fly import UPSTREAM, status


def test_status_keys():
    st = status()
    assert st["upstream"] == UPSTREAM
    assert "cloned" in st
    assert "git_on_path" in st
