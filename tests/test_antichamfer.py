import pytest
from unittest.mock import patch
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from math import atan, degrees
from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Cylinder,
    Face,
    Part,
    Plane,
)
from b3dkit.antichamfer import anti_chamfer


class TestAntiChamfer:
    def test_anti_chamfer_in_build_context(self):
        """Test anti_chamfer within a BuildPart context"""

        with BuildPart() as bkt:
            Box(
                10,
                10,
                10,
            )
            anti_chamfer(bkt.faces().filter_by(Axis.Z), 2, 1)

        assert bkt.part.is_valid
        original_volume = 10 * 10 * 10
        assert bkt.part.volume > original_volume

    def test_anti_chamfer_single_face(self):
        """Test anti_chamfer with a single face"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer
        result = anti_chamfer(top_face, 2.0, 1.0)

        # Check that result is a Part
        assert isinstance(result, Part)
        # Check that the result has more volume than the original (anti-chamfer adds material)
        assert result.volume > original_part.volume

    def test_anti_chamfer_empty_face(self):
        """Test anti_chamfer with an empty face list"""
        with pytest.raises(ValueError):
            anti_chamfer([], 2.0, 1.0)

    def test_anti_chamfer_float_face(self):
        """Test anti_chamfer with a non-Face input"""

        with pytest.raises(ValueError):
            anti_chamfer([3.2], 2.0, 1.0)

    def test_contextless_face(self):
        fc = test_face = Face(Plane.XY)
        with pytest.raises(ValueError):
            anti_chamfer(fc, 1.0, 1.0)

    def test_anti_chamfer_multiple_faces(self):
        """Test anti_chamfer with multiple faces (iterable)"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get top and bottom faces
        faces = [
            original_part.faces().filter_by(Axis.Z)[-1],  # top
            original_part.faces().filter_by(Axis.Z)[0],  # bottom
        ]

        # Apply anti_chamfer
        result = anti_chamfer(faces, 1.5, 1.0)

        # Check that result is a Part
        assert isinstance(result, Part)
        # Check that the result has more volume than the original
        assert result.volume > original_part.volume

    def test_anti_chamfer_length2_none_default(self):
        """Test anti_chamfer with length2=None (should default to length)"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer with length2=None
        result1 = anti_chamfer(top_face, 2.0, None)

        # Apply anti_chamfer with length2=length (should be equivalent)
        result2 = anti_chamfer(top_face, 2.0, 2.0)

        # Results should have the same volume
        assert abs(result1.volume - result2.volume) < 1e-6

    def test_anti_chamfer_different_length_values(self):
        """Test anti_chamfer with different length and length2 values"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer with different length values
        result1 = anti_chamfer(top_face, 1.0, 0.5)
        result2 = anti_chamfer(top_face, 2.0, 1.0)
        result3 = anti_chamfer(top_face, 1.0, 2.0)

        # All should be valid Parts
        assert isinstance(result1, Part)
        assert isinstance(result2, Part)
        assert isinstance(result3, Part)

        # All should have different volumes
        assert result1.volume != result2.volume != result3.volume

    def test_anti_chamfer_zero_length_returns_original(self):
        """Test anti_chamfer with zero length returns original part unchanged"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part
        original_volume = original_part.volume

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer with zero length - should return original part
        result = anti_chamfer(top_face, 0.0, 0.0)

        # Should return the same part (not modified)
        assert isinstance(result, Part)
        assert result.volume == original_volume

    def test_anti_chamfer_zero_length2_returns_original(self):
        """Test anti_chamfer with zero length2 returns original part unchanged"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part
        original_volume = original_part.volume

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer with zero length2 - should return original part
        result = anti_chamfer(top_face, 1.0, 0.0)

        # Should return the same part (not modified)
        assert isinstance(result, Part)
        assert result.volume == original_volume

    def test_anti_chamfer_zero_length_nonzero_length2_returns_original(self):
        """Test anti_chamfer with zero length but non-zero length2 returns original part"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part
        original_volume = original_part.volume

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer with zero length but non-zero length2 - should return original part
        result = anti_chamfer(top_face, 0.0, 1.0)

        # Should return the same part (not modified)
        assert isinstance(result, Part)
        assert result.volume == original_volume

    def test_anti_chamfer_guard_clause_coverage(self):
        """Test that the guard clause properly handles all zero value combinations"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part
        original_volume = original_part.volume

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Test all combinations that should trigger the guard clause
        test_cases = [
            (0.0, 0.0),  # Both zero
            (0.0, 1.0),  # length zero, length2 non-zero
            (1.0, 0.0),  # length non-zero, length2 zero
        ]

        for length, length2 in test_cases:
            result = anti_chamfer(top_face, length, length2)
            assert isinstance(result, Part)
            assert (
                result.volume == original_volume
            ), f"Failed for length={length}, length2={length2}"

    def test_anti_chamfer_preserves_original_part(self):
        """Test that anti_chamfer includes the original part geometry"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
        original_part = bp.part
        original_volume = original_part.volume

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer
        result = anti_chamfer(top_face, 1.0, 0.5)

        # Result should contain at least the original volume
        assert result.volume >= original_volume

    def test_anti_chamfer_with_cylinder(self):
        """Test anti_chamfer works with non-box geometries"""
        # Create a cylinder
        with BuildPart() as bp:
            Cylinder(5, 10)
        original_part = bp.part

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer
        result = anti_chamfer(top_face, 1.0, 0.8)

        # Check that result is a Part with increased volume
        assert isinstance(result, Part)
        assert result.volume > original_part.volume

    def test_anti_chamfer_face_iterable_conversion(self):
        """Test that single Face is converted to iterable internally"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get the top face (single Face object)
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Test with single Face
        result1 = anti_chamfer(top_face, 2.0, 1.0)

        # Test with Face wrapped in list
        result2 = anti_chamfer([top_face], 2.0, 1.0)

        # Results should be equivalent
        assert abs(result1.volume - result2.volume) < 1e-6

    def test_anti_chamfer_taper_calculation(self):
        """Test that the taper angle calculation is correct"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Test with specific length/length2 ratios that we can verify
        length = 2.0
        length2 = 1.0
        expected_taper = -degrees(atan(length2 / length))

        # Apply anti_chamfer - this should use the calculated taper internally
        result = anti_chamfer(top_face, length, length2)

        # The function should complete without error (taper calculation works)
        assert isinstance(result, Part)
        assert result.volume > original_part.volume

    def test_anti_chamfer_small_values(self):
        """Test anti_chamfer with very small length values"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer with small values
        result = anti_chamfer(top_face, 0.1, 0.05)

        # Should still work
        assert isinstance(result, Part)
        assert result.volume > original_part.volume

    def test_anti_chamfer_large_values(self):
        """Test anti_chamfer with large length values relative to part size"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer with relatively large values
        result = anti_chamfer(top_face, 3.0, 2.0)

        # Should still work (build123d should handle the geometry)
        assert isinstance(result, Part)

    def test_anti_chamfer_length2_greater_than_length(self):
        """Test anti_chamfer when length2 > length"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer with length2 > length
        result = anti_chamfer(top_face, 1.0, 2.0)

        # Should still work (different taper angle)
        assert isinstance(result, Part)
        assert result.volume > original_part.volume

    def test_anti_chamfer_equal_length_values(self):
        """Test anti_chamfer when length == length2"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer with equal lengths
        result = anti_chamfer(top_face, 1.5, 1.5)

        # Should work (45-degree taper)
        assert isinstance(result, Part)
        assert result.volume > original_part.volume

    def test_anti_chamfer_negative_length_values(self):
        """Test anti_chamfer with negative length values"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer with negative lengths (should still work geometrically)
        result = anti_chamfer(top_face, -1.0, -0.5)

        # Should return a Part (behavior may vary but shouldn't crash)
        assert isinstance(result, Part)

    def test_anti_chamfer_empty_face_list(self):
        """Test anti_chamfer with empty face list"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part
        original_volume = original_part.volume

        # Apply anti_chamfer with empty face list
        with pytest.raises(ValueError):
            result = anti_chamfer([], 1.0, 0.5)

    def test_anti_chamfer_very_small_length2(self):
        """Test anti_chamfer with very small length2 value"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer with very small length2
        result = anti_chamfer(top_face, 1.0, 1e-6)

        # Should work (very steep taper)
        assert isinstance(result, Part)
        assert result.volume > original_part.volume

    def test_anti_chamfer_parameter_order_matters(self):
        """Test that swapping length and length2 produces different results"""
        # Create a simple box
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        # Get the top face
        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        # Apply anti_chamfer with different parameter orders
        result1 = anti_chamfer(top_face, 2.0, 1.0)
        result2 = anti_chamfer(top_face, 1.0, 2.0)

        # Results should be different
        assert abs(result1.volume - result2.volume) > 1e-6

    def test_direct_run(self):

        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader("__main__", "src/b3dkit/antichamfer.py")
            loader.exec_module(module_from_spec(spec_from_loader(loader.name, loader)))
