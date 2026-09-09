import pytest

from b3dkit.twist_snap import (
    TwistSnapConnector,
    TwistSnapSocket,
)


class TestTwistSnap:
    def test_twist_snap_connector(self):
        connector = TwistSnapConnector(
            connector_radius=4.5,
            snapfit_height=2,
            snapfit_radius_extension=2 * (2 / 3),
            wall_depth=2,
        )
        assert connector.volume == pytest.approx(275.6677, rel=1e-4)
        assert connector.bounding_box().size.X == pytest.approx(11.5451, rel=1e-4)
        # Known issue: the base and its four snapfits meet only on a shared
        # plane, so they never fuse and this returns five solids. Pinned rather
        # than asserted as correct; when it is fixed this should read == 1.
        assert len(connector.solids()) == 5

    def test_connector_takes_no_clearance_arguments(self):
        """All fit clearance lives on the socket; the connector is nominal.

        tolerance and wall_width were accepted here and read by nothing.
        Measured, the socket already opens its bore to
        connector_radius + tolerance, giving exactly the intended gap, so
        applying tolerance here as well would have doubled it.
        """
        import inspect

        params = inspect.signature(TwistSnapConnector).parameters
        assert "tolerance" not in params
        assert "wall_width" not in params

    def test_socket_bore_clears_the_connector_by_tolerance(self):
        """The clearance the socket actually provides, measured not assumed."""
        import math

        from build123d import Plane, section

        tolerance = 0.12
        shared = dict(
            connector_radius=4.5,
            snapfit_height=2,
            snapfit_radius_extension=2 * (2 / 3),
            wall_depth=2,
        )
        connector = TwistSnapConnector(**shared)
        socket = TwistSnapSocket(tolerance=tolerance, wall_width=2, **shared)

        def radii(part, z):
            xs = section(obj=part, section_by=Plane.XY.offset(z))
            return [math.hypot(v.X, v.Y) for v in xs.vertices()]

        connector_outer = max(radii(connector, 1.0))
        socket_bore = min(radii(socket, 1.0))
        assert socket_bore - connector_outer == pytest.approx(tolerance, abs=1e-6)

    def test_twist_snap_socket(self):
        socket = TwistSnapSocket(
            connector_radius=4.5,
            tolerance=0.12,
            snapfit_height=2,
            snapfit_radius_extension=2 * (2 / 3) - 0.06,
            wall_width=2,
            wall_depth=2,
        )
        assert len(socket.solids()) == 1
        assert socket.volume == pytest.approx(630.1939, rel=1e-4)
        # the socket has to swallow the connector, so it is the wider part
        assert socket.bounding_box().size.X > 11.5451
