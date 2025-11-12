from dataclasses import dataclass, field
from enum import Enum, auto
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import pytest
from unittest.mock import patch
from pathlib import Path

from build123d import Axis, BuildPart, Box, Align, fillet

from b3dkit.slide_box import slide_box


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
            loader = SourceFileLoader("__main__", "src/b3dkit/slide_box.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))
