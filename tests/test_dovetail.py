import pytest
from build123d import Align, Box, BuildPart, Mode, Part, add

from b3dkit.dovetail import (
    DovetailStyle,
    DovetailSubpart,
    _dovetail_subpart_outline,
    _snugtail_subpart_outline,
    dovetail_split,
    dovetail_subpart,
)
from b3dkit.point import Point


class TestDovetail:

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
    return dovetail_subpart(_split_box(), Point(-20, 0), Point(20, 0), **kwargs)


def _max_delta(a: tuple, b: tuple) -> float:
    return max(abs(x - y) for x, y in zip(a, b, strict=True))


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

    Passing it with SNUGTAIL now raises rather than being discarded, so these
    tests guard both halves of the contract: the argument is rejected at the
    public boundary, and the prototyped default still reaches the outline.
    """

    def test_depth_ratio_rejected_for_snugtail(self):
        with pytest.raises(
            ValueError, match="has no effect for DovetailStyle.SNUGTAIL"
        ):
            _subpart(style=DovetailStyle.SNUGTAIL, depth_ratio=0.3)

    def test_depth_ratio_does_not_reach_snugtail(self, monkeypatch):
        """Even for a default build, depth_ratio must not be forwarded."""
        import b3dkit.dovetail as dovetail_module

        received = []
        original = dovetail_module._snugtail_subpart_outline

        def spy(*args, **kwargs):
            received.append(kwargs.get("depth_ratio"))
            return original(*args, **kwargs)

        monkeypatch.setattr(dovetail_module, "_snugtail_subpart_outline", spy)
        _subpart(style=DovetailStyle.SNUGTAIL)

        assert received, "_snugtail_subpart_outline was never called"
        assert all(value is None for value in received), (
            "depth_ratio reached _snugtail_subpart_outline; f6c4b7b deliberately "
            "decoupled it after physical prototyping"
        )


class TestStyleConditionalArguments:
    """Arguments a style would discard must raise instead of being ignored.

    The applicability map is measured, not assumed: each entry below was
    confirmed to change (or not change) the resulting geometry.
    """

    @pytest.mark.parametrize(
        "style, param, value",
        [
            (DovetailStyle.SNUGTAIL, "depth_ratio", 0.3),
            (DovetailStyle.SNUGTAIL, "linear_offset", 6),
            (DovetailStyle.SNUGTAIL, "slot_count", 3),
            (DovetailStyle.SNUGTAIL, "depth", 5),
            (DovetailStyle.TRADITIONAL, "slot_count", 3),
            (DovetailStyle.TRADITIONAL, "depth", 5),
            (DovetailStyle.T_SLOT, "length_ratio", 0.7),
            (DovetailStyle.T_SLOT, "depth_ratio", 0.3),
            (DovetailStyle.T_SLOT, "tail_angle_offset", 35),
            (DovetailStyle.T_SLOT, "linear_offset", 6),
        ],
    )
    def test_inert_argument_raises(self, style, param, value):
        with pytest.raises(ValueError, match="has no effect"):
            _subpart(style=style, **{param: value})

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
    def test_applicable_argument_accepted(self, style, param, value):
        assert _subpart(style=style, **{param: value}).is_valid

    @pytest.mark.parametrize("style", list(DovetailStyle))
    def test_defaults_never_raise(self, style):
        assert _subpart(style=style).is_valid


class TestDovetailSplit:
    """``dovetail_split`` builds both halves from one argument set."""

    def test_returns_matching_pair(self):
        tail, socket = dovetail_split(_split_box(), Point(-20, 0), Point(20, 0))
        assert tail.is_valid and socket.is_valid
        assert tail.label != socket.label or tail.volume != socket.volume

    def test_halves_match_dovetail_subpart(self):
        kwargs = dict(style=DovetailStyle.TRADITIONAL, length_ratio=0.7)
        tail, socket = dovetail_split(
            _split_box(), Point(-20, 0), Point(20, 0), **kwargs
        )
        assert tail.volume == pytest.approx(
            _subpart(subpart=DovetailSubpart.TAIL, **kwargs).volume
        )
        assert socket.volume == pytest.approx(
            _subpart(subpart=DovetailSubpart.SOCKET, **kwargs).volume
        )

    def test_rejects_subpart_argument(self):
        with pytest.raises(TypeError, match="builds both subparts"):
            dovetail_split(
                _split_box(),
                Point(-20, 0),
                Point(20, 0),
                subpart=DovetailSubpart.TAIL,
            )

    def test_propagates_style_validation(self):
        with pytest.raises(ValueError, match="has no effect"):
            dovetail_split(
                _split_box(),
                Point(-20, 0),
                Point(20, 0),
                style=DovetailStyle.T_SLOT,
                length_ratio=0.7,
            )


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


def _narrow_box() -> Part:
    """A part narrow enough that snugtail's fins meet.

    Snugtail splits its own tail into disconnected fins once the part is about
    30mm wide -- see TestSnugtailWidthLimit -- so the single-solid tests use a
    width below that, to guard the defects they are about is_valid rather than
    that separate one.
    """
    with BuildPart(mode=Mode.PRIVATE) as test:
        Box(20, 50, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return test.part


def _narrow_subpart(**kwargs) -> Part:
    return dovetail_subpart(_narrow_box(), Point(-10, 0), Point(10, 0), **kwargs)


class TestSubpartsAreSingleSolids:
    """A subpart must come back in one piece, whatever the arguments.

    Two defects hid here for the library's whole history, both invisible to an
    is_valid assertion because every piece was individually a valid solid.

    A positive vertical_offset built the two Z-slabs with mismatched tolerance
    terms, cutting a slot clean through the socket and leaving it in two pieces
    with a tenth of its volume gone.

    click_fit_radius added each divot twice: a Divot is a BasePartObject, so it
    registers into the enclosing builder on construction, and the code then
    added a rotated copy as well. Because rotate() turns about the global
    origin, the builder's Location translated that copy again and it landed
    outside the part as a free-floating sliver.
    """

    @pytest.mark.parametrize("style", list(DovetailStyle))
    @pytest.mark.parametrize("vertical_offset", [0.0, 0.5, -0.5])
    @pytest.mark.parametrize("click_fit_radius", [0.0, 0.5])
    @pytest.mark.parametrize("subpart", [DovetailSubpart.TAIL, DovetailSubpart.SOCKET])
    def test_subpart_is_one_solid(
        self, style, vertical_offset, click_fit_radius, subpart
    ):
        part = _narrow_subpart(
            style=style,
            subpart=subpart,
            vertical_offset=vertical_offset,
            click_fit_radius=click_fit_radius,
        )
        solids = part.solids()
        assert len(solids) == 1, (
            f"{style.name} {subpart.name} at vertical_offset={vertical_offset}, "
            f"click_fit_radius={click_fit_radius} came back as {len(solids)} "
            f"solids: {sorted(round(s.volume, 4) for s in solids)}"
        )

    @pytest.mark.parametrize("style", list(DovetailStyle))
    @pytest.mark.parametrize("vertical_offset", [0.0, 0.5, -0.5])
    def test_tail_and_socket_account_for_the_whole_part(self, style, vertical_offset):
        """Together the two subparts should be the original, less tolerance.

        The vertical_offset defect showed up here first: the pair summed to 899
        of a 1000mm3 box, because the slot cut through the socket removed
        material that ended up in neither half.
        """
        kwargs = dict(style=style, vertical_offset=vertical_offset)
        total = sum(
            _narrow_subpart(subpart=s, **kwargs).volume
            for s in (DovetailSubpart.TAIL, DovetailSubpart.SOCKET)
        )
        box_volume = 20 * 50 * 10
        assert total == pytest.approx(box_volume, rel=0.02), (
            f"{style.name} at vertical_offset={vertical_offset}: tail and socket "
            f"sum to {total:.1f}, not the {box_volume} of the part they split"
        )


class TestSnugtailWidthLimit:
    """Snugtail splits its own tail into fins on parts wider than about 30mm.

    Not a regression: v0.1.5 produces byte-identical geometry. The tail comes
    back as two or three disconnected pieces with no sliver involved, so it is
    unrelated to the divot and vertical_offset defects fixed alongside these
    tests. It lives in the snugtail outline maths, which was tuned against
    physical prints, so it is recorded here rather than guessed at.

    These tests pin the current boundary. If a fix lands, they should fail and
    be replaced by an assertion that wide parts work.
    """

    @staticmethod
    def _tail_solids(width):
        with BuildPart(mode=Mode.PRIVATE) as test:
            Box(width, 60, 30, align=(Align.CENTER, Align.CENTER, Align.MIN))
        return len(
            dovetail_subpart(
                test.part,
                Point(-width / 2, 0),
                Point(width / 2, 0),
                subpart=DovetailSubpart.TAIL,
                style=DovetailStyle.SNUGTAIL,
                click_fit_radius=0,
            ).solids()
        )

    @pytest.mark.parametrize("width", [20, 24, 28])
    def test_narrow_parts_give_one_solid(self, width):
        assert self._tail_solids(width) == 1

    @pytest.mark.parametrize("width", [30, 36, 40])
    def test_wide_parts_currently_fragment(self, width):
        """Documents a known defect. Delete this when snugtail is fixed."""
        assert self._tail_solids(width) > 1
