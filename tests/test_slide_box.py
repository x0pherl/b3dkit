from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch

import pytest
from build123d import Align, Axis, Box, BuildPart, Plane, fillet, section

from b3dkit.slide_box import _slider_template, slide_box
from conftest import module_path


class TestSlideBox:
    def test_slide_box(self):
        with BuildPart() as base_box:
            Box(20, 44, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
            fillet(base_box.part.edges().filter_by(Axis.Z), radius=1.5)

        sb = slide_box(
            base_box.part, wall_thickness=2, thumb_radius=3.5, divot_radius=0.5
        )
        assert sb.children[0].is_valid
        assert sb.children[1].is_valid

    def test_direct_run(self):

        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", module_path("slide_box"))
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))


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
    def sketch(self):
        with BuildPart() as blank:
            Box(60, 100, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
            fillet(blank.part.edges().filter_by(Axis.Z), radius=1.5)
        return section(obj=blank.part, section_by=Plane.XY.offset(20))

    @staticmethod
    def _divot_solids(sketch, wall, radius, tolerance):
        """the geometry the divots add to an otherwise identical template"""
        with_divots = _slider_template(
            sketch, wall, tolerance=tolerance, divot_radius=radius, cut_template=True
        )
        without_divots = _slider_template(
            sketch, wall, tolerance=tolerance, divot_radius=0, cut_template=True
        )
        return (with_divots - without_divots).solids()

    @pytest.mark.parametrize("wall", [2.0, 3.0, 4.0])
    @pytest.mark.parametrize("radius", [0.5, 0.75, 0.9, 1.0, 1.25])
    def test_divots_contribute_exactly_two_solids(self, sketch, wall, radius):
        # the sweep matters -- the tangency only bites on some wall/radius
        # combinations, so any single pairing passes on its own
        solids = self._divot_solids(sketch, wall, radius, tolerance=0.2)

        assert len(solids) == 2
        assert min(s.volume for s in solids) > radius**3 * 1e-2

    def test_wide_divot_clears_the_open_front(self, sketch):
        # a divot wider than half the wall used to overhang the front face of
        # the template, slivering against it the same way the taper did
        solids = self._divot_solids(sketch, wall=1.5, radius=1.25, tolerance=0.3)

        assert len(solids) == 2
        assert min(s.volume for s in solids) > 1.25**3 * 1e-2
