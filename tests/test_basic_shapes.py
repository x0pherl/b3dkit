from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch
import pytest
from build123d import Box, BuildPart, Part, Align
from b3dkit.basic_shapes import (
    circular_intersection,
    DiamondTorus,
    distance_to_circle_edge,
    RoundedCylinder,
    DiamondCylinder,
    PolygonalCylinder,
    # rail_block_template,
    TeardropCylinder,
    Teardrop,
    radius_to_apothem,
    apothem_to_radius,
    opposite_length,
    adjacent_length,
)


class TestApothemConversions:
    def test_apothem_from_radius(self):
        assert radius_to_apothem(5) == pytest.approx(4.330127018922194)
        assert radius_to_apothem(5, 8) == pytest.approx(4.619397662556434)

    def test_radius_to_apothem(self):
        assert apothem_to_radius(5) == pytest.approx(5.773502691896257)
        assert apothem_to_radius(5, 8) == pytest.approx(5.41196100146197)


class TestTriangleFunctions:
    def test_opposite_length(self):
        # For a 45-degree angle, opposite = adjacent * tan(45°) = adjacent * 1
        opposite = opposite_length(45, 5)
        assert opposite == pytest.approx(5.0)

        # For a 30-degree angle, opposite = adjacent * tan(30°) = adjacent * (1/√3)
        opposite = opposite_length(30, 10)
        assert opposite == pytest.approx(5.773502691896257)

    def test_adjacent_length(self):
        # For a 45-degree angle, adjacent = opposite / tan(45°) = opposite / 1
        adjacent = adjacent_length(45, 5)
        assert adjacent == pytest.approx(5.0)

        # For a 30-degree angle, adjacent = opposite / tan(30°) = opposite / (1/√3) = opposite * √3
        adjacent = adjacent_length(30, 10)
        assert adjacent == pytest.approx(17.320508075688772)


class TestTearDropSketch:
    def test_teardropsketch(self):
        sketch = Teardrop(10, 12, align=(Align.MAX, Align.MIN))
        assert sketch.is_valid
        assert sketch.bounding_box().size.X == pytest.approx(20)
        assert sketch.bounding_box().size.Y == pytest.approx(22)

    def test_teardropsketch_aligned_no_peak(self):
        sketch = Teardrop(10, 10, align=(Align.MIN, Align.MAX))
        assert sketch.is_valid
        assert sketch.bounding_box().max.X == pytest.approx(20)
        assert sketch.bounding_box().min.Y == pytest.approx(-20)


class TestTeardropCylinder:
    def test_teardrop_cylinder(self):
        cyl = TeardropCylinder(
            radius=10,
            height=10,
            peak_distance=11,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        assert cyl.is_valid
        assert cyl.bounding_box().size.X == pytest.approx(20)
        assert cyl.bounding_box().size.Y == pytest.approx(21)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_align_zmax_teardrop_cylinder(self):
        cyl = TeardropCylinder(
            radius=10,
            height=10,
            peak_distance=11,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
        )
        assert cyl.is_valid
        assert cyl.bounding_box().size.X == pytest.approx(20)
        assert cyl.bounding_box().size.Y == pytest.approx(21)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_align_zcenter_teardrop_cylinder(self):
        cyl = TeardropCylinder(
            radius=10,
            height=10,
            peak_distance=11,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
        assert cyl.is_valid
        assert cyl.bounding_box().size.X == pytest.approx(20)
        assert cyl.bounding_box().size.Y == pytest.approx(21)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_teardrop_cylinder(self):
        cyl = TeardropCylinder(
            radius=10,
            height=10,
            peak_distance=11,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        assert cyl.is_valid
        assert cyl.bounding_box().size.X == pytest.approx(20)
        assert cyl.bounding_box().size.Y == pytest.approx(21)
        assert cyl.bounding_box().size.Z == pytest.approx(10)


class TestCircularIntersection:
    def test_circular_intersection(self) -> float:
        assert circular_intersection(10, 5) == 8.660254037844387

    def test_circular_intersection_discriminant_error(self):
        with pytest.raises(ValueError):
            circular_intersection(-25, -10) == 8.660254037844387


class TestTorus:
    def test_diamond_torus(self):
        torus = DiamondTorus(major_radius=10, minor_radius=1)
        assert isinstance(torus, Part)
        assert torus.bounding_box().size.X == pytest.approx(22)
        assert torus.bounding_box().size.Y == pytest.approx(22)
        assert torus.bounding_box().size.Z == pytest.approx(2)


class TestDistanceToCircleEdge:
    def test_distance_to_circle_edge(self):
        assert distance_to_circle_edge(10, (0, 5), 45) == 5.818609561002116

    def test_distance_to_circle_edge_discriminant_error(self):
        with pytest.raises(ValueError):
            distance_to_circle_edge(10, (0, 25), 45) == 5.818609561002116


class TestRoundedCylinder:
    def test_short_cylinder_fail(self):
        with pytest.raises(ValueError):
            cyl = RoundedCylinder(2, 3)

    def test_rounded_cylinder(self):
        cyl = RoundedCylinder(5, 11)
        assert cyl.is_valid
        assert isinstance(cyl, Part)
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(10)
        assert cyl.bounding_box().size.Z == pytest.approx(11)


class TestPolygonalCylinder:

    def test_diamond_cylinder(self):
        cyl = DiamondCylinder(5, 10)
        assert cyl.is_valid
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(10)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_diamond_cylinder_zmax(self):
        cyl = DiamondCylinder(5, 10, align=(Align.CENTER, Align.CENTER, Align.MAX))
        assert cyl.is_valid
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(10)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_polygonal_cylinder(self):
        cyl = PolygonalCylinder(5, 10)
        assert cyl.is_valid
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(10)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_polygonal_cylinder(self):
        cyl = PolygonalCylinder(5, 10, align=(Align.CENTER, Align.CENTER, Align.MAX))
        assert cyl.is_valid
        assert cyl.bounding_box().size.X == pytest.approx(10)
        assert cyl.bounding_box().size.Y == pytest.approx(8.660254237844388)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_teardrop_cylinder_z_alignment(self):
        radius = 5
        peak_distance = 6
        height = 10

        # Test Align.MAX (line 201-202)
        cylinder_max = TeardropCylinder(
            radius=radius,
            height=height,
            peak_distance=peak_distance,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
        )
        assert cylinder_max.is_valid

        # Test Align.CENTER (line 203)
        cylinder_center = TeardropCylinder(
            radius=radius,
            peak_distance=peak_distance,
            height=height,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
        assert cylinder_center.is_valid

        # Test Align.MIN (default case, not explicitly in those lines but completes coverage)
        cylinder_min = TeardropCylinder(
            radius=radius,
            peak_distance=peak_distance,
            height=height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        assert cylinder_min.is_valid

        # Verify that different alignments produce different Z positions
        # This ensures the alignment logic is actually working
        max_bbox_max_z = cylinder_max.bounding_box().max.Z
        center_bbox_max_z = cylinder_center.bounding_box().max.Z
        min_bbox_max_z = cylinder_min.bounding_box().max.Z

        # MAX should be highest, MIN should be lowest
        assert min_bbox_max_z > center_bbox_max_z > max_bbox_max_z


class TestBareExecution:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
        ):
            loader = SourceFileLoader("__main__", "src/b3dkit/basic_shapes.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))
