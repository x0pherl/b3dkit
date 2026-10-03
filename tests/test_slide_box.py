from math import cos, radians

import pytest
from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Edge,
    Location,
    Plane,
    fillet,
    section,
)

from b3dkit.slide_box import _slider_template, slide_box


class TestSlideBox:
    def test_slide_box(self):
        with BuildPart() as base_box:
            Box(20, 44, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
            fillet(base_box.part.edges().filter_by(Axis.Z), radius=1.5)

        sb = slide_box(
            base_box.part, wall_thickness=2, thumb_radius=3.5, divot_radius=0.5
        )
        box, lid = sb.children
        assert (box.label, lid.label) == ("box", "lid")
        assert len(box.solids()) == 1
        assert len(lid.solids()) == 1
        assert box.volume == pytest.approx(4604.7926, rel=1e-4)
        assert lid.volume == pytest.approx(1344.8752, rel=1e-4)
        # the lid slides inside the box, so it must be narrower
        assert lid.bounding_box().size.X < box.bounding_box().size.X


class TestSliderDivots:
    """
    The divots sit against the tapered sliding faces of the template. Placing one
    so that it merely grazes a tapered face leaves needle-thin slivers behind the
    boolean, which show up as a nick in the rail the lid slides through.

    A pair of divots must therefore contribute exactly two solids, and each must
    be a real divot rather than a sliver -- the two failure modes are a doubled
    solid count and a solid orders of magnitude too small.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def sketch(cls):
        with BuildPart() as blank:
            Box(60, 100, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
            fillet(blank.part.edges().filter_by(Axis.Z), radius=1.5)
        return section(obj=blank.part, section_by=Plane.XY.offset(20))

    @staticmethod
    def _divot_solids(sketch, wall, radius, tolerance, cut_template=True):
        """the geometry the divots add to an otherwise identical template"""
        with_divots = _slider_template(
            sketch,
            wall,
            tolerance=tolerance,
            divot_radius=radius,
            cut_template=cut_template,
        )
        without_divots = _slider_template(
            sketch, wall, tolerance=tolerance, divot_radius=0, cut_template=cut_template
        )
        return (with_divots - without_divots).solids()

    @pytest.mark.parametrize("cut_template", [True, False])
    @pytest.mark.parametrize("wall", [2.0, 3.0, 4.0])
    @pytest.mark.parametrize("radius", [0.5, 0.75, 0.9, 1.0, 1.25])
    def test_divots_contribute_exactly_two_solids(
        self, sketch, wall, radius, cut_template
    ):
        # the sweep matters -- the tangency only bites on some wall/radius
        # combinations, so any single pairing passes on its own
        solids = self._divot_solids(
            sketch, wall, radius, tolerance=0.2, cut_template=cut_template
        )

        assert len(solids) == 2
        assert min(s.volume for s in solids) > radius**3 * 1e-2

    def test_wide_divot_clears_the_open_front(self, sketch):
        # a divot wider than half the wall used to overhang the front face of
        # the template, slivering against it the same way the taper did
        solids = self._divot_solids(sketch, wall=1.5, radius=1.25, tolerance=0.3)

        assert len(solids) == 2
        assert min(s.volume for s in solids) > 1.25**3 * 1e-2


class TestSlideBoxFit:
    """
    The tolerance is the total gap between lid and box on every mating face:
    the slot grows by half of it and the lid shrinks by half of it. The lid
    top stays flush with the box top.
    """

    WALL = 2
    TOP = 14

    @pytest.fixture(scope="class")
    @classmethod
    def base(cls):
        with BuildPart() as base_box:
            Box(20, 44, cls.TOP, align=(Align.CENTER, Align.CENTER, Align.MIN))
            fillet(base_box.part.edges().filter_by(Axis.Z), radius=1.5)
        return base_box.part

    def _fit(self, base, tolerance, divot_radius=0):
        """the box and the lid flipped back into place on it"""
        box, lid = slide_box(
            base,
            wall_thickness=self.WALL,
            thumb_radius=0,
            tolerance=tolerance,
            divot_radius=divot_radius,
        ).children
        return box, lid.moved(Location((0, 0, 0), (0, 180, 0)))

    @staticmethod
    def _along_x(part, z):
        """the edges where a line along +x at y=0 passes through the part"""
        return (Edge.make_line((0, 0, z), (20, 0, z)) & part).edges()

    @pytest.mark.parametrize("tolerance", [0.1, 0.15, 0.3])
    def test_lid_thickness(self, base, tolerance):
        _, lid = self._fit(base, tolerance)

        assert lid.bounding_box().max.Z == pytest.approx(self.TOP, abs=1e-4)
        assert lid.bounding_box().size.Z == pytest.approx(
            self.WALL - tolerance / 2, abs=1e-4
        )

    @pytest.mark.parametrize("tolerance", [0.1, 0.15, 0.3])
    def test_slot_depth(self, base, tolerance):
        box, _ = self._fit(base, tolerance)
        floor = self.TOP - self.WALL - tolerance / 2

        def first_material(z):
            return min(e.bounding_box().min.X for e in self._along_x(box, z))

        # the slot floor is a ledge: just above it the opening reaches out to
        # the rail, just below it only to the inner wall of the box
        cavity_wall = 10 - self.WALL - tolerance
        assert first_material(floor - 0.01) == pytest.approx(cavity_wall, abs=1e-4)
        assert first_material(floor + 0.01) > cavity_wall + 0.5

    @pytest.mark.parametrize("tolerance", [0.1, 0.15, 0.3])
    def test_tapered_face_gap(self, base, tolerance):
        box, lid = self._fit(base, tolerance)
        z = self.TOP - 0.5

        slot_face = min(e.bounding_box().min.X for e in self._along_x(box, z))
        lid_face = max(e.bounding_box().max.X for e in self._along_x(lid, z))
        # measured horizontally, a normal gap of `tolerance` on a face leaning
        # 22.5 degrees
        assert slot_face - lid_face == pytest.approx(
            tolerance / cos(radians(22.5)), abs=1e-4
        )

    @pytest.mark.parametrize("divot_radius", [0, 0.5])
    @pytest.mark.parametrize("tolerance", [0.1, 0.15, 0.3])
    def test_no_interference(self, base, tolerance, divot_radius):
        box, lid = self._fit(base, tolerance, divot_radius)

        overlap = box & lid
        assert sum(s.volume for s in overlap.solids()) == pytest.approx(0, abs=1e-6)

    @pytest.mark.parametrize("tolerance", [0.1, 0.15, 0.3])
    def test_divots_align(self, base, tolerance):
        plain_box, plain_lid = self._fit(base, tolerance)
        box, lid = self._fit(base, tolerance, divot_radius=0.5)

        detents = sorted(
            (s.center().X, s.center().Y) for s in (plain_box - box).solids()
        )
        bumps = sorted((s.center().X, s.center().Y) for s in (lid - plain_lid).solids())
        assert len(detents) == len(bumps) == 2
        for detent, bump in zip(detents, bumps, strict=True):
            assert detent == pytest.approx(bump, abs=1e-4)
