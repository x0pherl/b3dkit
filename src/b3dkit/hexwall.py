"""
HexWall

name: hexwall.py
by:   x0pherl
date: Jan 19th 2025

desc:
    This build123d python module creates a hexagonal pattern within a box, resulting
    in a grid of hexagons.
"""

from math import sqrt
from typing import Union

from build123d import (
    Align,
    Axis,
    BasePartObject,
    Box,
    BuildPart,
    BuildSketch,
    HexLocations,
    Mode,
    Part,
    RegularPolygon,
    RotationLike,
    extrude,
    tuplify,
)
from ocp_vscode import Camera, show


class HexWall(BasePartObject):

    def __init__(
        self,
        length: float,
        width: float,
        height: float,
        apothem: float,
        wall_thickness: float,
        inverse=False,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        Part Object: hexwall
        -------
        arguments:
            - length (float): box size
            - width (float): box size
            - height (float): box size
            - apothem (float): the distance between two paralel edges of the hexagon
            - rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
            - align (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
                or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
            - mode (Mode, optional): combine mode. Defaults to Mode.ADD
        """
        with BuildPart() as wall:
            hexwall_radius = 2 * sqrt(3) / 3 * apothem
            hexwall_xcount = int(length // ((sqrt(3) / 2 * apothem) / 2)) + 2
            if hexwall_xcount % 2 == 0:
                hexwall_xcount += 1
            Box(length=length, width=width, height=height, align=tuplify(align, 3))
            combine_mode = Mode.INTERSECT if inverse else Mode.SUBTRACT
            with BuildPart(mode=combine_mode):
                with BuildSketch(wall.faces().sort_by(Axis.Z)[0]) as sk:
                    with HexLocations(
                        radius=hexwall_radius,
                        x_count=hexwall_xcount,
                        y_count=int(width // apothem / 2) + 2,
                        align=(Align.CENTER, Align.CENTER),
                    ):
                        RegularPolygon(
                            radius=2 * sqrt(3) / 3 * (apothem - wall_thickness / 2),
                            major_radius=False,
                            side_count=6,
                        )
                extrude(sk.sketch, -height)
        part = wall.part
        part.label = "hexwall"

        super().__init__(
            part=part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


if __name__ == "__main__":
    show(
        HexWall(
            width=20,
            length=40,
            height=2,
            apothem=9,
            wall_thickness=2,
            inverse=True,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ),
        reset_camera=Camera.KEEP,
    )
