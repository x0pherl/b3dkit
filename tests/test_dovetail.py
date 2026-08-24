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
    DovetailSubpart,
    DovetailStyle,
    dovetail_subpart,
    _snugtail_subpart_outline,
    _dovetail_subpart_outline,
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
                    subpart=DovetailSubpart.TAIL,
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
                    subpart=DovetailSubpart.TAIL,
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
                    subpart=DovetailSubpart.TAIL,
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
                    subpart=DovetailSubpart.SOCKET,
                    scarf_angle=20,
                    vertical_offset=-0.5,
                ),
            )
        assert socket.part.is_valid

    def test_raises_invalid_style_for_snugtail(self):
        with pytest.raises(ValueError):
            _dovetail_subpart_outline(
                start=Point(-5, 0),
                end=Point(5, 0),
                subpart=DovetailSubpart.SOCKET,
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
                    subpart=DovetailSubpart.SOCKET,
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
                    subpart=DovetailSubpart.TAIL,
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
                    subpart=DovetailSubpart.TAIL,
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
                    subpart=DovetailSubpart.SOCKET,
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
            _snugtail_subpart_outline(
                Point(-5, 0),
                Point(5, 0),
                subpart=DovetailSubpart.SOCKET,
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
                    subpart=DovetailSubpart.TAIL,
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
                    subpart=DovetailSubpart.TAIL,
                    vertical_offset=0.5,
                ),
            )


def _split_box() -> Part:
    """A fresh reference solid for split tests."""
    with BuildPart(mode=Mode.PRIVATE) as test:
        Box(40, 60, 30, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return test.part


def _shape_signature(part: Part) -> tuple:
    """Volume plus centroid/bbox, so translation-only changes are still detectable.

    ``linear_offset`` slides the dovetail along the split line, which is
    volume-preserving -- asserting on volume alone would report it as inert.
    """
    center = part.center()
    bbox = part.bounding_box()
    return (
        part.volume,
        center.X,
        center.Y,
        bbox.min.X,
        bbox.max.X,
        bbox.min.Y,
        bbox.max.Y,
    )


def _subpart(**kwargs) -> Part:
    return dovetail_subpart(
        _split_box(), Point(-20, 0), Point(20, 0), **kwargs
    )


def _max_delta(a: tuple, b: tuple) -> float:
    return max(abs(x - y) for x, y in zip(a, b))


class TestDovetailParameterForwarding:
    """Every documented knob must actually reach the outline that consumes it.

    Regression coverage for the forwarding bug introduced in b079844 ("initial
    T Slot dovetail support"), which extracted ``_subpart_slab`` out of
    ``dovetail_subpart`` and declared ``linear_offset``, ``tail_angle_offset``,
    ``length_ratio`` and ``depth_ratio`` on the new helper without ever passing
    them to the inner ``_subpart_outline`` calls. The parameters were accepted and
    silently discarded, so ``dovetail.py`` held 100% line coverage while four
    public knobs did nothing.
    """

    @pytest.mark.parametrize(
        "style, param, value",
        [
            (DovetailStyle.TRADITIONAL, "length_ratio", 0.7),
            (DovetailStyle.TRADITIONAL, "depth_ratio", 0.3),
            (DovetailStyle.TRADITIONAL, "tail_angle_offset", 35),
            (DovetailStyle.TRADITIONAL, "linear_offset", 6),
            (DovetailStyle.SNUGTAIL, "length_ratio", 0.7),
            (DovetailStyle.SNUGTAIL, "tail_angle_offset", 35),
            (DovetailStyle.T_SLOT, "slot_count", 3),
            (DovetailStyle.T_SLOT, "depth", 5),
        ],
    )
    def test_parameter_changes_geometry(self, style, param, value):
        baseline = _shape_signature(_subpart(style=style))
        altered = _shape_signature(_subpart(style=style, **{param: value}))
        assert _max_delta(baseline, altered) > 1e-6, (
            f"{param} is inert for {style.name}: it is accepted but does not "
            "affect the resulting geometry"
        )


class TestSnugtailDepthRatioDecoupling:
    """``depth_ratio`` is deliberately withheld from snugtail. Do not "fix" this.

    Commit 3ed5a50 forwarded ``depth_ratio`` to snugtail; three days later
    f6c4b7b ("changes to proportions after physical prototyping") removed it
    again as part of a coordinated retune that halved ``tail_depth`` throughout
    and dropped ``depth_ratio`` out of snugtail's ``cut_length`` formulas
    entirely. The parameter no longer means for snugtail what it means for
    TRADITIONAL, and ``_snugtail_subpart_outline`` keeps its own prototyped
    default of 0.15.

    These tests exist so that re-forwarding it fails loudly rather than silently
    changing the geometry of every snugtail joint ever printed.
    """

    def test_depth_ratio_does_not_reach_snugtail(self, monkeypatch):
        import b3dkit.dovetail as dovetail_module

        received = []
        original = dovetail_module._snugtail_subpart_outline

        def spy(*args, **kwargs):
            received.append(kwargs.get("depth_ratio"))
            return original(*args, **kwargs)

        monkeypatch.setattr(dovetail_module, "_snugtail_subpart_outline", spy)
        _subpart(style=DovetailStyle.SNUGTAIL, depth_ratio=0.3)

        assert received, "_snugtail_subpart_outline was never called"
        assert all(value is None for value in received), (
            "depth_ratio reached _snugtail_subpart_outline; f6c4b7b deliberately "
            "decoupled it after physical prototyping"
        )

    def test_snugtail_geometry_ignores_depth_ratio(self):
        baseline = _shape_signature(_subpart(style=DovetailStyle.SNUGTAIL))
        altered = _shape_signature(
            _subpart(style=DovetailStyle.SNUGTAIL, depth_ratio=0.3)
        )
        assert _max_delta(baseline, altered) == pytest.approx(0, abs=1e-9)


class TestDefaultGeometryUnchanged:
    """Callers who pass no ratios must get byte-identical geometry to 0.1.5.

    Reference volumes captured from the pre-fix tree at commit 180f92e. Fixing
    the forwarding was only safe because every reachable default in the chain
    already agreed (1/3, 1/6, 15, 0) -- snugtail's own 0.8 ``length_ratio``
    default was unreachable through ``dovetail_subpart`` and stayed that way.
    """

    @pytest.mark.parametrize(
        "style, section, expected_volume",
        [
            (DovetailStyle.SNUGTAIL, DovetailSubpart.TAIL, 9244.107505),
            (DovetailStyle.SNUGTAIL, DovetailSubpart.SOCKET, 62680.650620),
            (DovetailStyle.TRADITIONAL, DovetailSubpart.TAIL, 38288.043194),
            (DovetailStyle.TRADITIONAL, DovetailSubpart.SOCKET, 33669.241040),
            (DovetailStyle.T_SLOT, DovetailSubpart.TAIL, 35802.080480),
            (DovetailStyle.T_SLOT, DovetailSubpart.SOCKET, 36162.080473),
        ],
    )
    def test_default_volume_matches_pre_fix_reference(
        self, style, section, expected_volume
    ):
        part = _subpart(style=style, subpart=section)
        assert part.volume == pytest.approx(expected_volume, abs=1e-4)
