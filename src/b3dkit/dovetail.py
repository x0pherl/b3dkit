from enum import Enum, auto
from math import atan, atan2, degrees, radians, tan
from typing import Tuple
from build123d import (
    Align,
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Box,
    Compound,
    Cylinder,
    FilletPolyline,
    GridLocations,
    Line,
    Location,
    Mode,
    Part,
    Plane,
    PolarLocations,
    Polyline,
    add,
    extrude,
    fillet,
    loft,
    make_face,
)

# it's a bad habit, but I keep some simple test code under __main__
# to make creating test object easy -- this adds ".b3dkit" to the path
if __name__ == "__main__":
    import sys, os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from b3dkit.point import (
    Point,
    midpoint,
    shifted_midpoint,
)

from b3dkit.click_fit import Divot


class DovetailPart(Enum):
    TAIL = auto()
    SOCKET = auto()


class DovetailStyle(Enum):
    TRADITIONAL = auto()
    SNUGTAIL = auto()
    T_SLOT = auto()


def subpart_outline_boundary(
    start: Point,
    end: Point,
    max_dimension: float,
    section: DovetailPart = DovetailPart.TAIL,
    tolerance: float = 0.1,
    scarf_offset: float = 0,
) -> Line:
    direction_multiplier = 1 if section == DovetailPart.TAIL else -1
    base_angle = start.angle_to(end)
    dovetail_tolerance = -(abs(tolerance / 2)) * direction_multiplier
    adjusted_start_point = start.related_point(base_angle - 90, scarf_offset)
    adjusted_end_point = end.related_point(base_angle - 90, scarf_offset)
    toleranced_start_point = adjusted_start_point.related_point(
        base_angle - 90, dovetail_tolerance
    )
    toleranced_end_point = adjusted_end_point.related_point(
        base_angle - 90, dovetail_tolerance
    )

    with BuildLine() as border:
        Polyline(
            *[
                tuple(toleranced_start_point),
                tuple(
                    toleranced_start_point.related_point(
                        base_angle + 180, max_dimension
                    )
                ),
                tuple(
                    toleranced_start_point.related_point(
                        base_angle - 225 * direction_multiplier, max_dimension
                    )
                ),
                tuple(
                    toleranced_end_point.related_point(
                        base_angle + 45 * direction_multiplier, max_dimension
                    )
                ),
                tuple(toleranced_end_point.related_point(base_angle, max_dimension)),
                tuple(toleranced_end_point),
            ]
        )

    return border.line


def snugtail_subpart_outline(
    start: Point,
    end: Point,
    max_dimension: float = 1000,
    section: DovetailPart = DovetailPart.TAIL,
    tolerance: float = 0.025,
    tail_angle_offset: float = 15,
    taper_distance: float = 0,
    length_ratio: float = 0.8,
    depth_ratio: float = 0.15,
    scarf_offset: float = 0,
    straighten_dovetail: bool = False,
) -> Line:
    """
    given a part and a start and end point on the XY plane, returns an outline to build an intersection Part to generate the subpart
    args:
        - part: the part to split
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - scarf_offset: setting this to a non-zero value will shift the dovetail to allow for tilt adjustemnt between the top & bottom outlines
        - straighten_dovetail: setting this to True will draw the straight line of the cut,
            allowing for the correct tolerances for the section
    """
    if (length_ratio + depth_ratio > 1) and not straighten_dovetail:
        raise ValueError(
            "the combined length_ratio and depth_ratio must be not exceed 1"
        )

    direction_multiplier = 1 if section == DovetailPart.TAIL else -1
    base_angle = start.angle_to(end)
    opposite_angle = 180 if base_angle == 0 else -base_angle
    dovetail_tolerance = -(abs(tolerance / 2)) * direction_multiplier
    adjusted_start_point = start.related_point(base_angle - 90, scarf_offset)
    adjusted_end_point = end.related_point(base_angle - 90, scarf_offset)
    toleranced_start_point = adjusted_start_point.related_point(
        base_angle - 90, dovetail_tolerance
    )
    toleranced_end_point = adjusted_end_point.related_point(
        base_angle - 90, dovetail_tolerance
    )

    cut_length = start.distance_to(end)
    tail_depth = cut_length * depth_ratio
    tail_length = cut_length * length_ratio

    cut_start = toleranced_start_point
    cut_end = toleranced_end_point

    fin_join = cut_start.related_point(
        base_angle, tail_depth / 2 + dovetail_tolerance
    ).related_point(base_angle - 90, tail_depth / 2 + dovetail_tolerance)
    fin_depart = cut_end.related_point(
        base_angle - 180, tail_depth / 2 + dovetail_tolerance
    ).related_point(base_angle - 90, tail_depth / 2 + dovetail_tolerance)

    start_fin = cut_start.related_point(
        base_angle, tail_depth / 2 + dovetail_tolerance
    ).related_point(base_angle + 90, dovetail_tolerance)
    end_fin = cut_end.related_point(
        base_angle - 180, tail_depth / 2 + dovetail_tolerance
    ).related_point(base_angle + 90, dovetail_tolerance)

    start_snugtail = start_fin.related_point(
        base_angle + 90, cut_length - tail_depth / 2
    )
    end_snugtail = end_fin.related_point(base_angle + 90, cut_length - tail_depth / 2)

    fin_connect = start_fin.related_point(
        base_angle + 90, cut_length - dovetail_tolerance
    )

    fin_disconnect = end_fin.related_point(
        base_angle + 90, cut_length - dovetail_tolerance
    )

    start_tail_line = fin_connect.related_point(
        base_angle,
        abs(dovetail_tolerance) * (4 if section == DovetailPart.TAIL else 6)
        - dovetail_tolerance * 2,
    )

    end_tail_line = fin_disconnect.related_point(
        opposite_angle,
        abs(dovetail_tolerance) * (4 if section == DovetailPart.TAIL else 6)
        - dovetail_tolerance * 2,
    )

    with BuildLine() as tail_line:
        add(
            subpart_outline_boundary(
                start=start,
                end=end,
                max_dimension=max_dimension,
                section=section,
                tolerance=tolerance,
                scarf_offset=scarf_offset,
            )
        )

        FilletPolyline(
            *[cut_start, fin_join, start_fin],
            radius=abs(dovetail_tolerance) * (3 if section == DovetailPart.TAIL else 2),
        )
        if straighten_dovetail:
            Line(start_fin, start_snugtail)
        else:
            add(
                dovetail_split_line(
                    start=start_fin.related_point(base_angle, -dovetail_tolerance),
                    end=start_snugtail.related_point(base_angle, -dovetail_tolerance),
                    linear_offset=-tail_depth / 2,
                    section=section,
                    tolerance=tolerance,
                    tail_angle_offset=tail_angle_offset,
                    taper_distance=taper_distance,
                    length_ratio=length_ratio,
                    depth_ratio=depth_ratio,
                )
            )
        FilletPolyline(
            *[start_snugtail, fin_connect, start_tail_line],
            radius=abs(dovetail_tolerance) * (2 if section == DovetailPart.TAIL else 3),
        )
        if straighten_dovetail:
            Line(
                start_tail_line,
                end_tail_line,
            )
        else:
            add(
                dovetail_split_line(
                    start=start_tail_line.related_point(
                        base_angle - 90, -dovetail_tolerance
                    ),
                    end=end_tail_line.related_point(
                        base_angle - 90, -dovetail_tolerance
                    ),
                    section=section,
                    linear_offset=0,
                    tolerance=tolerance,
                    tail_angle_offset=tail_angle_offset,
                    taper_distance=taper_distance,
                    length_ratio=length_ratio,
                    depth_ratio=depth_ratio,
                )
            )
        FilletPolyline(
            *[end_tail_line, fin_disconnect, end_snugtail],
            radius=abs(dovetail_tolerance) * (2 if section == DovetailPart.TAIL else 3),
        )
        if straighten_dovetail:
            Line(end_snugtail, end_fin)
        else:
            add(
                dovetail_split_line(
                    start=end_snugtail.related_point(base_angle, dovetail_tolerance),
                    end=end_fin.related_point(base_angle, dovetail_tolerance),
                    section=section,
                    linear_offset=tail_depth / 2,
                    tolerance=tolerance,
                    tail_angle_offset=tail_angle_offset,
                    taper_distance=taper_distance,
                    length_ratio=length_ratio,
                    depth_ratio=depth_ratio,
                )
            )
        FilletPolyline(
            *[end_fin, fin_depart, cut_end],
            radius=abs(dovetail_tolerance) * (3 if section == DovetailPart.TAIL else 2),
        )
    return tail_line.line


def dovetail_subpart_outline(
    start: Point,
    end: Point,
    max_dimension: float = 1000,
    section: DovetailPart = DovetailPart.TAIL,
    style: DovetailStyle = DovetailStyle.TRADITIONAL,
    linear_offset: float = 0,
    tolerance: float = 0.025,
    tail_angle_offset: float = 15,
    taper_distance: float = 0,
    length_ratio: float = 1 / 3,
    depth_ratio: float = 1 / 6,
    slot_count: int = 1,
    depth: float = 2,
    scarf_offset: float = 0,
    straighten_dovetail: bool = False,
) -> Line:
    """
    given a part and a start and end point on the XY plane, returns an outline to build an intersection Part to generate the subpart
    args:
        - part: the part to split
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - style: valid styles are DovetailStyle.TRADITIONAL, DovetailStyle.T_SLOT
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - scarf_offset: setting this to a non-zero value will shift the dovetail to allow for tilt adjustemnt between the top & bottom outlines
        - straighten_dovetail: setting this to True will draw the straight line of the cut,
            allowing for the correct tolerances for the section
    """
    if style not in (DovetailStyle.TRADITIONAL, DovetailStyle.T_SLOT):
        raise ValueError(f"Invalid style: {style}")
    direction_multiplier = 1 if section == DovetailPart.TAIL else -1
    base_angle = start.angle_to(end)
    dovetail_tolerance = -(abs(tolerance / 2)) * direction_multiplier
    adjusted_start_point = start.related_point(base_angle - 90, scarf_offset)
    adjusted_end_point = end.related_point(base_angle - 90, scarf_offset)
    toleranced_start_point = adjusted_start_point.related_point(
        base_angle - 90, dovetail_tolerance
    )
    toleranced_end_point = adjusted_end_point.related_point(
        base_angle - 90, dovetail_tolerance
    )

    with BuildLine() as tail_line:
        add(
            subpart_outline_boundary(
                start=start,
                end=end,
                max_dimension=max_dimension,
                section=section,
                tolerance=tolerance,
                scarf_offset=scarf_offset,
            )
        )
        if straighten_dovetail:
            Line(toleranced_start_point, toleranced_end_point)
        elif style == DovetailStyle.T_SLOT:
            add(
                tslot_split_line(
                    start=adjusted_start_point,
                    end=adjusted_end_point,
                    section=section,
                    slot_count=slot_count,
                    depth=depth,
                    tolerance=tolerance,
                    taper_distance=taper_distance,
                )
            )
        else:
            add(
                dovetail_split_line(
                    start=adjusted_start_point,
                    end=adjusted_end_point,
                    section=section,
                    linear_offset=linear_offset,
                    tolerance=tolerance,
                    tail_angle_offset=tail_angle_offset,
                    taper_distance=taper_distance,
                    length_ratio=length_ratio,
                    depth_ratio=depth_ratio,
                )
            )
    return tail_line.line


def subpart_outline(
    start: Point,
    end: Point,
    max_dimension: float = 1000,
    section: DovetailPart = DovetailPart.TAIL,
    style: DovetailStyle = DovetailStyle.SNUGTAIL,
    linear_offset: float = 0,
    tolerance: float = 0.025,
    tail_angle_offset: float = 15,
    taper_distance: float = 0,
    length_ratio: float = 1 / 3,
    depth_ratio: float = 1 / 6,
    scarf_offset: float = 0,
    slot_count: int = 2,
    depth: float = 2,
    straighten_dovetail: bool = False,
) -> Line:
    """
    given a part and a start and end point on the XY plane, returns an outline to build an intersection Part to generate the subpart
    args:
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - max_dimension: the maximum dimension of the part to split, used to determine the size of the outline
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - scarf_offset: setting this to a non-zero value will shift the dovetail to allow for tilt adjustemnt between the top & bottom outlines
        - straighten_dovetail: setting this to True will draw the straight line of the cut,
            allowing for the correct tolerances for the section
    """
    if style == DovetailStyle.SNUGTAIL:
        return snugtail_subpart_outline(
            start=start,
            end=end,
            max_dimension=max_dimension,
            section=section,
            tolerance=tolerance,
            tail_angle_offset=tail_angle_offset,
            taper_distance=taper_distance,
            length_ratio=length_ratio,
            scarf_offset=scarf_offset,
            straighten_dovetail=straighten_dovetail,
        )
    else:
        return dovetail_subpart_outline(
            start=start,
            end=end,
            max_dimension=max_dimension,
            section=section,
            style=style,
            linear_offset=linear_offset,
            tolerance=tolerance,
            tail_angle_offset=tail_angle_offset,
            taper_distance=taper_distance,
            length_ratio=length_ratio,
            depth_ratio=depth_ratio,
            scarf_offset=scarf_offset,
            slot_count=slot_count,
            depth=depth,
            straighten_dovetail=straighten_dovetail,
        )


def traditional_subpart_divots(
    subpart: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    linear_offset: float = 0,
    tolerance: float = 0.025,
    vertical_tolerance: float = 0.2,
    scarf_angle: float = 0,
    taper_angle: float = 0,
    depth_ratio: float = 1 / 6,
    vertical_offset: float = 0,
    click_fit_radius: float = 0,
):
    """
    adds/subtracts click-fit divots to subpart and returns it
    ----------
    Arguments:
        - subpart: the part to add divots to
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - scarf_angle: the scarf angle of the dovetail
        - taper_angle: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - vertical_offset: the vertical offset of the dovetail
        - click_fit_radius: the radius of the click-fit divots
    """

    cut_angle = start.angle_to(end)

    # how much of an offset is there along the top and bottom of the subparts
    scarf_offset = (subpart.bounding_box().size.Z) * tan(radians(scarf_angle)) / 2

    tailtop_z = subpart.bounding_box().max.Z + (
        vertical_offset if vertical_offset < 0 else 0
    )

    adjusted_top_divot_angle = scarf_angle - taper_angle

    taper_offset = (subpart.bounding_box().size.Z - abs(vertical_offset)) * tan(
        radians(adjusted_top_divot_angle)
    )

    topmode = (
        Mode.SUBTRACT
        if ((section == DovetailPart.TAIL) == (vertical_offset < 0))
        else Mode.ADD
    )
    bottommode = (
        Mode.ADD
        if ((section == DovetailPart.SOCKET) == (vertical_offset >= 0))
        else Mode.SUBTRACT
    )

    top_divot_center = shifted_midpoint(start, end, linear_offset).related_point(
        cut_angle - 90,
        start.distance_to(end) * depth_ratio
        - scarf_offset
        + taper_offset
        - click_fit_radius / 2,
    )

    with BuildPart() as divotedpart:
        add(subpart, mode=Mode.ADD)
        with BuildPart(
            Location(
                (
                    top_divot_center.x,
                    top_divot_center.y,
                    tailtop_z - click_fit_radius * 2,
                )
            ),
            mode=topmode,
        ):
            add(
                Divot(
                    click_fit_radius,
                    positive=topmode == Mode.ADD,
                    extend_base=True,
                )
                .rotate(
                    Axis.X,
                    (90 * (-1 if vertical_offset < 0 else 1))
                    + adjusted_top_divot_angle,
                )
                .rotate(Axis.Y, cut_angle),
            )
        #####################################
        # Bottom divots
        #####################################
        start_side = start.related_point(cut_angle, click_fit_radius * 2).related_point(
            cut_angle + 90,
            scarf_offset - ((click_fit_radius * 2) * tan(radians(scarf_angle))),
        )
        end_side = end.related_point(cut_angle, -click_fit_radius * 2).related_point(
            cut_angle - 90,
            -scarf_offset + ((click_fit_radius * 2) * tan(radians(scarf_angle))),
        )
        with BuildPart(
            Location(
                (
                    start_side.x,
                    start_side.y,
                    click_fit_radius * 2,
                )
            ),
            mode=bottommode,
        ):
            add(
                Divot(
                    click_fit_radius,
                    positive=bottommode == Mode.ADD,
                    extend_base=True,
                )
                .rotate(
                    Axis.X,
                    (90 * (1 if vertical_offset < 0 else -1)) + scarf_angle,
                )
                .rotate(Axis.Y, cut_angle),
            )
        with BuildPart(
            Location((end_side.x, end_side.y, click_fit_radius * 2)),
            mode=bottommode,
        ):
            add(
                Divot(click_fit_radius, positive=True, extend_base=True)
                .rotate(
                    Axis.X,
                    (90 * (1 if vertical_offset < 0 else -1)) + scarf_angle,
                )
                .rotate(Axis.Y, cut_angle),
            )

    return divotedpart.part


def snugtail_divots(
    subpart: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    tolerance: float = 0.025,
    scarf_angle: float = 0,
    depth_ratio: float = 1 / 10,
    length_ratio: float = 1 / 5,
    vertical_offset: float = 0,
    click_fit_radius: float = 0,
) -> Part:
    part_width = start.distance_to(end)
    tail_depth = part_width * depth_ratio
    direction_multiplier = -1 if section == DovetailPart.TAIL else 1
    inner_width = (
        part_width - (part_width * depth_ratio * 2) - (tolerance * direction_multiplier)
    )
    cut_angle = start.angle_to(end)
    with BuildPart() as divotedpart:
        add(subpart, mode=Mode.ADD)
        with BuildPart(
            Location(
                (
                    0,
                    part_width * length_ratio * 1.5 + midpoint(start, end).Y,
                    click_fit_radius * 2,
                )
            ),
            mode=Mode.SUBTRACT if section == DovetailPart.SOCKET else Mode.ADD,
        ):
            with PolarLocations(inner_width / 2, 2, start_angle=cut_angle):
                Divot(
                    radius=click_fit_radius,
                    positive=True,
                    extend_base=True,
                ).rotate(Axis.Y, -90)
    return divotedpart.part


def subpart_divots(
    subpart: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    style: DovetailStyle = DovetailStyle.SNUGTAIL,
    linear_offset: float = 0,
    tolerance: float = 0.025,
    vertical_tolerance: float = 0.2,
    scarf_angle: float = 0,
    taper_angle: float = 0,
    depth_ratio: float = 1 / 6,
    length_ratio: float = 1 / 3,
    vertical_offset: float = 0,
    click_fit_radius: float = 0,
):
    """
    adds/subtracts click-fit divots to subpart and returns it
    ----------
    Arguments:
        - subpart: the part to add divots to
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - style: create a traditional dovetal or a cut that wraps around 3 sides of the object and creates a tighter fit
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - scarf_angle: the scarf angle of the dovetail
        - taper_angle: an extra shrinking factor for the dovetail size, allows for easier assembly
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - vertical_offset: the vertical offset of the dovetail
        - click_fit_radius: the radius of the click-fit divots
    """
    if style == DovetailStyle.TRADITIONAL:
        return traditional_subpart_divots(
            subpart=subpart,
            start=start,
            end=end,
            section=section,
            linear_offset=linear_offset,
            tolerance=tolerance,
            vertical_tolerance=vertical_tolerance,
            scarf_angle=scarf_angle,
            taper_angle=taper_angle,
            depth_ratio=depth_ratio,
            vertical_offset=vertical_offset,
            click_fit_radius=click_fit_radius,
        )
    else:
        return snugtail_divots(
            subpart=subpart,
            start=start,
            end=end,
            section=section,
            tolerance=tolerance,
            scarf_angle=scarf_angle,
            depth_ratio=1 / 10,
            length_ratio=1 / 5,
            vertical_offset=vertical_offset,
            click_fit_radius=click_fit_radius,
        )


def subpart_section(
    start: Point,
    end: Point,
    max_dimension: float,
    section: DovetailPart = DovetailPart.TAIL,
    style: DovetailStyle = DovetailStyle.SNUGTAIL,
    floor_z: float = 0,
    floor_taper_distance: float = 0,
    floor_scarf_offset: float = 0,
    top_z: float = 0,
    top_taper_distance: float = 0,
    top_scarf_offset: float = 0,
    tolerance: float = 0.1,
    slot_count: int = 1,
    depth: float = 2,
    linear_offset: float = 0,
    tail_angle_offset: float = 20,
    length_ratio: float = 1 / 3,
    depth_ratio: float = 1 / 6,
    straighten_dovetail: bool = False,
) -> Part:
    with BuildPart() as intersect:
        with BuildSketch(Plane.XY.offset(floor_z)):
            with BuildLine() as baseline:
                add(
                    subpart_outline(
                        start=start,
                        end=end,
                        max_dimension=max_dimension,
                        section=section,
                        style=style,
                        tolerance=tolerance,
                        taper_distance=floor_taper_distance,
                        slot_count=slot_count,
                        depth=depth,
                        scarf_offset=floor_scarf_offset,
                        straighten_dovetail=straighten_dovetail,
                    )
                )
            make_face()
        with BuildSketch(Plane.XY.offset(top_z)) as topline:
            with BuildLine():
                add(
                    subpart_outline(
                        start=start,
                        end=end,
                        max_dimension=max_dimension,
                        section=section,
                        style=style,
                        tolerance=tolerance,
                        taper_distance=top_taper_distance,
                        slot_count=slot_count,
                        depth=depth,
                        scarf_offset=top_scarf_offset,
                        straighten_dovetail=straighten_dovetail,
                    )
                )
            make_face()
        loft()
    return intersect.part


def dovetail_subpart(
    part: Part,
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    style: DovetailStyle = DovetailStyle.SNUGTAIL,
    linear_offset: float = 0,
    tolerance: float = 0.025,
    vertical_tolerance: float = 0.2,
    slot_count: int = 1,
    depth: float = 2,
    tail_angle_offset: float = 15,
    taper_angle: float = 0,
    length_ratio: float = 1 / 3,
    depth_ratio: float = 1 / 6,
    scarf_angle: float = 0,
    vertical_offset: float = 0,
    click_fit_radius: float = 0,
) -> Part:
    """
    given a part and a start and end point on the XY plane, returns a Part for the appropriate split section
    args:
        - part: the part to split
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - style: create a traditional dovetal or a cut that wraps around 3 sides of the object and creates a tighter fit
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - taper_angle: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - scarf_angle: setting this to a non-zero value will tilt the dovetail along the Z axis which may improve part stability
        - vertical_offset: offsets the dovetail along the Z axis by the ammount specified, which results in a straight line
            cut on one side, and provides a hard stop for fitting. A positive number results in a straight cut on the bottom
            of the part passed, a negagive number results in a straight cut on the top of the part passed
    """
    if start == end:
        raise ValueError("start and end points cannot be the same")
    if abs(vertical_offset) > part.bounding_box().size.Z:
        raise ValueError("Vertical offset cannot be greater than the part's height")
    if vertical_offset < 0 and taper_angle < 0:
        raise ValueError(
            "a negative taper_angle and a positive vertical_offset will result in an invalid dovetail"
        )
    if vertical_offset > 0 and taper_angle > 0:
        raise ValueError(
            "a positive taper_angle and a positive vertical_offset will result in an invalid dovetail"
        )

    max_dimension = (
        max(
            part.bounding_box().size.X,
            part.bounding_box().size.Y,
            part.bounding_box().size.Z,
        )
        * 3
    )

    vertical_tolerance_adjustment = (
        vertical_tolerance
        * (1 if section == DovetailPart.TAIL else -1)
        * (1 if vertical_offset > 0 else -1)
    )
    scarf_offset = (part.bounding_box().size.Z) * tan(radians(scarf_angle)) / 2
    vertical_scarf_offset = (
        abs(vertical_offset) - vertical_tolerance_adjustment
    ) * tan(radians(scarf_angle))

    taper_offset = (
        part.bounding_box().size.Z
        - abs(vertical_offset)
        - vertical_tolerance_adjustment
    ) * tan(radians(abs(taper_angle)))
    with BuildPart() as intersect:
        if vertical_offset > 0:
            add(
                subpart_section(
                    start=start,
                    end=end,
                    max_dimension=max_dimension,
                    section=section,
                    style=style,
                    floor_z=part.bounding_box().min.Z,
                    floor_taper_distance=0,  # fix taper_offset if (taper_angle < 0) else 0,
                    floor_scarf_offset=-scarf_offset,
                    top_z=part.bounding_box().min.Z
                    + vertical_offset
                    + vertical_tolerance_adjustment,
                    top_taper_distance=0,  # fix
                    linear_offset=linear_offset,
                    top_scarf_offset=-scarf_offset + vertical_scarf_offset,
                    tolerance=tolerance,
                    slot_count=slot_count,
                    depth=depth,
                    straighten_dovetail=True,
                )
            )
        current_floor = (
            part.bounding_box().min.Z
            if vertical_offset <= 0
            else part.bounding_box().min.Z + abs(vertical_offset) + vertical_tolerance
        )
        add(
            subpart_section(
                start=start,
                end=end,
                max_dimension=max_dimension,
                section=section,
                style=style,
                floor_z=current_floor,
                floor_taper_distance=taper_offset if (taper_angle < 0) else 0,
                floor_scarf_offset=(
                    -scarf_offset
                    if vertical_offset <= 0
                    else -scarf_offset + vertical_scarf_offset
                ),
                top_z=part.bounding_box().max.Z
                + (
                    0
                    if vertical_offset >= 0
                    else vertical_offset + vertical_tolerance_adjustment
                ),
                top_taper_distance=taper_offset,
                top_scarf_offset=scarf_offset
                - (0 if vertical_offset >= 0 else vertical_scarf_offset),
                tolerance=tolerance,
                slot_count=slot_count,
                depth=depth,
                linear_offset=linear_offset,
                tail_angle_offset=tail_angle_offset,
                length_ratio=length_ratio,
                depth_ratio=depth_ratio,
                straighten_dovetail=False,
            )
        )
        if vertical_offset < 0:
            current_floor = part.bounding_box().max.Z + (
                0
                if vertical_offset >= 0
                else vertical_offset + vertical_tolerance_adjustment
            )
            add(
                subpart_section(
                    start=start,
                    end=end,
                    max_dimension=max_dimension,
                    section=section,
                    style=style,
                    floor_z=current_floor,
                    floor_taper_distance=0,
                    floor_scarf_offset=scarf_offset - vertical_scarf_offset,
                    top_z=part.bounding_box().max.Z,
                    top_taper_distance=0,
                    top_scarf_offset=scarf_offset,
                    tolerance=tolerance,
                    slot_count=slot_count,
                    depth=depth,
                    linear_offset=linear_offset,
                    tail_angle_offset=tail_angle_offset,
                    length_ratio=length_ratio,
                    depth_ratio=depth_ratio,
                    straighten_dovetail=True,
                )
            )
        add(part, mode=Mode.INTERSECT)
        if click_fit_radius != 0:
            intersect.part = subpart_divots(
                subpart=intersect.part,
                start=start,
                end=end,
                section=section,
                style=style,
                tolerance=tolerance,
                vertical_tolerance=vertical_tolerance,
                scarf_angle=scarf_angle,
                linear_offset=linear_offset,
                taper_angle=taper_angle,
                depth_ratio=depth_ratio,
                length_ratio=length_ratio,
                vertical_offset=vertical_offset,
                click_fit_radius=click_fit_radius,
            )

    return intersect.part


def tslot_split_line(
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    slot_count: int = 1,
    depth: float = 2,
    tolerance: float = 0.1,
    taper_distance=0,
) -> Line:
    """
    given a start and end point, returns a tslot split line as a Line object
    -------
    arguments:
        - start: the start point for the dovetail line
        - end: the end point for the dovetail line
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
    """
    base_angle = start.angle_to(end)
    length = start.distance_to(end)
    base_width = depth * 2
    next_distance = (length - (base_width * slot_count)) / (slot_count + 1)
    dovetail_tolerance = (
        -(abs(tolerance / 2)) if section == DovetailPart.TAIL else abs(tolerance / 2)
    )

    adjusted_start_point = start.related_point(base_angle - 90, dovetail_tolerance)
    adjusted_end_point = adjusted_start_point.related_point(base_angle, length)

    last_point = adjusted_start_point

    with BuildLine() as tslot_outline:

        for slot_index in range(slot_count):
            root_start = last_point.related_point(base_angle, next_distance)
            trunk_start = root_start.related_point(
                base_angle, depth / 2 + dovetail_tolerance + taper_distance
            )
            branch_start = trunk_start.related_point(
                base_angle + 90, depth / 2 + dovetail_tolerance * 2 + taper_distance
            )
            mid_trunk_start = midpoint(trunk_start, branch_start)
            branch_start_inner = branch_start.related_point(base_angle, -depth / 2)
            branch_start_inner_mid = midpoint(branch_start_inner, branch_start)
            branch_start_outer = branch_start_inner.related_point(
                base_angle + 90, depth / 2 - dovetail_tolerance * 2 - taper_distance * 2
            )
            branch_start_mid = midpoint(branch_start_inner, branch_start_outer)
            branch_end_inner = branch_start_inner.related_point(
                base_angle, depth * 2 - dovetail_tolerance * 2 - taper_distance * 2
            )
            branch_end_outer = branch_start_outer.related_point(
                base_angle, depth * 2 - dovetail_tolerance * 2 - taper_distance * 2
            )
            branch_mid = midpoint(branch_start_outer, branch_end_outer)
            branch_end_mid = midpoint(branch_end_inner, branch_end_outer)
            branch_end = branch_start.related_point(
                base_angle, depth - dovetail_tolerance * 2 - taper_distance * 2
            )
            branch_end_inner_mid = midpoint(branch_end_inner, branch_end)
            trunk_end = trunk_start.related_point(
                base_angle, depth - dovetail_tolerance * 2 - taper_distance * 2
            )
            mid_trunk_end = midpoint(trunk_end, branch_end)

            root_end = root_start.related_point(base_angle, depth * 2)
            FilletPolyline(
                last_point,
                trunk_start,
                mid_trunk_start,
                radius=abs(tolerance) * (2 if section == DovetailPart.TAIL else 3),
            )
            FilletPolyline(
                mid_trunk_start,
                branch_start,
                branch_start_inner_mid,
                radius=abs(tolerance) * (2 if section == DovetailPart.TAIL else 3),
            )
            FilletPolyline(
                branch_start_inner_mid,
                branch_start_inner,
                branch_start_mid,
                radius=abs(tolerance) * (3 if section == DovetailPart.TAIL else 2),
            )
            FilletPolyline(
                branch_start_mid,
                branch_start_outer,
                branch_mid,
                radius=abs(tolerance) * (3 if section == DovetailPart.TAIL else 2),
            )
            FilletPolyline(
                branch_mid,
                branch_end_outer,
                branch_end_mid,
                radius=abs(tolerance) * (3 if section == DovetailPart.TAIL else 2),
            )
            FilletPolyline(
                branch_end_mid,
                branch_end_inner,
                branch_end_inner_mid,
                radius=abs(tolerance) * (3 if section == DovetailPart.TAIL else 2),
            )
            FilletPolyline(
                branch_end_inner_mid,
                branch_end,
                mid_trunk_end,
                radius=abs(tolerance) * (2 if section == DovetailPart.TAIL else 3),
            )
            FilletPolyline(
                mid_trunk_end,
                trunk_end,
                root_end,
                radius=abs(tolerance) * (2 if section == DovetailPart.TAIL else 3),
            )
            last_point = root_end
        Polyline(last_point, adjusted_end_point)
    return tslot_outline.line


def dovetail_split_line(
    start: Point,
    end: Point,
    section: DovetailPart = DovetailPart.TAIL,
    linear_offset: float = 0,
    tolerance: float = 0.025,
    tail_angle_offset: float = 15,
    taper_distance: float = 0,
    length_ratio: float = 1 / 3,
    depth_ratio: float = 1 / 6,
) -> Line:
    """
    given a start and end point, returns a dovetail split line as a Line object
    -------
    arguments:
        - start: the start point for the dovetail line
        - end: the end point for the dovetail line
        - section: the section of the dovetail to create (DovetailPart.TAIL or DovetailPart.SOCKET)
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
    """
    dovetail_tolerance = (
        -(abs(tolerance / 2)) if section == DovetailPart.TAIL else abs(tolerance / 2)
    )

    base_angle = start.angle_to(end)
    tail_angle_tolerance_adjustment = dovetail_tolerance * tan(
        radians(tail_angle_offset)
    )
    base_angle = start.angle_to(end)
    length = start.distance_to(end)
    tongue_length = length * length_ratio + (dovetail_tolerance * 2)
    tongue_depth = length * depth_ratio
    tail_angle_extension = (tongue_depth) * tan(radians(tail_angle_offset))
    adjusted_start_point = start.related_point(base_angle - 90, dovetail_tolerance)

    tail_end_start = adjusted_start_point.related_point(
        base_angle,
        length / 2
        - tongue_length / 2
        - tail_angle_tolerance_adjustment
        + linear_offset
        + taper_distance,
    ).related_point(base_angle - 90, tongue_depth - taper_distance / 2)

    tail_end = adjusted_start_point.related_point(
        base_angle,
        length / 2
        + tongue_length / 2
        + tail_angle_tolerance_adjustment
        + linear_offset
        - taper_distance,
    ).related_point(base_angle - 90, tongue_depth - taper_distance / 2)

    tail_base_start = adjusted_start_point.related_point(
        base_angle,
        length / 2
        - tongue_length / 2
        + tail_angle_extension
        - tail_angle_tolerance_adjustment
        + linear_offset
        + taper_distance / 2,
    )

    tail_base_resume = adjusted_start_point.related_point(
        base_angle,
        length / 2
        + tongue_length / 2
        - tail_angle_extension
        + tail_angle_tolerance_adjustment
        + linear_offset
        - taper_distance / 2,
    )

    adjusted_end_point = adjusted_start_point.related_point(base_angle, length)

    with BuildLine() as dovetail_outline:
        FilletPolyline(
            adjusted_start_point,
            tail_base_start,
            midpoint(tail_base_start, tail_end_start),
            radius=abs(dovetail_tolerance) * (2 if section == DovetailPart.TAIL else 3),
        )
        FilletPolyline(
            midpoint(tail_base_start, tail_end_start),
            tail_end_start,
            midpoint(tail_end_start, tail_end),
            radius=abs(dovetail_tolerance) * (3 if section == DovetailPart.TAIL else 2),
        )
        FilletPolyline(
            midpoint(tail_end_start, tail_end),
            tail_end,
            midpoint(tail_end, tail_base_resume),
            radius=abs(dovetail_tolerance) * (3 if section == DovetailPart.TAIL else 2),
        )
        FilletPolyline(
            midpoint(tail_end, tail_base_resume),
            tail_base_resume,
            adjusted_end_point,
            radius=abs(dovetail_tolerance) * (2 if section == DovetailPart.TAIL else 3),
        )

    return dovetail_outline.line


# if __name__ == "__main__":
#     from ocp_vscode import show, Camera
#     with BuildPart(mode=Mode.PRIVATE) as test:
#         Box(40, 200, 78.7, align=(Align.CENTER, Align.CENTER, Align.MIN))

#     splines = snugtail_subpart_outline(
#         test.part,
#         Point(-20, 0),
#         Point(20, 0),
#         section=DovetailPart.SOCKET,
#         taper_distance=0,
#         tolerance=0.8,
#         length_ratio=.6,
#         depth_ratio=.3,
#         tail_angle_offset=35,
#         # scarf_angle=20,
#         # straighten_dovetail=True,
#     )
#     spline = snugtail_subpart_outline(
#         test.part,
#         Point(-20, 0),
#         Point(20, 0),
#         section=DovetailPart.TAIL,
#         taper_distance=4,
#         tolerance=0.8,
#         length_ratio=.6,
#         depth_ratio=.3,
#         tail_angle_offset=35,
#         # scarf_angle=20,
#         # straighten_dovetail=True,
#     )
#     splines.color = (0.5, 0.5, 0.5)

#     show(spline, splines, reset_camera=Camera.KEEP)

if __name__ == "__main__":
    from ocp_vscode import show, Camera

    with BuildPart(mode=Mode.PRIVATE) as test:
        Box(40, 200, 78.7, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with BuildPart(
            Plane.XY.offset(73.6),
            mode=Mode.SUBTRACT,
        ):
            Cylinder(
                25,
                200,
                rotation=(90, 0, 0),
            )

    tl = dovetail_subpart(
        test.part,
        Point(-20, 0),
        Point(20, 0),
        section=DovetailPart.TAIL,
        style=DovetailStyle.T_SLOT,
        tolerance=0.1,
        depth=2,
        slot_count=1,
        taper_angle=0.25,
        scarf_angle=2,
        vertical_offset=-14.33333,
        tail_angle_offset=25,
        length_ratio=0.7,
        depth_ratio=0.3,
    ).move(Location((0, 0, 0)))
    sckt = dovetail_subpart(
        test.part,
        Point(-20, 0),
        Point(20, 0),
        section=DovetailPart.SOCKET,
        style=DovetailStyle.T_SLOT,
        tolerance=0.1,
        depth=2,
        slot_count=1,
        taper_angle=0.25,
        scarf_angle=2,
        vertical_offset=-14.33333,
        tail_angle_offset=25,
        length_ratio=0.7,
        depth_ratio=0.3,
    )
    sckt.color = (0.5, 0.5, 0.5)
    splines = dovetail_subpart_outline(
        Point(-20, 0),
        Point(20, 0),
        section=DovetailPart.SOCKET,
        style=DovetailStyle.T_SLOT,
        taper_distance=0,
        tolerance=0.1,
        length_ratio=0.6,
        depth_ratio=0.3,
        tail_angle_offset=35,
        slot_count=1,
        depth=2,
        # scarf_angle=20,
        # straighten_dovetail=True,
    )
    spline = dovetail_subpart_outline(
        Point(-20, 0),
        Point(20, 0),
        section=DovetailPart.TAIL,
        style=DovetailStyle.T_SLOT,
        taper_distance=0,
        tolerance=0.1,
        length_ratio=0.6,
        depth_ratio=0.3,
        tail_angle_offset=35,
        slot_count=1,
        depth=2,
        # scarf_angle=20,
        # straighten_dovetail=True,
    )
    # spline = snugtail_subpart_outline(
    #     Point(-20, 0),
    #     Point(20, 0),
    #     section=DovetailPart.TAIL,
    #     taper_distance=0,
    #     tolerance=0.8,
    #     length_ratio=0.6,
    #     depth_ratio=0.3,
    #     tail_angle_offset=35,
    #     # scarf_angle=20,
    #     # straighten_dovetail=True,
    # )
    # splines = dovetail_subpart_outline(
    #     test.part,
    #     Point(-20, 0),
    #     Point(20, 0),
    #     section=DovetailPart.SOCKET,
    #     taper_distance=0,
    #     tolerance=0.8,
    #     length_ratio=.6,
    #     depth_ratio=.3,
    #     tail_angle_offset=35,
    #     # scarf_angle=20,
    #     # straighten_dovetail=True,
    # )
    # spline = dovetail_subpart_outline(
    #     test.part,
    #     Point(-20, 0),
    #     Point(20, 0),
    #     section=DovetailPart.TAIL,
    #     taper_distance=0,
    #     tolerance=0.8,
    #     length_ratio=.6,
    #     depth_ratio=.3,
    #     tail_angle_offset=35,
    #     # scarf_angle=20,
    #     # straighten_dovetail=True,
    # )
    splines.color = (0.5, 0.5, 0.5)
    with BuildSketch() as sks:
        add(splines)
        make_face()
    sks.color = (0.5, 0.5, 0.5)
    with BuildSketch() as sk:
        add(spline)
        make_face()
    from build123d import export_stl

    show(
        tl,
        sckt,
        # sk,
        # sks,
        # spline,
        # splines,
        reset_camera=Camera.KEEP,
    )
    # export_stl(tl, "tail.stl")
    # export_stl(sckt, "socket.stl")
