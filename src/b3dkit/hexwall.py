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
    Cone,
    Cylinder,
    Edge,
    GeomType,
    HexLocations,
    Locations,
    Mode,
    Part,
    Plane,
    RegularPolygon,
    RotationLike,
    extrude,
    thicken,
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


class HexCylindrical(BasePartObject):

    def __init__(
        self,
        cylindrical: Cone | Cylinder,
        hole_radius: float,
        spacing_radius: float,
        horizontal_count: int,
        vertical_count: int,
        thickness: float,
        z_distance: float,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        Part Object: HexCylindrical
        -------
        Wraps a honeycomb of hexagonal holes around the cylindrical surface of a Cylinder
        or Cone and returns the hole geometry *only* (the cutters), so the caller can remove
        them elsewhere with ``mode=Mode.SUBTRACT``.

        The holes are laid out row by row: ``horizontal_count`` holes run around the cone at each
        height, ``vertical_count`` rows stack up the slope from ``z_distance``, and alternate
        rows are offset half a step for a honeycomb stagger. Each hex is projected onto
        the true cone surface (so it follows the curvature) and thickened into a cutter.

        arguments:
            - cylindrical (Part): the cone or cylinder to wrap holes around. Assumed upright on the
                Z axis with its base at the bottom; its circular edges define the radius
                at each height.
            - hole_radius (float): radius of each hexagonal hole (RegularPolygon radius)
            - spacing_radius (float): hex cell radius controlling spacing; nearest holes
                are ``2 * spacing_radius`` apart (matches ``HexLocations(radius=...)``)
            - horizontal_count (int): number of holes around the cone in each row
            - vertical_count (int): number of rows stacked up the slope
            - thickness (float): how far each cutter extends in/out of the surface; set
                ``thickness >= wall_thickness`` to cut clean through a hollow cone wall
            - z_distance (float): height of the lowest row of holes, measured up
                from the bottom of the cone (not an absolute Z coordinate)
            - rotation (RotationLike, optional): angles to rotate about axes. Defaults to
                (0, 0, 0)
            - align (Align | tuple[Align, Align, Align] | None, optional): align MIN,
                CENTER, or MAX of object. Defaults to None
            - mode (Mode, optional): combine mode. Defaults to Mode.ADD
        """

        # Derive the cone's radius-vs-height from its circular edges so any upright
        # cone/frustum works (a pointed cone reduces to radius 0 at its apex).
        circles = cylindrical.edges().filter_by(GeomType.CIRCLE).sort_by(Axis.Z)
        if not circles:
            raise ValueError(
                "cone must have at least one circular edge to wrap holes around"
            )
        bottom = circles[0]
        z_bottom, r_bottom = bottom.arc_center.Z, bottom.radius
        if len(circles) >= 2:
            z_top, r_top = circles[-1].arc_center.Z, circles[-1].radius
        else:
            z_top, r_top = cylindrical.bounding_box().max.Z, 0.0

        def radius_at(z: float) -> float:
            return r_bottom + (r_top - r_bottom) * (z - z_bottom) / (z_top - z_bottom)

        # Honeycomb pitches: nearest-neighbour distance == 2 * spacing_radius, matching
        # HexLocations(radius=spacing_radius). Rows run around (x), stacked up slope (y).
        x_pitch = 2 * spacing_radius
        y_pitch = spacing_radius * sqrt(3)

        def hex_row(count: int) -> list[Part]:
            """A flat row of ``count`` hex faces spaced by x_pitch along +X."""
            with BuildSketch() as row_sketch:
                with Locations(*[(i * x_pitch, 0) for i in range(count)]):
                    RegularPolygon(hole_radius, side_count=6, major_radius=False)
            return row_sketch.sketch.faces()

        # Wrap one row onto the surface at each height, then thicken into cutters.
        # Stop once a row climbs off the cone's surface: above the top edge the
        # radius would extrapolate to zero/negative, which make_circle rejects.
        cutters: list[Part] = []
        for row in range(vertical_count):
            z = z_bottom + z_distance + row * y_pitch
            if not z_bottom <= z <= z_top:
                break
            r = radius_at(z)
            if r <= 0:  # pragma: no cover - defensive: z-bound above already
                break  # keeps r >= 0; only an exact-apex row could reach here
            path = Edge.make_circle(r, Plane.XY.offset(z))

            faces = hex_row(horizontal_count)
            # project_faces anchors the row at faces[0].min.X and lays it out in one
            # direction. Center the row's mean position on a fixed meridian so it grows
            # symmetrically from the center instead of drifting to one side up the taper.
            bboxes = [f.bounding_box() for f in faces]
            first_min_x = bboxes[0].min.X
            mean_center_x = sum((b.min.X + b.max.X) / 2 for b in bboxes) / len(bboxes)
            center_offset = (mean_center_x - first_min_x) / path.length
            stagger = (x_pitch / 2) / path.length if row % 2 else 0.0

            projected = cylindrical.project_faces(
                faces, path=path, start=0.5 - center_offset + stagger
            )
            cutters.extend(
                thicken(face, amount=-thickness, both=False) for face in projected
            )

        # No rows fit on the surface (e.g. z_distance starts at/above the top, or
        # the surface is too short for the given spacing). Fail clearly instead of
        # letting BasePartObject choke on an empty shape downstream.
        if not cutters:
            raise ValueError(
                "no hex holes fit on the surface; check z_distance, spacing_radius, "
                "and the cone/cylinder height"
            )

        # Return the cutters as a single (un-fused) Part so the whole pattern can be
        # subtracted in one boolean by the caller.
        part = Part(children=cutters)
        part.label = "hexcone"

        super().__init__(
            part=part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


if __name__ == "__main__":
    cone = Cone(100, 50, 100, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cylinder = Cylinder(100, 100)

    part = cone
    hexsample = HexCylindrical(part, 1, 2, 20, 10, 2, 20)

    show(part, hexsample)
