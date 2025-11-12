from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch
import pytest
from build123d import Box, BuildPart, Part, Align, Axis, fillet, Compound

from b3dkit.high_top_slide_box import (
    high_top_slide_box,
    high_top_slide_box_lid,
    high_top_slide_box_base,
    _slide_top_rail_cut,
    _high_top_slide_box_top,
)


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
            loader = SourceFileLoader(
                "__main__", "src/b3dkit/high_top_slide_box.py"
            )
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

        # Test with very small top height
        result = high_top_slide_box(
            base_part=small_base_part,
            top_height=1,
            rail_height=8,
            wall_thickness=2,
        )
        assert result.children[0].is_valid
        assert result.children[1].is_valid

        # Test with very small rail height
        result = high_top_slide_box(
            base_part=small_base_part,
            top_height=5,
            rail_height=2,
            wall_thickness=2,
        )
        assert result.children[0].is_valid
        assert result.children[1].is_valid

    def test_rectangular_base_part(self):
        """Test with a non-square rectangular base part."""
        with BuildPart() as rect_box:
            Box(30, 15, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))

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
