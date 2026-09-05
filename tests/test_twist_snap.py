from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch

from b3dkit.twist_snap import (
    TwistSnapConnector,
    TwistSnapSocket,
)
from conftest import module_path


class TestTwistSnap:
    def test_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", module_path("twist_snap"))
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))

    def test_twist_snap_connector(self):
        connector = TwistSnapConnector(
            connector_radius=4.5,
            tolerance=0.12,
            snapfit_height=2,
            snapfit_radius_extension=2 * (2 / 3) - 0.06,
            wall_width=2,
            wall_depth=2,
        )
        assert connector.is_valid

    def test_twist_snap_socket(self):
        socket = TwistSnapSocket(
            connector_radius=4.5,
            tolerance=0.12,
            snapfit_height=2,
            snapfit_radius_extension=2 * (2 / 3) - 0.06,
            wall_width=2,
            wall_depth=2,
        )
        assert socket.is_valid
