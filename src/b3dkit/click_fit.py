"""
click_fit.py allows for the creation of a preciscely fitting
snap fit connector that is easier to assemble and slower to
wear out than a simple half sphere.
"""

from typing import Union
from build123d import (
    Align,
    Axis,
    BasePartObject,
    BuildPart,
    BuildSketch,
    Circle,
    Mode,
    Part,
    Plane,
    RotationLike,
    chamfer,
    extrude,
    loft,
    tuplify,
)

from ocp_vscode import show, Camera


class Divot(BasePartObject):

    def __init__(
        self,
        radius: float = 0.5,
        positive: bool = True,
        extend_base=False,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """Part Object: Divot
        Create a divot that can be used to create a snap fit connector for 3d printing.
        ----------
        Arguments:
            - radius: float
                The radius of the divot.
            - positive: bool
                when True, reduces the size and shaping of the divot
                for the extruded part. when False, deepens and widens the socket.
            - extend_base: bool
                when True, extends the base of the divot to allow for a clean
                connection when attaching without precise placement.
            - rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
            - align (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
                or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
            - mode (Mode, optional): combine mode. Defaults to Mode.ADD
        """

        tolerance = 0 if not positive else radius * 0.05
        ratio = 0.5 if positive else 0.55
        with BuildPart() as divot_part:
            with BuildSketch():
                Circle(radius - tolerance)
            with BuildSketch(Plane.XY.offset(radius * ratio)) as sketch:
                Circle(radius * ratio)
            loft()
            chamfer(divot_part.part.faces().sort_by(Axis.Z)[-1].edges(), radius * 0.1)
            if extend_base:
                extrude(divot_part.part.faces().sort_by(Axis.Z)[0], radius)
        super().__init__(
            divot_part.part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


if __name__ == "__main__":
    show(
        Divot(10, extend_base=True),
        Divot(10, positive=False),
        reset_camera=Camera.KEEP,
    )
