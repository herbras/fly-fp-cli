from fly_fp.malecns import data_ready, status


def test_status_does_not_crash():
    st = status()
    assert "ready" in st
    assert "fly_data" in st
    assert st["ready"] is data_ready()


def test_make_brain_stub_still_works():
    from fly_fp.brain import make_brain
    b = make_brain("stub")
    out = b.rollout([0.2] * 8, steps=3)
    assert len(out) == 64
