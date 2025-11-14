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
        sinkhole = TeardropBoltCutSinkhole()

        assert sinkhole.is_valid

    def test_teardrop_bolt_cut_custom_shaft(self):
        """Test teardrop bolt cut with custom shaft dimensions"""
        sinkhole = TeardropBoltCutSinkhole(shaft_radius=2.0, shaft_depth=5.0)

        assert sinkhole.is_valid

    def test_teardrop_bolt_cut_custom_head(self):
        """Test teardrop bolt cut with custom head dimensions"""
        sinkhole = TeardropBoltCutSinkhole(head_radius=4.0, head_depth=3.0)

        assert sinkhole.is_valid

    def test_teardrop_bolt_cut_with_chamfer(self):
        """Test teardrop bolt cut with various chamfer radii"""
        sinkhole1 = TeardropBoltCutSinkhole(chamfer_radius=0.5)
        sinkhole2 = TeardropBoltCutSinkhole(chamfer_radius=2.0)

        assert sinkhole1.volume != sinkhole2.volume

    def test_teardrop_bolt_cut_with_extension(self):
        """Test teardrop bolt cut with extension distance"""
        sinkhone_with = TeardropBoltCutSinkhole(extension_distance=50)
        sinkhone_without = TeardropBoltCutSinkhole(extension_distance=0)

        assert sinkhone_with.volume > sinkhone_without.volume

    def test_teardrop_bolt_cut_zero_extension(self):
        """Test teardrop bolt cut with zero extension (blind hole)"""
        sinkhone = TeardropBoltCutSinkhole(extension_distance=0)

        assert isinstance(sinkhone, Part)
        assert sinkhone.volume > 0

    def test_teardrop_bolt_cut_custom_teardrop_ratio(self):
        """Test teardrop bolt cut with custom teardrop_ratio"""
        boltcut1 = TeardropBoltCutSinkhole(teardrop_ratio=1.0)  # Cylindrical
        boltcut2 = TeardropBoltCutSinkhole(teardrop_ratio=1.1)  # Default teardrop
        boltcut3 = TeardropBoltCutSinkhole(
            teardrop_ratio=1.2
        )  # More pronounced teardrop

        assert isinstance(boltcut1, Part)
        assert isinstance(boltcut2, Part)
        assert isinstance(boltcut3, Part)
        # Larger ratios should produce larger volumes
        assert boltcut1.volume < boltcut2.volume < boltcut3.volume


class TestBoltCutSinkhole:
    def test_bolt_cut_default_parameters(self):
        """Test bolt cut with default parameters"""
        boltcut = BoltCutSinkhole()

        assert boltcut.is_valid

    def test_bolt_cut_with_chamfer(self):
        """Test bolt cut with various chamfer radii"""
        boltcut1 = BoltCutSinkhole(chamfer_radius=0.5)
        boltcut2 = BoltCutSinkhole(chamfer_radius=2.0)

        assert isinstance(boltcut1, Part)
        assert isinstance(boltcut2, Part)
        # Different chamfer radii should produce different volumes
        assert boltcut1.volume != boltcut2.volume

    def test_bolt_cut_with_extension(self):
        """Test bolt cut with extension distance"""
        boltcut_with = BoltCutSinkhole(extension_distance=50)
        boltcut_without = BoltCutSinkhole(extension_distance=0)

        assert boltcut_with.volume > boltcut_without.volume

    def test_bolt_cut_zero_extension(self):
        """Test bolt cut with zero extension (blind hole)"""
        boltcut = BoltCutSinkhole(extension_distance=0)

        assert boltcut.is_valid

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

        boltcut = BoltCutSinkhole(**params)
        teardropcut = TeardropBoltCutSinkhole(**params)

        # Teardrop with default ratio should have more volume than cylindrical
        assert boltcut.is_valid
        assert teardropcut.is_valid
        assert teardropcut.volume > boltcut.volume

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

        boltcut = BoltCutSinkhole(**params)
        teardropcut = TeardropBoltCutSinkhole(**params, teardrop_ratio=1.0)

        # Should produce identical results
        assert boltcut.is_valid
        assert teardropcut.is_valid
        assert abs(boltcut.volume - teardropcut.volume) < 1e-6


class TestSquareNutSinkhole:
    def test_square_nut_default_parameters(self):
        """Test square nut sinkhole with default parameters"""
        sinkhole = SquareNutSinkhole()

        assert sinkhole.is_valid

    def test_square_nut_with_extension(self):
        """Test square nut sinkhole with bolt extension"""
        sinkhole_with = SquareNutSinkhole(bolt_extension=5)
        sinkhole_without = SquareNutSinkhole(bolt_extension=0)

        assert sinkhole_with.volume > sinkhole_without.volume

    def test_square_nut_zero_extension(self):
        """Test square nut sinkhole with zero extension"""
        sinkhole = SquareNutSinkhole(bolt_extension=0)

        assert sinkhole.is_valid

    def test_square_nut_different_nut_sizes(self):
        """Test with different nut sizes"""
        small_nut = SquareNutSinkhole(nut_legnth=4.0, nut_height=1.5)
        large_nut = SquareNutSinkhole(nut_legnth=8.0, nut_height=3.0)

        assert isinstance(small_nut, Part)
        assert isinstance(large_nut, Part)
        # Larger nut should have more volume
        assert large_nut.volume > small_nut.volume


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
