from math import atan, degrees

from build123d import (
    Align,
    Axis,
    BasePartObject,
    Box,
    Builder,
    BuildPart,
    Compound,
    Face,
    Iterable,
    Location,
    Mode,
    Part,
    add,
    extrude,
    fillet,
    flatten_sequence,
)

__all__ = [
    "anti_chamfer",
]


def anti_chamfer(
    face: Face | Iterable[Face],
    length: float,
    length2: float | None = None,
) -> Part:
    """extrude the given faces outward with a taper, the inverse of a chamfer

    Applies to BuildPart only. Inside a builder the context object is replaced
    with the result, matching build123d's own chamfer, which likewise takes no
    mode argument.

    args:
        - face: the Face, or iterable of Faces, to extend
        - length: how far to extend, in mm
        - length2: the taper measured across the face, in mm; defaults to length

    raises ValueError if no Faces are given, if any object is not a Face, or if
    the faces do not belong to a Part
    raises RuntimeError if called inside a builder other than BuildPart
    """
    faces_list = flatten_sequence(face)
    if len(faces_list) == 0:
        raise ValueError("No faces provided to anti_chamfer")
    if not all([isinstance(obj, Face) for obj in faces_list]):
        raise ValueError("anti_chamfer operation takes only Faces")

    # Check the builder directly rather than routing through
    # validate_inputs(context, "chamfer", ...). That looked anti_chamfer up in
    # build123d's operations_apply_to table under chamfer's name, which is a
    # table b3dkit does not own and, worse, a looser contract: chamfer applies
    # to BuildSketch and BuildLine, where anti_chamfer's extrude() cannot work.
    # Borrowing it let anti_chamfer run inside a BuildSketch and quietly do the
    # wrong thing instead of refusing.
    context: Builder | None = Builder._get_context("anti_chamfer")
    if context is not None and not isinstance(context, BuildPart):
        raise RuntimeError(
            f"anti_chamfer applies to BuildPart, not {type(context).__name__}"
        )

    if length2 is None:
        length2 = length

    if context is not None:
        target = context._obj
    else:
        target = faces_list[0].topo_parent
    if target is None:
        raise ValueError("face does not seem to belong to a Part")
    # Convert BasePartObject in Part so casting into Part during construction works
    target = Part(target.wrapped) if isinstance(target, BasePartObject) else target

    if length == 0 or length2 == 0:
        return target

    with BuildPart() as new_part:
        add(target)
        for f in faces_list:
            extrude(
                f.offset(-length),
                amount=length,
                taper=-degrees(atan(length2 / length)),
            )
    if context is not None:
        context._add_to_context(
            Part(Compound([new_part.part]).wrapped), mode=Mode.REPLACE
        )
    return Part(Compound([new_part.part]).wrapped)


if __name__ == "__main__":
    from ocp_vscode import Camera, show

    with BuildPart(Location((33, 11, 0))) as bkt:
        Box(
            60,
            10,
            20,
            rotation=(0, 0, 45),
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        fillet(bkt.edges().filter_by(Axis.Z), 3)
        anti_chamfer(bkt.faces().filter_by(Axis.Z), 1, 1)
    show(bkt, reset_camera=Camera.KEEP)
