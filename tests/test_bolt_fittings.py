"""
Comprehensive tests for the bolt_fittings module.

These tests cover all functions and their parameters to ensure:
- Correct geometry creation
- Parameter variations and edge cases
- Return type validation
- Dimensional accuracy
- Mutation testing coverage
"""

from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from unittest.mock import patch
import pytest
from build123d import (
    Align,
    Axis,
    BuildPart,
    Part,
)
from b3dkit.bolt_fittings import (
    TeardropBoltCutSinkhole,
    ScrewCut,
    NutCut,
    BoltCutSinkhole,
    HeatsinkCut,
    SquareNutSinkhole,
)


class TestTeardropBoltCutSinkhole:
    def test_teardrop_bolt_cut_default_parameters(self):
        """Test teardrop bolt cut with default parameters"""
        result = TeardropBoltCutSinkhole()

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_teardrop_bolt_cut_custom_shaft(self):
        """Test teardrop bolt cut with custom shaft dimensions"""
        result = TeardropBoltCutSinkhole(shaft_radius=2.0, shaft_depth=5.0)

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_teardrop_bolt_cut_custom_head(self):
        """Test teardrop bolt cut with custom head dimensions"""
        result = TeardropBoltCutSinkhole(head_radius=4.0, head_depth=3.0)

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_teardrop_bolt_cut_with_chamfer(self):
        """Test teardrop bolt cut with various chamfer radii"""
        result1 = TeardropBoltCutSinkhole(chamfer_radius=0.5)
        result2 = TeardropBoltCutSinkhole(chamfer_radius=2.0)

        assert isinstance(result1, Part)
        assert isinstance(result2, Part)
        # Different chamfer radii should produce different volumes
        assert result1.volume != result2.volume

    def test_teardrop_bolt_cut_with_extension(self):
        """Test teardrop bolt cut with extension distance"""
        result_with = TeardropBoltCutSinkhole(extension_distance=50)
        result_without = TeardropBoltCutSinkhole(extension_distance=0)

        assert isinstance(result_with, Part)
        assert isinstance(result_without, Part)
        # With extension should have more volume
        assert result_with.volume > result_without.volume

    def test_teardrop_bolt_cut_zero_extension(self):
        """Test teardrop bolt cut with zero extension (blind hole)"""
        result = TeardropBoltCutSinkhole(extension_distance=0)

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_teardrop_bolt_cut_small_dimensions(self):
        """Test teardrop bolt cut with small dimensions"""
        result = TeardropBoltCutSinkhole(
            shaft_radius=0.5,
            shaft_depth=1.0,
            head_radius=1.0,
            head_depth=1.5,
            chamfer_radius=0.2,
        )

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_teardrop_bolt_cut_large_dimensions(self):
        """Test teardrop bolt cut with large dimensions"""
        result = TeardropBoltCutSinkhole(
            shaft_radius=5.0,
            shaft_depth=10.0,
            head_radius=8.0,
            head_depth=8.0,
            chamfer_radius=2.0,
        )

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_teardrop_bolt_cut_head_larger_than_shaft(self):
        """Test that head radius is larger than shaft radius"""
        result = TeardropBoltCutSinkhole(shaft_radius=1.5, head_radius=3.0)

        assert isinstance(result, Part)
        # Head should create additional volume beyond shaft
        assert result.volume > 0

    def test_teardrop_bolt_cut_parameter_combinations(self):
        """Test various parameter combinations"""
        combinations = [
            (1.0, 2.0, 2.0, 3.0, 0.5, 10),
            (2.0, 3.0, 4.0, 5.0, 1.0, 50),
            (1.65, 2.0, 3.1, 5.0, 1.0, 100),
        ]

        for shaft_r, shaft_d, head_r, head_d, chamfer_r, ext in combinations:
            result = TeardropBoltCutSinkhole(
                shaft_radius=shaft_r,
                shaft_depth=shaft_d,
                head_radius=head_r,
                head_depth=head_d,
                chamfer_radius=chamfer_r,
                extension_distance=ext,
            )
            assert isinstance(result, Part)
            assert result.volume > 0

    def test_teardrop_bolt_cut_custom_teardrop_ratio(self):
        """Test teardrop bolt cut with custom teardrop_ratio"""
        result1 = TeardropBoltCutSinkhole(teardrop_ratio=1.0)  # Cylindrical
        result2 = TeardropBoltCutSinkhole(teardrop_ratio=1.1)  # Default teardrop
        result3 = TeardropBoltCutSinkhole(
            teardrop_ratio=1.2
        )  # More pronounced teardrop

        assert isinstance(result1, Part)
        assert isinstance(result2, Part)
        assert isinstance(result3, Part)
        # Larger ratios should produce larger volumes
        assert result1.volume < result2.volume < result3.volume

    def test_teardrop_bolt_cut_ratio_1_0_equals_cylindrical(self):
        """Test that teardrop_ratio=1.0 produces same result as BoltCutSinkhole"""
        params = {
            "shaft_radius": 1.65,
            "shaft_depth": 2.0,
            "head_radius": 3.1,
            "head_depth": 5.0,
            "chamfer_radius": 1.0,
            "extension_distance": 10.0,
        }

        teardrop_result = TeardropBoltCutSinkhole(**params, teardrop_ratio=1.0)
        bolt_result = BoltCutSinkhole(**params)

        # Should have identical volumes
        assert abs(teardrop_result.volume - bolt_result.volume) < 1e-6

    def test_teardrop_bolt_cut_ratio_variations(self):
        """Test that different teardrop ratios produce different volumes"""
        base_params = {
            "shaft_radius": 1.65,
            "shaft_depth": 2.0,
            "head_radius": 3.1,
            "head_depth": 5.0,
            "chamfer_radius": 1.0,
            "extension_distance": 10.0,
        }

        ratios = [1.0, 1.05, 1.1, 1.15, 1.2]
        results = [
            TeardropBoltCutSinkhole(**base_params, teardrop_ratio=r) for r in ratios
        ]

        # Each result should be valid
        for result in results:
            assert isinstance(result, Part)
            assert result.volume > 0

        # Volumes should increase with ratio
        for i in range(len(results) - 1):
            assert results[i].volume < results[i + 1].volume


class TestBoltCutSinkhole:
    def test_bolt_cut_default_parameters(self):
        """Test bolt cut with default parameters"""
        result = BoltCutSinkhole()

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_bolt_cut_custom_shaft(self):
        """Test bolt cut with custom shaft dimensions"""
        result = BoltCutSinkhole(shaft_radius=2.0, shaft_depth=5.0)

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_bolt_cut_custom_head(self):
        """Test bolt cut with custom head dimensions"""
        result = BoltCutSinkhole(head_radius=4.0, head_depth=3.0)

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_bolt_cut_with_chamfer(self):
        """Test bolt cut with various chamfer radii"""
        result1 = BoltCutSinkhole(chamfer_radius=0.5)
        result2 = BoltCutSinkhole(chamfer_radius=2.0)

        assert isinstance(result1, Part)
        assert isinstance(result2, Part)
        # Different chamfer radii should produce different volumes
        assert result1.volume != result2.volume

    def test_bolt_cut_with_extension(self):
        """Test bolt cut with extension distance"""
        result_with = BoltCutSinkhole(extension_distance=50)
        result_without = BoltCutSinkhole(extension_distance=0)

        assert isinstance(result_with, Part)
        assert isinstance(result_without, Part)
        # With extension should have more volume
        assert result_with.volume > result_without.volume

    def test_bolt_cut_zero_extension(self):
        """Test bolt cut with zero extension (blind hole)"""
        result = BoltCutSinkhole(extension_distance=0)

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_bolt_cut_small_dimensions(self):
        """Test bolt cut with small dimensions"""
        result = BoltCutSinkhole(
            shaft_radius=0.5,
            shaft_depth=1.0,
            head_radius=1.0,
            head_depth=1.5,
            chamfer_radius=0.2,
        )

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_bolt_cut_large_dimensions(self):
        """Test bolt cut with large dimensions"""
        result = BoltCutSinkhole(
            shaft_radius=5.0,
            shaft_depth=10.0,
            head_radius=8.0,
            head_depth=8.0,
            chamfer_radius=2.0,
        )

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_bolt_cut_vs_teardrop(self):
        """Test that bolt_cut and TeardropBoltCutSinkhole with default ratio produce different results"""
        params = {
            "shaft_radius": 1.65,
            "shaft_depth": 2.0,
            "head_radius": 3.1,
            "head_depth": 5.0,
            "chamfer_radius": 1.0,
            "extension_distance": 10.0,
        }

        bolt_result = BoltCutSinkhole(**params)
        teardrop_result = TeardropBoltCutSinkhole(
            **params
        )  # Uses default teardrop_ratio=1.1

        # Teardrop with default ratio should have more volume than cylindrical
        assert isinstance(bolt_result, Part)
        assert isinstance(teardrop_result, Part)
        assert teardrop_result.volume > bolt_result.volume

    def test_bolt_cut_is_wrapper_for_teardrop(self):
        """Test that BoltCutSinkhole is a wrapper for TeardropBoltCutSinkhole with ratio=1.0"""
        params = {
            "shaft_radius": 2.0,
            "shaft_depth": 3.0,
            "head_radius": 4.0,
            "head_depth": 6.0,
            "chamfer_radius": 1.5,
            "extension_distance": 20.0,
        }

        bolt_result = BoltCutSinkhole(**params)
        teardrop_result = TeardropBoltCutSinkhole(**params, teardrop_ratio=1.0)

        # Should produce identical results
        assert isinstance(bolt_result, Part)
        assert isinstance(teardrop_result, Part)
        assert abs(bolt_result.volume - teardrop_result.volume) < 1e-6

    def test_bolt_cut_parameter_combinations(self):
        """Test various parameter combinations"""
        combinations = [
            (1.0, 2.0, 2.0, 3.0, 0.5, 10),
            (2.0, 3.0, 4.0, 5.0, 1.0, 50),
            (1.65, 2.0, 3.1, 5.0, 1.0, 100),
        ]

        for shaft_r, shaft_d, head_r, head_d, chamfer_r, ext in combinations:
            result = BoltCutSinkhole(
                shaft_radius=shaft_r,
                shaft_depth=shaft_d,
                head_radius=head_r,
                head_depth=head_d,
                chamfer_radius=chamfer_r,
                extension_distance=ext,
            )
            assert isinstance(result, Part)
            assert result.volume > 0


class TestSquareNutSinkhole:
    def test_square_nut_default_parameters(self):
        """Test square nut sinkhole with default parameters"""
        result = SquareNutSinkhole()

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_square_nut_custom_bolt(self):
        """Test square nut sinkhole with custom bolt dimensions"""
        result = SquareNutSinkhole(bolt_radius=2.0, bolt_depth=5.0)

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_square_nut_custom_nut(self):
        """Test square nut sinkhole with custom nut dimensions"""
        result = SquareNutSinkhole(nut_height=3.0, nut_legnth=7.0, nut_depth=50.0)

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_square_nut_with_extension(self):
        """Test square nut sinkhole with bolt extension"""
        result_with = SquareNutSinkhole(bolt_extension=5)
        result_without = SquareNutSinkhole(bolt_extension=0)

        assert isinstance(result_with, Part)
        assert isinstance(result_without, Part)
        # With extension should have more volume
        assert result_with.volume > result_without.volume

    def test_square_nut_zero_extension(self):
        """Test square nut sinkhole with zero extension"""
        result = SquareNutSinkhole(bolt_extension=0)

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_square_nut_small_dimensions(self):
        """Test square nut sinkhole with small dimensions"""
        result = SquareNutSinkhole(
            bolt_radius=0.5,
            bolt_depth=1.0,
            nut_height=1.0,
            nut_legnth=3.0,
            nut_depth=10.0,
            bolt_extension=0.5,
        )

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_square_nut_large_dimensions(self):
        """Test square nut sinkhole with large dimensions"""
        result = SquareNutSinkhole(
            bolt_radius=5.0,
            bolt_depth=10.0,
            nut_height=5.0,
            nut_legnth=15.0,
            nut_depth=200.0,
            bolt_extension=10.0,
        )

        assert isinstance(result, Part)
        assert result.volume > 0

    def test_square_nut_nut_larger_than_bolt(self):
        """Test that nut dimensions are larger than bolt"""
        result = SquareNutSinkhole(bolt_radius=1.5, nut_legnth=6.0)

        assert isinstance(result, Part)
        # Nut trap should add significant volume
        assert result.volume > 0

    def test_square_nut_different_nut_sizes(self):
        """Test with different nut sizes"""
        small_nut = SquareNutSinkhole(nut_legnth=4.0, nut_height=1.5)
        large_nut = SquareNutSinkhole(nut_legnth=8.0, nut_height=3.0)

        assert isinstance(small_nut, Part)
        assert isinstance(large_nut, Part)
        # Larger nut should have more volume
        assert large_nut.volume > small_nut.volume

    def test_square_nut_parameter_combinations(self):
        """Test various parameter combinations"""
        combinations = [
            (1.0, 2.0, 1.5, 4.0, 20, 0.5),
            (1.65, 2.0, 2.1, 5.6, 100, 1.0),
            (2.5, 3.0, 3.0, 8.0, 50, 2.0),
        ]

        for bolt_r, bolt_d, nut_h, nut_l, nut_d, bolt_ext in combinations:
            result = SquareNutSinkhole(
                bolt_radius=bolt_r,
                bolt_depth=bolt_d,
                nut_height=nut_h,
                nut_legnth=nut_l,
                nut_depth=nut_d,
                bolt_extension=bolt_ext,
            )
            assert isinstance(result, Part)
            assert result.volume > 0

    def test_square_nut_geometry_structure(self):
        """Test that square nut creates the expected geometry structure"""
        result = SquareNutSinkhole(
            bolt_radius=1.65,
            bolt_depth=2.0,
            nut_height=2.1,
            nut_legnth=5.6,
            nut_depth=10.0,
            bolt_extension=1.0,
        )

        assert isinstance(result, Part)
        # Should have multiple components (bolt hole + nut trap + optional extension)
        assert result.volume > 0

        # Check that geometry extends in Y direction (nut trap direction)
        bbox = result.bounding_box()
        assert bbox.size.Y > 0


class TestBoltFittingsIntegration:
    def test_all_functions_return_parts(self):
        """Test that all functions return valid Part objects"""
        teardrop = TeardropBoltCutSinkhole()
        bolt = BoltCutSinkhole()
        square = BoltCutSinkhole()

        assert isinstance(teardrop, Part)
        assert isinstance(bolt, Part)
        assert isinstance(square, Part)

    def test_consistent_sizing(self):
        """Test that similar dimensions produce similar results"""
        params = {
            "shaft_radius": 1.65,
            "shaft_depth": 2.0,
            "head_radius": 3.1,
            "head_depth": 5.0,
            "chamfer_radius": 1.0,
            "extension_distance": 0,
        }

        teardrop = TeardropBoltCutSinkhole(**params)  # Default ratio=1.1
        bolt = BoltCutSinkhole(**params)  # Equivalent to ratio=1.0

        # Teardrop with default 1.1 ratio should be slightly larger than cylindrical
        ratio = teardrop.volume / bolt.volume
        assert 1.0 < ratio < 1.3  # Teardrop has 1.1x multipliers

    def test_teardrop_ratio_parameter_independence(self):
        """Test that teardrop_ratio parameter works independently"""
        params = {
            "shaft_radius": 1.65,
            "shaft_depth": 2.0,
            "head_radius": 3.1,
            "head_depth": 5.0,
            "chamfer_radius": 1.0,
            "extension_distance": 10.0,
        }

        # Test that changing only teardrop_ratio changes volume
        result_low = TeardropBoltCutSinkhole(**params, teardrop_ratio=1.05)
        result_mid = TeardropBoltCutSinkhole(**params, teardrop_ratio=1.1)
        result_high = TeardropBoltCutSinkhole(**params, teardrop_ratio=1.15)

        # Volumes should increase with ratio
        assert result_low.volume < result_mid.volume < result_high.volume

    def test_volume_increases_with_dimensions(self):
        """Test that increasing dimensions increases volume"""
        small = BoltCutSinkhole(shaft_radius=1.0, head_radius=2.0)
        medium = BoltCutSinkhole(shaft_radius=2.0, head_radius=3.0)
        large = BoltCutSinkhole(shaft_radius=3.0, head_radius=4.0)

        assert small.volume < medium.volume < large.volume


class TestScrewCut:
    def test_screw_cut(self):
        screw = ScrewCut(5, 1, 2, 10, 10)
        assert screw.is_valid
        assert screw.bounding_box().size.X == pytest.approx(10)
        assert screw.bounding_box().size.Y == pytest.approx(10)
        assert screw.bounding_box().size.Z == pytest.approx(20)

    def test_nut_cut(self):
        nut = NutCut(5, 1, 2, 10)
        assert nut.is_valid

    def test_invalid_screw_cut(self):
        with pytest.raises(ValueError):
            ScrewCut(head_radius=5, shaft_radius=6)

    def test_heatsink_cut(self):
        heatsink = HeatsinkCut(10, 1, 5, 10)
        assert heatsink.is_valid
        assert heatsink.bounding_box().size.X == pytest.approx(20)
        assert heatsink.bounding_box().size.Y == pytest.approx(20)
        assert heatsink.bounding_box().size.Z == pytest.approx(11)


class TestBareExecution:
    def test_bare_execution(self):
        with (patch("ocp_vscode.show"),):
            loader = SourceFileLoader("__main__", "src/b3dkit/bolt_fittings.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))
