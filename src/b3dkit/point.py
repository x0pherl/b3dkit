"""
A minimal abstraction for a 2D point, allowing the x,y values to be interpreted from a tuple.
Also has some utility functions for calculating various useful properties of points.
"""

from dataclasses import dataclass
from math import atan2, cos, degrees, radians, sin, tan
from typing import Union, Tuple
from build123d import Axis


@dataclass
class Point:
    """
    A 2D point with x and y coordinates.
    """

    x: float
    y: float

    @property
    def X(self):
        """the x coordinate of the point
        ----------
        Returns:
            - float: The x coordinate of the point"""
        return self.x

    @property
    def Y(self):
        """the y coordinate of the point
        ----------
        Returns:
            - float: The y coordinate of the point"""
        return self.y

    def __init__(self, x: Union[float, list[float, float]] = None, y: float = None):
        """initialize the point with x and y coordinates passed as a tuple or individual values
        ----------
        Arguments:
            - x: Union[float, list[float, float]]
                The x coordinate or a list containing [x, y] coordinates
            - y: float
                The y coordinate (ignored if x is a list)"""
        if isinstance(x, list) and len(x) >= 2:
            self.x, self.y = x
        else:
            self.x = x
            self.y = y

    def __iter__(self):
        """iterate through the x and y coordinates of the point
        ----------
        Yields:
            - float: The x coordinate, then the y coordinate"""
        yield self.x
        yield self.y

    def __getitem__(self, index):
        """return the x or y coordinate of the point
        ----------
        Arguments:
            - index: int
                0 for x coordinate, 1 for y coordinate
        Returns:
            - float: The requested coordinate"""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Index out of range")

    def angle_to(self, point: "Point") -> float:
        """from the point, identify the angle to a second point
        ----------
        Arguments:
            - point: Point
                The target point to calculate angle to
        Returns:
            - float: The angle in degrees (0-360) from this point to the target point"""
        return degrees(atan2(point.y - self.y, point.x - self.x)) % 360

    def distance_to(self, point: "Point") -> float:
        """from the point, identify the distance to a second point
        ----------
        Arguments:
            - point: Point
                The target point to calculate distance to
        Returns:
            - float: The Euclidean distance between the two points"""
        return ((self.x - point.x) ** 2 + (self.y - point.y) ** 2) ** 0.5

    def related_point(self, angle: float, distance: float) -> "Point":
        """from the point, identify a second point at a specified angle and distance
        ----------
        Arguments:
            - angle: float
                The angle in degrees from this point (0° = positive x direction)
            - distance: float
                The distance from this point to the new point
        Returns:
            - Point: A new point at the specified angle and distance"""
        angle_rad = radians(angle)
        return Point(
            self.x + distance * cos(angle_rad),
            self.y + distance * sin(angle_rad),
        )

    def related_point_by_axis(
        self, angle: float, axis_distance: float, axis: Axis = Axis.X
    ) -> "Point":
        """from the point, identify a second point at a specified angle with a given distance along x or y axis
        ----------
        Arguments:
            - angle: float
                The angle in degrees from this point (0° = positive x direction)
            - axis_distance: float
                The distance to travel along the specified axis
            - axis: Axis
                Either Axis.X or Axis.Y - the axis along which to measure the distance
        Returns:
            - Point: A new point at the specified angle with the given axis distance"""
        angle_rad = radians(angle)

        if axis == Axis.X:
            # If we want to move axis_distance along x-axis at the given angle
            # x_distance = axis_distance, so we need to find the corresponding y_distance
            # cos(angle) = x_distance / hypotenuse, so hypotenuse = x_distance / cos(angle)
            if abs(cos(angle_rad)) < 1e-10:
                raise ValueError(
                    f"Cannot move along x-axis at angle {angle} degrees (cos ≈ 0)"
                )
            hypotenuse = abs(axis_distance / cos(angle_rad))
            return Point(
                self.x + axis_distance,
                self.y
                + hypotenuse * sin(angle_rad) * (1 if cos(angle_rad) > 0 else -1),
            )
        elif axis == Axis.Y:
            # If we want to move axis_distance along y-axis at the given angle
            # y_distance = axis_distance, so we need to find the corresponding x_distance
            # sin(angle) = y_distance / hypotenuse, so hypotenuse = y_distance / sin(angle)
            if abs(sin(angle_rad)) < 1e-10:
                raise ValueError(
                    f"Cannot move along y-axis at angle {angle} degrees (sin ≈ 0)"
                )
            hypotenuse = abs(axis_distance / sin(angle_rad))
            return Point(
                self.x
                + hypotenuse * cos(angle_rad) * (1 if sin(angle_rad) > 0 else -1),
                self.y + axis_distance,
            )
        else:
            raise ValueError("axis must be Axis.X or Axis.Y")


def midpoint(point1: Point, point2: Point) -> Point:
    """find the midpoint between two points
    ----------
    Arguments:
        - point1: Point
            The first point.
        - point2: Point
            The second point."""
    midpoint = Point((point1.x + point2.x) / 2, (point1.y + point2.y) / 2)
    return midpoint


def shifted_midpoint(point1: Point, point2: Point, shift: float) -> Point:
    """find the midpoint between two points, with an allowance to shift the
    midpoint towards point2
    ----------
    Arguments:
        - point1: Point
            The first point.
        - point2: Point
            The second point.
        - shift: float
            The distance to shift the midpoint towards point2"""
    mid_x = (point1.x + point2.x) / 2
    mid_y = (point1.y + point2.y) / 2

    direction_x = point2.x - point1.x
    direction_y = point2.y - point1.y

    # Normalize the direction vector
    length = (direction_x**2 + direction_y**2) ** 0.5
    direction_x /= length
    direction_y /= length

    # Shift the midpoint towards point2 by the specified amount
    shifted_mid_x = mid_x + direction_x * shift
    shifted_mid_y = mid_y + direction_y * shift

    return Point(shifted_mid_x, shifted_mid_y)
