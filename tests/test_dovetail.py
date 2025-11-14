from dataclasses import dataclass, field
from enum import Enum, auto
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import pytest
import os
from unittest.mock import patch
from pathlib import Path

from build123d import BuildPart, Box, Part, Sphere, Align, Mode, Location, add

from b3dkit.point import Point

from b3dkit.dovetail import (
    DovetailPart,
    DovetailStyle,
    dovetail_subpart,
    snugtail_subpart_outline,
    dovetail_subpart_outline,
)


class TestDovetail:

    def test_direct_run(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/b3dkit/dovetail.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))

    def test_start_end_match(self):
        with BuildPart(mode=Mode.PRIVATE) as test:
            Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with pytest.raises(ValueError):
            x = (
                dovetail_subpart(
                    test.part,
                    Point(5, 0),
                    Point(5, 0),
                ),
            )

    def test_vertical_offset_too_high(self):
        with BuildPart(mode=Mode.PRIVATE) as test:
            Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with pytest.raises(ValueError):
            x = (
                dovetail_subpart(
                    test.part,
                    Point(-5, 0),
                    Point(5, 0),
                    section=DovetailPart.TAIL,
                    vertical_offset=100,
                ),
            )

    def test_vertical_offset_too_low(self):
        with BuildPart(mode=Mode.PRIVATE) as test:
            Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with pytest.raises(ValueError):
            x = (
                dovetail_subpart(
                    test.part,
                    Point(-5, 0),
                    Point(5, 0),
                    section=DovetailPart.TAIL,
                    vertical_offset=-100,
                ),
            )

    def test_valid_traditional_tail(self):
        with BuildPart(mode=Mode.PRIVATE) as test:
            Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart() as tail:
            add(
                dovetail_subpart(
                    test.part,
                    Point(-5, 0),
                    Point(5, 0),
                    section=DovetailPart.TAIL,
                    style=DovetailStyle.TRADITIONAL,
                    vertical_offset=0.5,
                    click_fit_radius=0.5,
                ),
            )
        assert tail.part.is_valid

    def test_valid_socket(self):
        with BuildPart(mode=Mode.PRIVATE) as test:
            Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart() as socket:
            add(
                dovetail_subpart(
                    test.part,
                    Point(-5, 0),
                    Point(5, 0),
                    taper_angle=1,
                    section=DovetailPart.SOCKET,
                    scarf_angle=20,
                    vertical_offset=-0.5,
                ),
            )
        assert socket.part.is_valid

    def test_raises_invalid_style_for_snugtail(self):
        with pytest.raises(ValueError):
            dovetail_subpart_outline(
                start=Point(-5, 0),
                end=Point(5, 0),
                section=DovetailPart.SOCKET,
                style=DovetailStyle.SNUGTAIL,
            )

    def test_valid_tslot_socket(self):
        with BuildPart(mode=Mode.PRIVATE) as test:
            Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart() as socket:
            add(
                dovetail_subpart(
                    test.part,
                    Point(-5, 0),
                    Point(5, 0),
                    taper_angle=1,
                    style=DovetailStyle.T_SLOT,
                    section=DovetailPart.SOCKET,
                    scarf_angle=20,
                    vertical_offset=-0.5,
                ),
            )
        assert socket.part.is_valid

    def test_valid_tslot_tail(self):
        with BuildPart(mode=Mode.PRIVATE) as test:
            Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart() as tail:
            add(
                dovetail_subpart(
                    test.part,
                    Point(-5, 0),
                    Point(5, 0),
                    taper_angle=1,
                    style=DovetailStyle.T_SLOT,
                    section=DovetailPart.TAIL,
                    scarf_angle=20,
                    vertical_offset=-0.5,
                ),
            )
        assert tail.part.is_valid

    def test_valid_snugtail_tail(self):
        with BuildPart(mode=Mode.PRIVATE) as test:
            Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart() as tail:
            add(
                dovetail_subpart(
                    test.part,
                    Point(-5, 0),
                    Point(5, 0),
                    section=DovetailPart.TAIL,
                    style=DovetailStyle.SNUGTAIL,
                    vertical_offset=0.5,
                    click_fit_radius=1,
                ),
            )
        assert tail.part.is_valid

    def test_valid_snugtail_socket(self):
        with BuildPart(mode=Mode.PRIVATE) as test:
            Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart() as socket:
            add(
                dovetail_subpart(
                    test.part,
                    Point(-5, 0),
                    Point(5, 0),
                    taper_angle=1,
                    section=DovetailPart.SOCKET,
                    style=DovetailStyle.SNUGTAIL,
                    scarf_angle=20,
                    vertical_offset=-0.5,
                    click_fit_radius=1,
                ),
            )
        assert socket.part.is_valid

    def test_snugtail_ratios_exceed_max(self):
        with BuildPart(mode=Mode.PRIVATE) as test:
            Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with pytest.raises(ValueError):
            snugtail_subpart_outline(
                Point(-5, 0),
                Point(5, 0),
                section=DovetailPart.SOCKET,
                taper_distance=0,
                length_ratio=0.9,
                depth_ratio=0.11,
            )

    def test_valid_vert_tail(self):
        with BuildPart(mode=Mode.PRIVATE) as test:
            Box(10, 50, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with pytest.raises(ValueError):
            x = (
                dovetail_subpart(
                    test.part,
                    Point(-5, 0),
                    Point(5, 0),
                    taper_angle=-1,
                    section=DovetailPart.TAIL,
                    vertical_offset=-0.5,
                ),
            )
        with pytest.raises(ValueError):
            x = (
                dovetail_subpart(
                    test.part,
                    Point(-5, 0),
                    Point(5, 0),
                    taper_angle=0.5,
                    section=DovetailPart.TAIL,
                    vertical_offset=0.5,
                ),
            )


@pytest.mark.manual
def test_visualize_positive_voffset_dovetail():
    from ocp_vscode import show, Camera

    with BuildPart() as hanger:
        Box(20, 10, 2, align=[Align.CENTER, Align.MAX, Align.MIN])
        Box(20, 200, 2, align=[Align.CENTER, Align.MIN, Align.MIN])

    taper = 0
    scarf = -45
    voffset = 0.6
    top = dovetail_subpart(
        hanger.part,
        Point(-10, 17),
        Point(10, 17),
        section=DovetailPart.TAIL,
        taper_angle=taper,
        scarf_angle=scarf,
        vertical_offset=voffset,
    )
    bottom = dovetail_subpart(
        hanger.part,
        Point(-10, 17),
        Point(10, 17),
        section=DovetailPart.SOCKET,
        taper_angle=taper,
        scarf_angle=scarf,
        vertical_offset=voffset,
    ).move(Location((0, -15, 0)))

    with (
        patch("build123d.export_stl"),
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists"),
        patch("pathlib.Path.is_dir"),
        patch("ocp_vscode.show"),
        patch("ocp_vscode.save_screenshot"),
    ):
        show(top, bottom, reset_camera=Camera.KEEP)


@pytest.mark.manual
def test_visualize_negative_voffset_dovetail():
    from ocp_vscode import show, Camera
    from build123d import BuildSketch, make_face, Plane, Cylinder

    with BuildPart(mode=Mode.PRIVATE) as test:
        Box(40, 80, 78.7, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(
            Plane.XY.offset(73.6),
            mode=Mode.SUBTRACT,
        ):
            Cylinder(
                25,
                170,
                rotation=(90, 0, 0),
            )

    tl = dovetail_subpart(
        test.part,
        Point(-20, 0),
        Point(20, 0),
        section=DovetailPart.TAIL,
        tolerance=0.075,
        vertical_tolerance=0.2,
        taper_angle=2,
        scarf_angle=20,
        vertical_offset=-14.33333,
        click_fit_radius=0.75,
    ).move(Location((0, 0, 0)))
    sckt = dovetail_subpart(
        test.part,
        Point(-20, 0),
        Point(20, 0),
        section=DovetailPart.SOCKET,
        tolerance=0.075,
        vertical_tolerance=0.2,
        taper_angle=2,
        scarf_angle=20,
        vertical_offset=-14.33333,
        click_fit_radius=0.75,
    )
    sckt.color = (0.5, 0.5, 0.5)
    splines = snugtail_subpart_outline(
        Point(-25, 0),
        Point(25, 0),
        section=DovetailPart.SOCKET,
        taper_distance=0,
        # scarf_angle=20,
        straighten_dovetail=True,
    )
    spline = snugtail_subpart_outline(
        Point(-25, 0),
        Point(25, 0),
        section=DovetailPart.TAIL,
        taper_distance=0,
        # scarf_angle=20,
        straighten_dovetail=True,
    )
    with BuildSketch() as sks:
        add(splines)
        make_face()
    with BuildSketch() as sk:
        add(spline)
        make_face()
    from build123d import export_stl

    with (
        patch("build123d.export_stl"),
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists"),
        patch("pathlib.Path.is_dir"),
        patch("ocp_vscode.show"),
        patch("ocp_vscode.save_screenshot"),
    ):
        show(
            tl,
            sckt,
            # sk,
            # sks,
            # spline,
            # splines,
            reset_camera=Camera.KEEP,
        )


if __name__ == "__main__":
    test_visualize_positive_voffset_dovetail()
