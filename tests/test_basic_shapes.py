from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from inspect import signature
from unittest.mock import patch
import pytest
from build123d import Circle, Part, Align
from b3dkit.basic_shapes import (
    DiamondTorus,
    DiamondCylinder,
    PolygonalCylinder,
    RoundedCylinder,
    Teardrop,
    TeardropCylinder,
    adjacent_length,
    apothem_to_radius,
    circular_intersection,
    distance_to_circle_edge,
    opposite_length,
    radius_to_apothem,
)


# PolygonalCylinder / DiamondCylinder build their profile with Circle(arc_size=...).
# Native arc_size support landed in build123d's 0.10.1 dev line; the compatibility
# monkey-patch that used to backfill it on older releases has been removed, so skip
# the arc_size-dependent shapes when the installed build123d can't accept it.
requires_circle_arc_size = pytest.mark.skipif(
    "arc_size" not in signature(Circle.__init__).parameters,
    reason="installed build123d Circle lacks native arc_size support (needs >= 0.10.1)",
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
    @pytest.mark.parametrize(
        "align",
        [
            (Align.CENTER, Align.CENTER, Align.MIN),
            (Align.CENTER, Align.CENTER, Align.CENTER),
            (Align.CENTER, Align.CENTER, Align.MAX),
        ],
        ids=["z_min", "z_center", "z_max"],
    )
    def test_teardrop_cylinder_dimensions_across_z_alignments(self, align):
        cyl = TeardropCylinder(
            radius=10,
            height=10,
            peak_distance=11,
            align=align,
        )
        assert cyl.is_valid
        assert cyl.bounding_box().size.X == pytest.approx(20)
        assert cyl.bounding_box().size.Y == pytest.approx(21)
        assert cyl.bounding_box().size.Z == pytest.approx(10)

    def test_teardrop_cylinder_z_alignment(self):
        radius = 5
        peak_distance = 6
        height = 10

        cylinder_max = TeardropCylinder(
            radius=radius,
            height=height,
            peak_distance=peak_distance,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
        )
        assert cylinder_max.is_valid

        cylinder_center = TeardropCylinder(
            radius=radius,
            peak_distance=peak_distance,
            height=height,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
        )
        assert cylinder_center.is_valid

        cylinder_min = TeardropCylinder(
            radius=radius,
            peak_distance=peak_distance,
            height=height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        assert cylinder_min.is_valid

        max_bbox_max_z = cylinder_max.bounding_box().max.Z
        center_bbox_max_z = cylinder_center.bounding_box().max.Z
        min_bbox_max_z = cylinder_min.bounding_box().max.Z

        assert min_bbox_max_z > center_bbox_max_z > max_bbox_max_z


class TestCircularIntersection:
    def test_circular_intersection(self):
        assert circular_intersection(10, 5) == pytest.approx(8.660254037844387)

    @pytest.mark.parametrize(
        "radius, coordinate",
        [(-25, -10), (10, 25), (10, -25)],
        ids=["negative_radius", "coordinate_gt_radius", "coordinate_lt_zero"],
    )
    def test_circular_intersection_rejects_invalid_inputs(self, radius, coordinate):
        with pytest.raises(ValueError, match="x-coordinate"):
            circular_intersection(radius, coordinate)


class TestTorus:
    def test_diamond_torus(self):
        torus = DiamondTorus(major_radius=10, minor_radius=1)
        assert isinstance(torus, Part)
        assert torus.bounding_box().size.X == pytest.approx(22)
        assert torus.bounding_box().size.Y == pytest.approx(22)
        assert torus.bounding_box().size.Z == pytest.approx(2)


class TestDistanceToCircleEdge:
    def test_distance_to_circle_edge(self):
        assert distance_to_circle_edge(10, (0, 5), 45) == pytest.approx(
            5.818609561002116
        )

    def test_distance_to_circle_edge_rejects_point_outside_circle(self):
        with pytest.raises(ValueError):
            distance_to_circle_edge(10, (0, 25), 45)


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


@requires_circle_arc_size
class TestPolygonalCylinder:

    @pytest.mark.parametrize(
        "kwargs, expected_xyz",
        [
            # 1) Baseline full hex prism
            (
                dict(radius=5, height=10),
                (10.0, 8.660254037844387, 10.0),
            ),
            # 2) Partial arc clips the profile (smaller or equal XY, same Z)
            (
                dict(radius=5, height=10, arc_size=180),
                None,  # custom assertions below
            ),
            # 3) Non-uniform stretch: Z via extrude, XY via post-scale
            (
                dict(radius=5, height=10, stretch=(2, 1.5, 1.2)),
                (20.0, 12.99038105676658, 12.0),
            ),
            # 4) Z alignment behavior check with same dimensions
            (
                dict(
                    radius=5,
                    height=10,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                ),
                (10.0, 8.660254037844387, 10.0),
            ),
        ],
    )
    def test_polygonal_cylinder_matrix(self, kwargs, expected_xyz):
        cyl = PolygonalCylinder(**kwargs)
        assert cyl.is_valid

        bbox = cyl.bounding_box()

        if expected_xyz is not None:
            ex, ey, ez = expected_xyz
            assert bbox.size.X == pytest.approx(ex)
            assert bbox.size.Y == pytest.approx(ey)
            assert bbox.size.Z == pytest.approx(ez)
        else:
            full = PolygonalCylinder(radius=kwargs["radius"], height=kwargs["height"])
            full_bbox = full.bounding_box()
            assert bbox.size.X <= full_bbox.size.X
            assert bbox.size.Y <= full_bbox.size.Y
            assert bbox.size.Z == pytest.approx(full_bbox.size.Z)
            assert cyl.volume < full.volume

    def test_polygonal_cylinder_align_z_positions(self):
        h = 10
        c_min = PolygonalCylinder(5, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
        c_ctr = PolygonalCylinder(
            5, h, align=(Align.CENTER, Align.CENTER, Align.CENTER)
        )
        c_max = PolygonalCylinder(5, h, align=(Align.CENTER, Align.CENTER, Align.MAX))

        assert (
            c_min.bounding_box().max.Z
            > c_ctr.bounding_box().max.Z
            > c_max.bounding_box().max.Z
        )


@requires_circle_arc_size
class TestDiamondCylinder:
    @pytest.mark.parametrize(
        "kwargs",
        [
            dict(radius=5, height=10),
            dict(
                radius=5,
                height=10,
                arc_size=180,
                stretch=(1.2, 0.8, 1.1),
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            ),
        ],
        ids=["defaults", "non_default_passthrough"],
    )
    def test_matches_polygonal_cylinder_side_count_4(self, kwargs):
        diamond = DiamondCylinder(**kwargs)
        poly4 = PolygonalCylinder(side_count=4, **kwargs)

        assert diamond.is_valid
        assert poly4.is_valid

        db = diamond.bounding_box().size
        pb = poly4.bounding_box().size
        assert db.X == pytest.approx(pb.X)
        assert db.Y == pytest.approx(pb.Y)
        assert db.Z == pytest.approx(pb.Z)
        assert diamond.volume == pytest.approx(poly4.volume)


@requires_circle_arc_size
class TestBareExecution:
    def test_bare_execution(self):
        with (
            patch("pathlib.Path.mkdir"),
            patch("ocp_vscode.show"),
        ):
            loader = SourceFileLoader("__main__", "src/b3dkit/basic_shapes.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))
