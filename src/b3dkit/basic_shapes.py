"""
Utility functions for creating and manipulating basic 3D shapes
and geometric calculations. These functions extend build123d's
capabilities with shapes and operations commonly used in 3D design.
"""

from math import sqrt, radians, cos, sin, tan
from tempfile import template
from typing import Union

from build123d import (
    Align,
    Axis,
    BasePartObject,
    BaseSketchObject,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Builder,
    Circle,
    Compound,
    Cylinder,
    GridLocations,
    JernArc,
    Line,
    Location,
    Mode,
    Part,
    Plane,
    PolarLocations,
    RadiusArc,
    RegularPolygon,
    RotationLike,
    Shape,
    Sketch,
    Sphere,
    add,
    extrude,
    fillet,
    loft,
    make_face,
    scale,
    sweep,
    tuplify,
    validate_inputs,
)
from ocp_vscode import Camera, show


def radius_to_apothem(radius: float, side_count: int = 6) -> float:
    """
    calculates the apothem of a regular polygon given its circumradius
    -------
    arguments:
        - radius: the circumradius of the polygon
    """
    return radius * cos(radians(360 / (2 * side_count)))


def apothem_to_radius(apothem: float, side_count: int = 6) -> float:
    """
    calculates the circumradius of a regular polygon given its apothem
    -------
    arguments:
        - apothem: the apothem of the polygon
    """
    return apothem / cos(radians(360 / (2 * side_count)))


def opposite_length(angle: float, adjacent_length: float) -> float:
    """calculate the opposite side length of a right triangle given the angle and adjacent side length
    ----------
    Arguments:
        - angle: float
            The angle in degrees.
        - adjacent_length: float
            The length of the adjacent side."""
    angle_rad = radians(angle)
    return adjacent_length * tan(angle_rad)


def adjacent_length(angle: float, opposite_length: float) -> float:
    """calculate the adjacent side length of a right triangle given the angle and opposite side length
    ----------
    Arguments:
        - angle: float
            The angle in degrees.
        - opposite_length: float
            The length of the opposite side."""
    angle_rad = radians(angle)
    return opposite_length / tan(angle_rad)


def distance_to_circle_edge(radius, point, angle) -> float:
    """
    for a circle with the given radius, find the distance from the
    given point to the edge of the circle in the direction determined
    by the given angle
    """
    x1, y1 = point
    theta = radians(angle)

    a = 1
    b = 2 * (x1 * cos(theta) + y1 * sin(theta))
    c = x1**2 + y1**2 - radius**2

    discriminant = b**2 - 4 * a * c

    if discriminant < 0:
        raise ValueError(f"Error: discriminant calculated as < 0 ({discriminant})")
    t1 = (-b + sqrt(discriminant)) / (2 * a)
    t2 = (-b - sqrt(discriminant)) / (2 * a)

    t = max(t1, t2)

    return t


def circular_intersection(radius: float, coordinate: float) -> float:
    """
    given a positive position along the axis of a circle, find the intersection
    along the other axis of the perimeter of the circle
    -------
    arguments:
        - radius: the radius of the circle
        - coordinate: a coordinate along one axis of the circle (must be a
            positive value less than the radius)
    """
    if 0 > coordinate > radius:
        raise ValueError("The x-coordinate cannot be greater than the radius.")
    return sqrt(radius**2 - coordinate**2)


class DiamondTorus(BasePartObject):
    def __init__(
        self,
        major_radius: float,
        minor_radius: float,
        stretch: tuple = (1, 1),
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        sweeps a regular diamond along a circle defined by major_radius
        -------
        arguments:
            - major_radius: the radius of the circle to sweep the diamond along
            - minor_radius: the radius of the diamond
            - stretch: scales the diamond shape
            - rotation: the rotation of the torus
            - align: the alignment of the torus
            - mode: the mode of the torus
        """

        context: BuildPart = BuildPart._get_context()
        validate_inputs(context, self)

        with BuildPart() as torus:
            with BuildLine():
                l1 = JernArc(
                    start=(major_radius, 0),
                    tangent=(0, 1),
                    radius=major_radius,
                    arc_size=360,
                )
            with BuildSketch(l1 ^ 0):
                RegularPolygon(radius=minor_radius, side_count=4)
                scale(by=(stretch[0], stretch[1], 1))
            sweep()
        super().__init__(
            part=torus.part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


class RoundedCylinder(BasePartObject):
    def __init__(
        self,
        radius: float,
        height: float,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        sweeps a regular diamond along a circle defined by major_radius
        -------
        arguments:
            - radius: the radius of the cylinder
            - height: the height of the cylinder
            - rotation: the rotation of the cylinder
            - align: the alignment of the cylinder
            - mode: the mode of the cylinder
        """

        context: BuildPart = BuildPart._get_context()
        validate_inputs(context, self)

        if height <= radius * 2:
            raise ValueError("height must be greater than radius * 2")
        with BuildPart() as cylinder:
            Cylinder(radius=radius, height=height, align=align)
            fillet(
                cylinder.faces().sort_by(Axis.Z)[-1].edges()
                + cylinder.faces().sort_by(Axis.Z)[0].edges(),
                radius=radius,
            )
        super().__init__(
            part=cylinder.part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


class PolygonalCylinder(BasePartObject):

    def __init__(
        self,
        radius: float,
        height: float,
        side_count: int = 6,
        stretch: tuple = (1, 1, 1),
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        creates an extruded polygon that behaves like a cylinder
        -------
        arguments:
            - radius: the radius of the cylinder
            - height: the height of the cylinder
            - side_count: the number of sides of the polygonal base (default is 6)
            - stretch: scales the base polygon
            - rotation: the rotation of the cylinder
            - align: the alignment of the cylinder
            - mode: the mode to use when
        """
        context: BuildPart = BuildPart._get_context()
        validate_inputs(context, self)

        with BuildPart() as tube:
            with BuildSketch():
                RegularPolygon(
                    radius=radius, side_count=side_count, align=tuplify(align, 2)
                )
            extrude(amount=height * stretch[2])
        super().__init__(
            part=tube.part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


class DiamondCylinder(PolygonalCylinder):

    def __init__(
        self,
        radius: float,
        height: float,
        stretch: tuple = (1, 1, 1),
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        creates an extruded diamond that behaves like a cylinder
        -------
        arguments:
            - radius: the radius of the cylinder
            - height: the height of the cylinder
            - rotation: the rotation of the cylinder
            - align: the alignment of the cylinder (default
                    is (Align.CENTER, Align.CENTER, Align.CENTER) )
            - mode: the mode to use when adding the part
        """
        super().__init__(
            radius=radius,
            height=height,
            side_count=4,
            stretch=stretch,
            rotation=rotation,
            align=align,
            mode=mode,
        )


class Teardrop(BaseSketchObject):

    def __init__(
        self,
        radius: float,
        peak_distance: float,
        rotation: RotationLike = (0, 0),
        align: Union[None, Align, tuple[Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        Create a teardrop shape sketch;
        this can be useful when creating holes along the Z axis
        to compensate for overhang issues with FDM printers.
        ----------
        Arguments:
            - radius: float
                The radius of the teardrop.
            - peak_distance: float
                The distance from the center of the teardrop circle to the peak of the
                teardrop shape.
            - align: tuple
                The alignment of the teardrop. Note that the Y alignment is to the center of the cylinder, ignoring the peak distance
            - mode: Mode
                The mode of the teardrop.
        """
        context: BuildSketch = BuildSketch._get_context()
        validate_inputs(context, self)

        x = radius * sqrt(1 - (radius**2 / peak_distance**2))
        y = radius**2 / peak_distance
        with BuildSketch() as teardrop:
            if peak_distance == radius:
                Circle(radius)
            else:
                with BuildLine() as outline:
                    Line((-x, -y), (0, -peak_distance))
                    Line((0, -peak_distance), (x, -y))
                    RadiusArc((x, -y), (-x, -y), radius, short_sagitta=False)
                make_face()
        super().__init__(
            obj=teardrop.sketch,
            rotation=rotation,
            align=tuplify(align, 2),
            mode=mode,
        )


class TeardropCylinder(BasePartObject):

    def __init__(
        self,
        radius: float,
        height: float,
        peak_distance: float,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        Create a cylinder with a teardrop shape;
        this can be useful when creating holes along the Z axis
        to compensate for overhang issues with FDM printers.
        ----------
        Arguments:
            - radius: float
                The radius of the cylinder.
            - height: float
                The height of the cylinder.
            - peak_distance: float
                The distance from the center of the cylinder to the peak of the
                teardrop shape.
            - rotation: tuple
                The rotation of the cylinder.
            - align: tuple
                The alignment of the cylinder.
            - mode: Mode
                The mode of the cylinder.
        """
        context: BuildPart = BuildPart._get_context()
        validate_inputs(context, self)

        with BuildPart() as cylinder:
            with BuildSketch():
                Teardrop(radius, peak_distance, align=tuplify(align, 2))
            extrude(amount=height)
        super().__init__(
            part=cylinder.part,
            rotation=rotation,
            align=tuplify(align, 3),
            mode=mode,
        )


if __name__ == "__main__":

    show(
        DiamondTorus(
            50,
            2,
        ),
        reset_camera=Camera.KEEP,
    )
    show(
        DiamondCylinder(
            radius=50,
            height=200,
            stretch=(1, 1, 1),
            rotation=(0, 0, 0),
            align=(Align.MIN, Align.MIN, Align.CENTER),
        ),
        reset_camera=Camera.KEEP,
    )
