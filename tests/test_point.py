from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import pytest
from math import radians, tan
from build123d import Axis
from b3dkit.point import Point, midpoint, shifted_midpoint


class TestPoint:
    def test_point_creation_with_coordinates(self):
        p = Point(3.0, 4.0)
        assert p.x == 3.0
        assert p.y == 4.0

    def test_point_creation_with_list(self):
        p = Point([3.0, 4.0])
        assert p.x == 3.0
        assert p.y == 4.0

    def test_point_properties(self):
        p = Point(3.0, 4.0)
        assert p.X == 3.0
        assert p.Y == 4.0

    def test_point_iteration(self):
        p = Point(3.0, 4.0)
        coords = list(p)
        assert coords == [3.0, 4.0]

    def test_point_indexing(self):
        p = Point(3.0, 4.0)
        assert p[0] == 3.0
        assert p[1] == 4.0

        with pytest.raises(IndexError):
            _ = p[2]

    def test_angle_to(self):
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        angle = p1.angle_to(p2)
        assert angle == pytest.approx(45.0)

    def test_distance_to(self):
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        distance = p1.distance_to(p2)
        assert distance == pytest.approx(5.0)

    def test_related_point(self):
        p = Point(0, 0)
        related = p.related_point(45, 5)
        assert related.x == pytest.approx(3.5355339059327378)
        assert related.y == pytest.approx(3.5355339059327378)

    def test_related_point_by_axis_x(self):
        p = Point(0, 0)
        # At 45 degrees, if we move 4 units along x-axis, we should move 4 units along y-axis too
        related = p.related_point_by_axis(45, 4, Axis.X)
        assert related.x == pytest.approx(4.0)
        assert related.y == pytest.approx(4.0)

    def test_related_point_by_axis_y(self):
        p = Point(0, 0)
        # At 45 degrees, if we move 3 units along y-axis, we should move 3 units along x-axis too
        related = p.related_point_by_axis(45, 3, Axis.Y)
        assert related.x == pytest.approx(3.0)
        assert related.y == pytest.approx(3.0)

    def test_related_point_by_axis_30_degrees_x(self):
        p = Point(0, 0)
        # At 30 degrees, cos(30°) = √3/2 ≈ 0.866, sin(30°) = 1/2 = 0.5
        # If we move 2 units along x-axis, hypotenuse = 2/cos(30°) = 2/0.866 ≈ 2.309
        # y-distance = hypotenuse * sin(30°) = 2.309 * 0.5 ≈ 1.155
        related = p.related_point_by_axis(30, 2, Axis.X)
        assert related.x == pytest.approx(2.0)
        assert related.y == pytest.approx(1.1547005383792515)  # 2 * tan(30°)

    def test_related_point_by_axis_60_degrees_y(self):
        p = Point(0, 0)
        # At 60 degrees, sin(60°) = √3/2 ≈ 0.866, cos(60°) = 1/2 = 0.5
        # If we move 3 units along y-axis, hypotenuse = 3/sin(60°) = 3/0.866 ≈ 3.464
        # x-distance = hypotenuse * cos(60°) = 3.464 * 0.5 ≈ 1.732
        related = p.related_point_by_axis(60, 3, Axis.Y)
        assert related.x == pytest.approx(1.7320508075688772)  # 3 / tan(60°)
        assert related.y == pytest.approx(3.0)

    def test_related_point_by_axis_invalid_axis(self):
        p = Point(0, 0)
        with pytest.raises(ValueError, match="axis must be Axis.X or Axis.Y"):
            p.related_point_by_axis(45, 2, "invalid")

    def test_related_point_by_axis_zero_cosine(self):
        p = Point(0, 0)
        # At 90 degrees, cos(90°) ≈ 0, so we can't move along x-axis
        with pytest.raises(ValueError, match="Cannot move along x-axis at angle 90"):
            p.related_point_by_axis(90, 2, Axis.X)

    def test_related_point_by_axis_zero_sine(self):
        p = Point(0, 0)
        # At 0 degrees, sin(0°) = 0, so we can't move along y-axis
        with pytest.raises(ValueError, match="Cannot move along y-axis at angle 0"):
            p.related_point_by_axis(0, 2, Axis.Y)

    def test_related_point_by_axis_default_parameter(self):
        p = Point(0, 0)
        # Test that the default parameter is Axis.X
        related = p.related_point_by_axis(45, 4)  # Should default to Axis.X
        assert related.x == pytest.approx(4.0)
        assert related.y == pytest.approx(4.0)


class TestUtilityFunctions:
    def test_midpoint(self):
        p1 = Point(0, 0)
        p2 = Point(10, 10)
        mid = midpoint(p1, p2)
        assert mid.x == 5.0
        assert mid.y == 5.0

    def test_shifted_midpoint_no_shift(self):
        p1 = Point(0, 0)
        p2 = Point(10, 10)
        shifted_mid = shifted_midpoint(p1, p2, 0)
        assert shifted_mid.x == pytest.approx(5.0)
        assert shifted_mid.y == pytest.approx(5.0)

    def test_shifted_midpoint_with_shift(self):
        p1 = Point(0, 0)
        p2 = Point(10, 0)
        shifted_mid = shifted_midpoint(p1, p2, 2)
        assert shifted_mid.x == pytest.approx(7.0)  # 5 + 2
        assert shifted_mid.y == pytest.approx(0.0)

    def test_shifted_midpoint_diagonal_shift(self):
        p1 = Point(0, 0)
        p2 = Point(6, 8)  # 3-4-5 triangle scaled by 2
        shifted_mid = shifted_midpoint(p1, p2, 1)  # shift by 1 unit towards p2

        # Midpoint is at (3, 4)
        # Direction vector is (6, 8), normalized to (0.6, 0.8)
        # Shifted midpoint is (3, 4) + 1 * (0.6, 0.8) = (3.6, 4.8)
        assert shifted_mid.x == pytest.approx(3.6)
        assert shifted_mid.y == pytest.approx(4.8)
