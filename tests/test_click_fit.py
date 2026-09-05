from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch

from b3dkit.click_fit import Divot
from conftest import module_path


class TestClickfit:
    def test_divot(self):
        hole = Divot(10, False)
        assert hole.is_valid
        bump = Divot(10, True)
        assert bump.is_valid
        assert hole.volume > bump.volume

    def test_divot_extend_base(self):
        bump = Divot(10, True, extend_base=True)
        assert bump.is_valid

    def test_direct_run(self):

        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", module_path("click_fit"))
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))
