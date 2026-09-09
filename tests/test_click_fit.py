import pytest

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
        assert len(bump.solids()) == 1
        assert bump.volume == pytest.approx(3676.0264, rel=1e-4)
        # extending the base makes it taller than the plain divot
        assert bump.bounding_box().size.Z > Divot(10, True).bounding_box().size.Z
