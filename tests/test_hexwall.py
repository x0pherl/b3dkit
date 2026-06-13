from collections import defaultdict
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from math import atan2, cos, degrees, sin
import pytest
from unittest.mock import patch

from build123d import Box, Cone, Cylinder, Align

from b3dkit.hexwall import HexWall, HexCylindrical


def _cone():
    """A tapering frustum (two circular edges) anchored on the build plate."""
    return Cone(100, 50, 100, align=(Align.CENTER, Align.CENTER, Align.MIN))


class TestHexWall:
    def test_hexwall(self):
        pattern = HexWall(10, 10, 1, 1, 0.2)
        assert pattern.is_valid

    def test_hexwall_forces_odd_column_count(self):
        # length=13/apothem=1 yields an even raw column count, exercising the
        # branch that bumps it odd so the hex grid stays centered
        pattern = HexWall(13, 10, 1, 1, 0.2)
        assert pattern.is_valid

    def test_direct_run(self):

        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/b3dkit/hexwall.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))


class TestHexCylindrical:
    def test_cone_builds_all_rows(self):
        # every requested row fits on the surface -> one cutter per hole
        part = HexCylindrical(_cone(), 1, 2, 8, 5, 2, 5)
        assert part.is_valid
        assert len(part.children) == 8 * 5

    def test_cylinder_builds(self):
        # constant-radius path (straight wall) wraps cleanly too
        cyl = Cylinder(50, 80, align=(Align.CENTER, Align.CENTER, Align.MIN))
        part = HexCylindrical(cyl, 1, 2, 8, 5, 2, 10)
        assert part.is_valid
        assert len(part.children) == 8 * 5

    def test_rows_truncate_off_surface(self):
        # asking for more rows than fit stops at the top edge instead of raising
        part = HexCylindrical(_cone(), 1, 2, 8, 500, 2, 5)
        assert 0 < len(part.children) < 8 * 500
        assert len(part.children) % 8 == 0  # only whole rows are dropped

    def test_pointed_cone_single_edge(self):
        # a pointed cone exposes only one circular edge (the base); the apex
        # radius is inferred from the bounding box rather than a second edge
        pc = Cone(50, 0, 100, align=(Align.CENTER, Align.CENTER, Align.MIN))
        part = HexCylindrical(pc, 1, 2, 8, 5, 2, 10)
        assert part.is_valid
        assert len(part.children) == 8 * 5

    def test_non_revolved_solid_raises(self):
        # no circular edge -> cannot derive a radius-vs-height profile
        with pytest.raises(ValueError):
            HexCylindrical(Box(10, 10, 10), 1, 2, 8, 5, 2, 2)

    def test_no_holes_fit_raises(self):
        # z_distance past the top edge leaves no room for any row -> clear error
        # instead of an empty-shape failure downstream
        with pytest.raises(ValueError):
            HexCylindrical(_cone(), 1, 2, 8, 5, 2, 150)

    def test_rows_centered_symmetrically(self):
        # regression guard: each row is centered on the same meridian so the
        # pattern stays left/right symmetric instead of drifting up the taper
        part = HexCylindrical(_cone(), 1, 2, 8, 10, 2, 20)
        rows = defaultdict(list)
        for cutter in part.children:
            center = cutter.center()
            rows[round(center.Z, 1)].append(atan2(center.Y, center.X))
        assert len(rows) > 1  # ensure we actually compared multiple heights
        for angles in rows.values():
            # circular mean of the row's hole angles, robust to the +-180 wrap
            mean_angle = degrees(
                atan2(sum(sin(a) for a in angles), sum(cos(a) for a in angles))
            )
            assert abs(abs(mean_angle) - 180) < 5
