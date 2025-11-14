from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch
import math
import pytest
from build123d import Part

from b3dkit.ball_socket import BallMount, BallSocket


# ---------- Helpers ----------
def expected_socket_height(r: float, w: float) -> float:
    # Matches current implementation: cylinder height = ball_radius + wall_thickness * 2.5
    return r + w * 2.5


def expected_socket_diameter(r: float, w: float) -> float:
    return 2 * (r + w)


# ---------- Ball Mount Tests ----------
class TestBallMount:
    def test_ball_mount_basic(self):
        mount = BallMount(10.0)
        assert isinstance(mount, Part)
        assert mount.is_valid
        bbox = mount.bounding_box()
        assert bbox.size.X == pytest.approx(20.0, abs=0.1)
        assert bbox.size.Y == pytest.approx(20.0, abs=0.1)
        # Height = 3.5 * radius (shaft from 0 to 2.25R, sphere center at 2.5R -> top 3.5R)
        assert bbox.size.Z == pytest.approx(35.0, abs=0.5)


class TestBallSocket:
    def test_ball_socket_basic(self):
        r = 10.0
        w = 2.0
        socket = BallSocket(r)
        assert isinstance(socket, Part)
        assert socket.is_valid
        assert socket.label == "Ball Socket"

    @pytest.mark.parametrize("r,w", [(3, 2), (5, 1), (10, 2), (20, 4), (12.5, 3.5)])
    def test_ball_socket_param_dimensions(self, r, w):
        socket = BallSocket(r, wall_thickness=w)
        assert socket.is_valid
        bbox = socket.bounding_box()

    def test_ball_socket_custom_wall_thickness(self):
        r, w = 10.0, 3.0
        socket = BallSocket(r, wall_thickness=w)

    def test_ball_socket_tolerance_does_not_change_outer_size(self):
        r, w = 10.0, 2.0
        base_bbox = BallSocket(r).bounding_box()
        bbox = BallSocket(r, tolerance=0.2).bounding_box()
        assert bbox.size.X == pytest.approx(base_bbox.size.X, abs=0.05)
        assert bbox.size.Z == pytest.approx(base_bbox.size.Z, abs=0.05)

    def test_ball_socket_wall_thickness_volume_growth(self):
        r = 10.0
        thin = BallSocket(r, wall_thickness=1.0)
        thick = BallSocket(r, wall_thickness=5.0)
        assert thin.volume < thick.volume

    def test_ball_socket_centered(self):
        socket = BallSocket(10.0)
        bbox = socket.bounding_box()
        assert abs(bbox.center().X) < 0.01
        assert abs(bbox.center().Y) < 0.01
        assert bbox.min.Z == pytest.approx(0.0, abs=0.01)

    def test_ball_socket_small_radius(self):
        r, w = 3.0, 2.0
        socket = BallSocket(r)
        bbox = socket.bounding_box()
        assert bbox.size.X == pytest.approx(expected_socket_diameter(r, w), abs=0.1)
        assert bbox.size.Z == pytest.approx(expected_socket_height(r, w), abs=0.1)

    def test_ball_socket_has_flex_cuts_volume_reduction(self):
        r, w = 10.0, 2.0
        socket = BallSocket(r)
        assert socket.volume > 0
        # Compare to solid cylinder of same outer size
        solid_volume = math.pi * (r + w) ** 2 * expected_socket_height(r, w)
        assert socket.volume < solid_volume * 0.9  # should be noticeably reduced


# ---------- Edge / Extreme Cases ----------
class TestEdgeCases:

    def test_extreme_tolerance_values(self):
        tight = BallSocket(10.0, tolerance=-0.1)
        loose = BallSocket(10.0, tolerance=1.0)
        assert tight.is_valid
        assert loose.is_valid
        assert loose.volume < BallSocket(10.0, tolerance=0.0).volume


# ---------- Direct Run ----------
class TestDirectRun:
    def test_direct_run(self):
        with patch("ocp_vscode.show"):
            loader = SourceFileLoader("__main__", "src/b3dkit/ball_socket.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))
