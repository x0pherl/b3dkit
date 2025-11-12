from build123d import (
    Align,
    Axis,
    BasePartObject,
    Box,
    BuildPart,
    Builder,
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
    validate_inputs,
)
from math import atan, degrees, tan, radians
from ocp_vscode import show, Camera


def anti_chamfer(
    face: Face | Iterable[Face],
    length: float,
    length2: float | None = None,
) -> Part:
    faces_list = flatten_sequence(face)
    if len(faces_list) == 0:
        raise ValueError("No faces provided to anti_chamfer")
    if not all([isinstance(obj, Face) for obj in faces_list]):
        raise ValueError("anti_chamfer operation takes only Faces")

    context: Builder | None = Builder._get_context("chamfer")
    validate_inputs(context, "chamfer", faces_list)

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
