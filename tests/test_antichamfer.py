import pytest
from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Cylinder,
    Face,
    Plane,
    Rectangle,
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
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        ac = anti_chamfer(top_face, 2.0, 1.0)

        assert ac.is_valid
        assert ac.volume > original_part.volume

    def test_anti_chamfer_empty_face(self):
        """Test anti_chamfer with an empty face list"""
        with pytest.raises(ValueError):
            anti_chamfer([], 2.0, 1.0)

    def test_anti_chamfer_float_face(self):
        """Test anti_chamfer with a non-Face input"""
        with pytest.raises(ValueError):
            anti_chamfer([3.2], 2.0, 1.0)

    def test_contextless_face(self):
        """Test anti_chamfer with a Face that has no context Part"""
        test_face = Face(Plane.XY)
        with pytest.raises(ValueError):
            anti_chamfer(test_face, 1.0, 1.0)

    def test_anti_chamfer_multiple_faces(self):
        """Test anti_chamfer with multiple faces (iterable)"""
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        ac = anti_chamfer(original_part.faces().filter_by(Axis.Z), 1.5, 1.0)
        assert ac.is_valid
        assert ac.volume > original_part.volume

    def test_anti_chamfer_length2_none_default(self):
        """Test anti_chamfer with length2=None (should default to length)"""
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        ac1 = anti_chamfer(top_face, 2.0, None)
        ac2 = anti_chamfer(top_face, 2.0, 2.0)

        assert pytest.approx(0) == abs(ac1.volume - ac2.volume)

    def test_anti_chamfer_different_length_values(self):
        """Test anti_chamfer with different length and length2 values"""
        with BuildPart() as bp:
            Box(10, 10, 10)
        original_part = bp.part

        top_face = original_part.faces().filter_by(Axis.Z)[-1]

        ac1 = anti_chamfer(top_face, 1.0, 0.5)
        ac2 = anti_chamfer(top_face, 2.0, 1.0)
        ac3 = anti_chamfer(top_face, 1.0, 2.0)

        assert ac1.is_valid
        assert ac2.is_valid
        assert ac3.is_valid

        assert ac1.volume != ac2.volume != ac3.volume

    def test_anti_chamfer_with_cylinder(self):
        """Test anti_chamfer works with a round face"""
        with BuildPart() as bp:
            Cylinder(5, 10)
        original_part = bp.part

        ac_part = anti_chamfer(bp.part.faces().filter_by(Axis.Z)[-1], 1.0, 0.8)

        assert ac_part.is_valid
        assert ac_part.volume > original_part.volume

    def test_anti_chamfer_negative_length_values(self):
        """Test anti_chamfer with negative length values"""
        with BuildPart() as bp:
            Box(10, 10, 10)

        ac_part = anti_chamfer(bp.part.faces().filter_by(Axis.Z)[-1], -1.0, -0.5)
        assert ac_part.is_valid

    def test_anti_chamfer_zero_length_values(self):
        """Test anti_chamfer with negative length values"""
        with BuildPart() as bp:
            Box(10, 10, 10)

        ac1 = anti_chamfer(bp.part.faces().filter_by(Axis.Z)[-1], 1, 0)
        ac2 = anti_chamfer(bp.part.faces().filter_by(Axis.Z)[-1], 0, 1)

        assert ac1.is_valid
        assert ac2.is_valid
        assert bp.part.volume == ac1.volume == ac2.volume


class TestAntiChamferBuilderContract:
    """anti_chamfer applies to BuildPart only, and must say so.

    It previously identified itself as "chamfer" to build123d's
    operations_apply_to table. That table is not b3dkit's to use, and chamfer's
    entry is a looser contract than anti_chamfer can honour: chamfer applies to
    BuildSketch and BuildLine, where anti_chamfer's extrude() cannot work.
    Borrowing it meant a call inside a BuildSketch completed silently instead of
    being refused.
    """

    def test_rejects_build_sketch(self):
        with BuildSketch() as sketch:
            Rectangle(10, 10)
            with pytest.raises(RuntimeError, match="applies to BuildPart"):
                anti_chamfer(sketch.sketch.faces(), 1, 1)

    def test_accepts_build_part(self):
        with BuildPart() as part:
            Box(60, 10, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
            before = part.part.volume
            anti_chamfer(part.faces().filter_by(Axis.Z), 1, 1)
        assert part.part.is_valid
        assert part.part.volume > before

    def test_works_outside_any_builder(self):
        with BuildPart() as part:
            Box(60, 10, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
        result = anti_chamfer(part.part.faces().filter_by(Axis.Z), 1, 1)
        assert result.is_valid
        assert result.volume > part.part.volume

    def test_does_not_use_build123d_private_dispatch_table(self):
        """The fix is only real if the borrowed name is gone from the source."""
        import inspect

        import b3dkit.antichamfer as module

        source = inspect.getsource(module.anti_chamfer)
        code = "\n".join(
            line for line in source.splitlines() if not line.strip().startswith("#")
        )
        assert "validate_inputs" not in code
        assert '"chamfer"' not in code
