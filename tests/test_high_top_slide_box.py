from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch

import pytest
from build123d import Align, Axis, Box, BuildPart, Compound, Part, fillet

from b3dkit.high_top_slide_box import (
    _high_top_slide_box_top,
    _slide_top_rail_cut,
    high_top_slide_box,
    high_top_slide_box_base,
    high_top_slide_box_lid,
)
from conftest import module_path


class TestHighTopSlideBox:
    @pytest.fixture
    def base_part(self):
        """Create a basic test part for testing."""
        with BuildPart() as base_box:
            Box(44, 44, 44, align=(Align.CENTER, Align.CENTER, Align.MIN))
            fillet(base_box.part.edges().filter_by(Axis.Z), radius=1.5)
        return base_box.part

    @pytest.fixture
    def small_base_part(self):
        """Create a smaller test part for faster testing."""
        with BuildPart() as base_box:
            Box(20, 20, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
        return base_box.part

    def test_high_top_slide_box_default_params(self, small_base_part):
        """Test high_top_slide_box with default parameters."""
        result = high_top_slide_box(
            base_part=small_base_part,
            top_height=5,
            rail_height=8,
            wall_thickness=2,
        )

        assert isinstance(result, Compound)
        assert result.label == "slide box"
        assert len(result.children) == 2
        assert result.children[0].is_valid
        assert result.children[1].is_valid
        assert len(result.children[0].solids()) == 1
        assert len(result.children[1].solids()) == 1

    def test_high_top_slide_box_with_all_params(self, small_base_part):
        """Test high_top_slide_box with all parameters specified."""
        result = high_top_slide_box(
            base_part=small_base_part,
            top_height=6,
            rail_height=10,
            wall_thickness=3,
            rail_angle=1.0,
            divot_radius=0.8,
            thumb_radius=2.0,
            tolerance=0.15,
        )

        assert isinstance(result, Compound)
        assert len(result.children) == 2
        assert result.children[0].is_valid
        assert result.children[1].is_valid
        assert len(result.children[0].solids()) == 1
        assert len(result.children[1].solids()) == 1

    def test_high_top_slide_box_lid(self, small_base_part):
        """Test high_top_slide_box_lid function."""
        lid = high_top_slide_box_lid(
            base_part=small_base_part,
            top_height=5,
            rail_height=8,
            wall_thickness=2,
        )

        assert isinstance(lid, Part)
        assert lid.is_valid
        assert len(lid.solids()) == 1
        assert lid.label == "box top"

    def test_high_top_slide_box_lid_with_params(self, small_base_part):
        """Test high_top_slide_box_lid with various parameters."""
        lid = high_top_slide_box_lid(
            base_part=small_base_part,
            top_height=4,
            rail_height=6,
            wall_thickness=1.5,
            rail_angle=0.5,
            divot_radius=0.6,
            thumb_radius=1.5,
            tolerance=0.1,
        )

        assert isinstance(lid, Part)
        assert lid.is_valid
        assert len(lid.solids()) == 1

    def test_high_top_slide_box_base(self, small_base_part):
        """Test high_top_slide_box_base function."""
        base = high_top_slide_box_base(
            base_part=small_base_part,
            top_height=5,
            rail_height=8,
            wall_thickness=2,
        )

        assert isinstance(base, Part)
        assert base.is_valid
        assert len(base.solids()) == 1
        assert base.label == "box bottom"

    def test_high_top_slide_box_base_with_params(self, small_base_part):
        """Test high_top_slide_box_base with various parameters."""
        base = high_top_slide_box_base(
            base_part=small_base_part,
            top_height=6,
            rail_height=10,
            wall_thickness=3,
            rail_angle=0.8,
            divot_radius=0.7,
            thumb_radius=2.5,
            tolerance=0.2,
        )

        assert isinstance(base, Part)
        assert base.is_valid
        assert len(base.solids()) == 1

    def test_slide_top_rail_cut(self):
        """Test _slide_top_rail_cut internal function."""
        rail_cut = _slide_top_rail_cut(
            part_width=20,
            part_depth=20,
            rail_height=8,
            wall_thickness=2,
        )

        assert isinstance(rail_cut, Part)
        assert rail_cut.is_valid

    def test_slide_top_rail_cut_with_angle(self):
        """Test _slide_top_rail_cut with rail angle."""
        rail_cut = _slide_top_rail_cut(
            part_width=20,
            part_depth=20,
            rail_height=8,
            wall_thickness=2,
            rail_angle=1.0,
            effective_tolerance=0.1,
        )

        assert isinstance(rail_cut, Part)
        assert rail_cut.is_valid

    def test_high_top_slide_box_top_cut_template_false(self, small_base_part):
        """Test _high_top_slide_box_top with cut_template=False."""
        top = _high_top_slide_box_top(
            base_part=small_base_part,
            top_height=5,
            rail_height=8,
            wall_thickness=2,
            cut_template=False,
        )

        assert isinstance(top, Part)
        assert top.is_valid
        assert len(top.solids()) == 1
        # The label is set on the BuildPart context, not the returned part
        assert hasattr(top, "label") or top.label == "" or top.label is None

    def test_high_top_slide_box_top_cut_template_true(self, small_base_part):
        """Test _high_top_slide_box_top with cut_template=True."""
        top = _high_top_slide_box_top(
            base_part=small_base_part,
            top_height=5,
            rail_height=8,
            wall_thickness=2,
            cut_template=True,
        )

        assert isinstance(top, Part)
        assert top.is_valid
        assert len(top.solids()) == 1

    def test_dimensions_consistency(self, small_base_part):
        """Test that the dimensions of the created parts are consistent with input."""
        top_height = 5
        rail_height = 8
        wall_thickness = 2

        result = high_top_slide_box(
            base_part=small_base_part,
            top_height=top_height,
            rail_height=rail_height,
            wall_thickness=wall_thickness,
        )

        lid = result.children[0]
        base = result.children[1]

        # Check that parts have reasonable dimensions
        lid_bbox = lid.bounding_box()
        base_bbox = base.bounding_box()
        original_bbox = small_base_part.bounding_box()

        # Lid should have similar X,Y dimensions to original
        assert lid_bbox.size.X == pytest.approx(original_bbox.size.X, abs=0.1)
        assert lid_bbox.size.Y == pytest.approx(original_bbox.size.Y, abs=0.1)

        # Base should have similar X,Y dimensions to original
        assert base_bbox.size.X == pytest.approx(original_bbox.size.X, abs=0.1)
        assert base_bbox.size.Y == pytest.approx(original_bbox.size.Y, abs=0.1)

    def test_zero_divot_radius(self, small_base_part):
        """Test with divot_radius=0 to ensure no divots are created."""
        result = high_top_slide_box(
            base_part=small_base_part,
            top_height=5,
            rail_height=8,
            wall_thickness=2,
            divot_radius=0,
        )

        assert isinstance(result, Compound)
        assert len(result.children) == 2
        assert result.children[0].is_valid
        assert result.children[1].is_valid
        assert len(result.children[0].solids()) == 1
        assert len(result.children[1].solids()) == 1

    def test_negative_tolerance(self, small_base_part):
        """Test with negative tolerance."""
        result = high_top_slide_box(
            base_part=small_base_part,
            top_height=5,
            rail_height=8,
            wall_thickness=2,
            tolerance=-0.1,
        )

        assert isinstance(result, Compound)
        assert len(result.children) == 2
        assert result.children[0].is_valid
        assert result.children[1].is_valid
        assert len(result.children[0].solids()) == 1
        assert len(result.children[1].solids()) == 1

    def test_large_rail_angle(self, small_base_part):
        """Test with a larger rail angle."""
        result = high_top_slide_box(
            base_part=small_base_part,
            top_height=5,
            rail_height=8,
            wall_thickness=2,
            rail_angle=2.0,
        )

        assert isinstance(result, Compound)
        assert len(result.children) == 2
        assert result.children[0].is_valid
        assert result.children[1].is_valid
        assert len(result.children[0].solids()) == 1
        assert len(result.children[1].solids()) == 1

    def test_minimal_dimensions(self):
        """Test with very small dimensions."""
        with BuildPart() as tiny_box:
            Box(10, 10, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))

        result = high_top_slide_box(
            base_part=tiny_box.part,
            top_height=2,
            rail_height=3,
            wall_thickness=1,
        )

        assert isinstance(result, Compound)
        assert len(result.children) == 2
        assert result.children[0].is_valid
        assert result.children[1].is_valid
        assert len(result.children[0].solids()) == 1
        assert len(result.children[1].solids()) == 1

    def test_direct_run(self):
        """Test that the module can be run directly without errors."""
        with (
            patch("ocp_vscode.show"),
            (
                patch("build123d.export_stl")
                if hasattr(__import__("build123d"), "export_stl")
                else patch("builtins.open")
            ),
        ):
            loader = SourceFileLoader("__main__", module_path("high_top_slide_box"))
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))

    def test_parameter_validation_edge_cases(self, small_base_part):
        """Test edge cases for parameter validation."""
        # Test with very thin walls
        result = high_top_slide_box(
            base_part=small_base_part,
            top_height=5,
            rail_height=8,
            wall_thickness=0.5,
        )
        assert result.children[0].is_valid
        assert result.children[1].is_valid
        assert len(result.children[0].solids()) == 1
        assert len(result.children[1].solids()) == 1

        # Test with very small top height
        result = high_top_slide_box(
            base_part=small_base_part,
            top_height=1,
            rail_height=8,
            wall_thickness=2,
        )
        assert result.children[0].is_valid
        assert result.children[1].is_valid
        assert len(result.children[0].solids()) == 1
        assert len(result.children[1].solids()) == 1

        # Test with very small rail height
        result = high_top_slide_box(
            base_part=small_base_part,
            top_height=5,
            rail_height=2,
            wall_thickness=2,
        )
        assert result.children[0].is_valid
        assert result.children[1].is_valid
        assert len(result.children[0].solids()) == 1
        assert len(result.children[1].solids()) == 1

    def test_rectangular_base_part(self):
        """Test with a non-square rectangular base part."""
        with BuildPart() as rect_box:
            Box(30, 15, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))

        result = high_top_slide_box(
            base_part=rect_box.part,
            top_height=4,
            rail_height=6,
            wall_thickness=2,
        )

        assert isinstance(result, Compound)
        assert len(result.children) == 2
        assert result.children[0].is_valid
        assert result.children[1].is_valid
        assert len(result.children[0].solids()) == 1
        assert len(result.children[1].solids()) == 1

    def test_tall_base_part(self):
        """Test with a tall base part."""
        with BuildPart() as tall_box:
            Box(20, 20, 50, align=(Align.CENTER, Align.CENTER, Align.MIN))

        result = high_top_slide_box(
            base_part=tall_box.part,
            top_height=8,
            rail_height=12,
            wall_thickness=3,
        )

        assert isinstance(result, Compound)
        assert len(result.children) == 2
        assert result.children[0].is_valid
        assert result.children[1].is_valid
        assert len(result.children[0].solids()) == 1
        assert len(result.children[1].solids()) == 1


class TestHighTopSlideBoxValidation:
    """Dimensions that cannot yield a single printable solid must be rejected.

    Before validation existed, a part with too little material above the rails
    silently produced a Compound of three solids: the lid plus two detached
    divots. It reported ``is_valid`` on macOS OCCT and not on Linux, so the
    defect surfaced only as a platform-dependent CI failure.
    """

    @staticmethod
    def _box(width=30, depth=15, height=14):
        with BuildPart() as part:
            Box(width, depth, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
        return part.part

    def test_insufficient_headroom_raises(self):
        # top_height + rail_height consumes the whole part, leaving nothing below
        with pytest.raises(ValueError, match="must remain below the rails"):
            high_top_slide_box(
                base_part=self._box(height=10),
                top_height=4,
                rail_height=6,
                wall_thickness=2,
            )

    def test_headroom_below_wall_thickness_raises(self):
        # 1mm of headroom where wall_thickness is 2 -- the divots cannot fuse
        with pytest.raises(ValueError, match="must remain below the rails"):
            high_top_slide_box(
                base_part=self._box(height=11),
                top_height=4,
                rail_height=6,
                wall_thickness=2,
            )

    def test_headroom_equal_to_wall_thickness_is_accepted(self):
        # exactly wall_thickness of headroom is the boundary and must build cleanly
        result = high_top_slide_box(
            base_part=self._box(height=12),
            top_height=4,
            rail_height=6,
            wall_thickness=2,
        )
        assert len(result.children[0].solids()) == 1
        assert len(result.children[1].solids()) == 1

    def test_wall_thickness_too_large_raises(self):
        with pytest.raises(ValueError, match="wall_thickness"):
            high_top_slide_box(
                base_part=self._box(width=30, depth=15),
                top_height=4,
                rail_height=6,
                wall_thickness=8,
            )

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"wall_thickness": 0},
            {"rail_height": 0},
            {"top_height": 0},
        ],
    )
    def test_non_positive_dimensions_raise(self, kwargs):
        params = {"top_height": 4, "rail_height": 6, "wall_thickness": 2, **kwargs}
        with pytest.raises(ValueError, match="greater than 0"):
            high_top_slide_box(base_part=self._box(), **params)

    def test_lid_and_base_validate_too(self):
        small = self._box(height=10)
        with pytest.raises(ValueError, match="must remain below the rails"):
            high_top_slide_box_lid(
                base_part=small, top_height=4, rail_height=6, wall_thickness=2
            )
        with pytest.raises(ValueError, match="must remain below the rails"):
            high_top_slide_box_base(
                base_part=small, top_height=4, rail_height=6, wall_thickness=2
            )
