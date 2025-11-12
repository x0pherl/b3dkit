"""

Twist & Snap Connector

name: twist_snap.py
by:   x0pherl
date: May 19 2024

desc: A parameterized twist and snap fitting.

license:

license:

    Copyright 2024 x0pherl

    Use of this source code is governed by an MIT-style
    license that can be found in the LICENSE file or at
    https://opensource.org/licenses/MIT.

"""

from dataclasses import dataclass
from enum import Enum, Flag, auto
from math import radians, cos, sin
from typing import Union

from build123d import (
    Align,
    Axis,
    BasePartObject,
    BuildPart,
    BuildSketch,
    Compound,
    Cylinder,
    GeomType,
    Location,
    Locations,
    Mode,
    PolarLocations,
    Polygon,
    RotationLike,
    SortBy,
    add,
    fillet,
    sweep,
    tuplify,
)

from ocp_vscode import Camera, show


class TwistSnapConnector(BasePartObject):

    def __init__(
        self,
        connector_radius: float = 4.5,
        tolerance: float = 0.12,
        arc_percentage: float = 10,
        snapfit_count: int = 4,
        snapfit_radius_extension: float = 2 * 2 / 3,
        wall_width: float = 2,
        wall_depth: float = 2,
        snapfit_height: float = 2,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        Returns a connector that locks into a socket with a twist.
        ----------
        Arguments:
            - connector_radius: the base radius of the connector mechanism
            - tolerance: the spacing between the connector and the socket
            - arc_percentage: the percentage of the arc that the snapfit will cover
            - snapfit_count: how many snapfit mechanisms to add
            - snapfit_radius_extension: how far beyond the connector the snapfit extends
            - wall_width: the thickness of the wall mechanism
            - wall_depth: the depth of the wall mechanism
            - snapfit_height: the height of the snapfit mechanism
            - rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
            - align (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
                or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
            - mode (Mode, optional): combine mode. Defaults to Mode.ADD

        """
        with BuildPart() as twistbase:
            Cylinder(
                radius=connector_radius,
                height=wall_depth * 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            path = (
                twistbase.edges()
                .filter_by(GeomType.CIRCLE)
                .sort_by(Axis.Z, reverse=True)
                .sort_by(SortBy.RADIUS)[-1]
            )  # top edge of cylinder
            path = path.trim(
                arc_percentage / -200,
                arc_percentage / 200,
            )
            with BuildPart(mode=Mode.PRIVATE) as snapfit:
                path = path.rotate(Axis.Z, 90)
                with BuildSketch(path ^ 0):
                    Polygon(
                        *[
                            (0, 0),
                            (snapfit_radius_extension, 0),
                            (
                                snapfit_radius_extension,
                                snapfit_height,
                            ),
                            (0, snapfit_height / 2),
                        ],
                        align=(Align.MAX, Align.MIN),
                    )
                sweep(path=path)
                with Locations(
                    snapfit.part.center() + (0, snapfit_radius_extension / 2, 0)
                ):
                    Cylinder(
                        radius=snapfit_radius_extension / 2,
                        height=snapfit_height * 3,
                        mode=Mode.SUBTRACT,
                    )
                fillet(
                    snapfit.faces().sort_by(Axis.Y)[-2:].edges().filter_by(Axis.Z),
                    min(
                        snapfit_radius_extension / 8,
                        snapfit.part.max_fillet(
                            snapfit.faces()
                            .sort_by(Axis.Y)[-2:]
                            .edges()
                            .filter_by(Axis.Z),
                            max_iterations=40,
                        ),
                    ),
                )

            with PolarLocations(0, snapfit_count):
                add(snapfit.part)
        super().__init__(
            twistbase.part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


class TwistSnapSocket(BasePartObject):

    def __init__(
        self,
        connector_radius: float = 4.5,
        tolerance: float = 0.12,
        arc_percentage: float = 10,
        snapfit_count: int = 4,
        snapfit_radius_extension: float = 2 * 2 / 3,
        wall_width: float = 2,
        wall_depth: float = 2,
        snapfit_height: float = 2,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ) -> Compound:
        """
        Returns a socket that locks into a connector with a twist.
        ----------
        Arguments:
            - connector_radius: the base radius of the connector mechanism
            - tolerance: the spacing between the connector and the socket
            - arc_percentage: the percentage of the arc that the snapfit will cover
            - snapfit_count: how many snapfit mechanisms to add
            - snapfit_radius_extension: how far beyond the connector the snapfit extends
            - wall_width: the thickness of the wall mechanism
            - wall_depth: the depth of the wall mechanism
            - snapfit_height: the height of the snapfit mechanism
            - rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
            - align (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
                or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
            - mode (Mode, optional): combine mode. Defaults to Mode.ADD
        """
        outer_socket_radius = connector_radius + wall_width * 4 / 3
        with BuildPart() as socket_fitting:
            Cylinder(
                radius=outer_socket_radius,
                height=wall_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            with BuildPart(socket_fitting.faces().sort_by(Axis.Z)[-1]) as snap_socket:
                Cylinder(
                    radius=outer_socket_radius,
                    height=wall_depth * 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
                Cylinder(
                    radius=connector_radius + tolerance,
                    height=wall_depth * 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT,
                )
            trace_path = (
                snap_socket.edges()
                .filter_by(GeomType.CIRCLE)
                .sort_by(Axis.Z, reverse=True)
                .sort_by(SortBy.RADIUS, reverse=True)[-1]
            )  # top edge of cylinder
            path = trace_path.trim(
                (arc_percentage / -200) * 1.1,
                (arc_percentage / 200) * 1.1,
            )
            with BuildPart(mode=Mode.PRIVATE) as snapfit:
                path = path.rotate(Axis.Z, 90)
                with BuildSketch(path ^ 0):
                    Polygon(
                        *[
                            (0, 0),
                            (snapfit_radius_extension, 0),
                            (
                                snapfit_radius_extension,
                                snapfit_height * 2,
                            ),
                            (0, snapfit_height * 2),
                        ],
                        align=(Align.MAX, Align.MIN),
                    )
                sweep(path=path)
                fillet(
                    snapfit.faces().sort_by(Axis.Y)[-1].edges().filter_by(Axis.Z),
                    snapfit_radius_extension / 8,
                )
            with PolarLocations(0, snapfit_count):
                add(snapfit.part, mode=Mode.SUBTRACT)

            path = trace_path.trim(
                (arc_percentage / -200) * 3.3,
                (arc_percentage / 200) * 1.1,
            )
            with BuildPart(mode=Mode.PRIVATE) as snapfit:
                path = path.rotate(Axis.Z, 90)
                with BuildSketch(path ^ 0):
                    Polygon(
                        *[
                            (0, 0),
                            (
                                snapfit_radius_extension + tolerance,
                                0,
                            ),
                            (
                                snapfit_radius_extension + tolerance,
                                snapfit_height + tolerance,
                            ),
                            (
                                0,
                                snapfit_height / 2 + tolerance,
                            ),
                        ],
                        align=(Align.MAX, Align.MIN),
                    )
                sweep(path=path)
                fillet(
                    snapfit.faces().sort_by(Axis.Y)[-1].edges().filter_by(Axis.Z),
                    snapfit_radius_extension / 8,
                )
            with PolarLocations(0, snapfit_count):
                add(snapfit.part, mode=Mode.SUBTRACT)
            with PolarLocations(
                connector_radius + snapfit_radius_extension + tolerance * 2,
                snapfit_count,
                start_angle=arc_percentage * -4,
            ):
                Cylinder(
                    radius=snapfit_radius_extension / 2 - tolerance,
                    height=snapfit_height * 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
        super().__init__(
            socket_fitting.part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


if __name__ == "__main__":
    connector = (
        TwistSnapConnector(
            connector_radius=4.5,
            tolerance=0.12,
            snapfit_height=2,
            snapfit_radius_extension=2 * (2 / 3) - 0.06,
            wall_width=2,
            wall_depth=2,
        )
        .rotate(Axis.X, 180)
        .move(Location((0, 0, 15)))
    )
    socket = TwistSnapSocket(
        connector_radius=4.5,
        tolerance=0.12,
        snapfit_height=2,
        snapfit_radius_extension=2 * (2 / 3) - 0.06,
        wall_width=2,
        wall_depth=2,
    )

    show(connector, socket, reset_camera=Camera.KEEP)
