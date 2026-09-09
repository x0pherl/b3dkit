from b3dkit.click_fit import Divot


class TestClickfit:
    def test_divot(self):
        hole = Divot(10, False)
        assert hole.is_valid
        bump = Divot(10, True)
        assert bump.is_valid
        assert hole.volume > bump.volume

    def test_divot_extend_base(self):
        bump = Divot(10, True, extend_base=True)
        assert bump.is_valid
