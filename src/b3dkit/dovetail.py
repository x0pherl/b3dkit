from enum import Enum, auto
from math import radians, tan

from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Cylinder,
    FilletPolyline,
    Line,
    Location,
    Mode,
    Part,
    Plane,
    PolarLocations,
    Polyline,
    add,
    loft,
    make_face,
)

# it's a bad habit, but I keep some simple test code under __main__
# to make creating test object easy -- this adds ".b3dkit" to the path
if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from b3dkit.click_fit import Divot
from b3dkit.point import (
    Point,
    midpoint,
    shifted_midpoint,
)

__all__ = [
    "DovetailSubpart",
    "DovetailStyle",
    "dovetail_subpart",
    "dovetail_split",
]


class DovetailSubpart(Enum):
    TAIL = auto()
    SOCKET = auto()


class DovetailStyle(Enum):
    TRADITIONAL = auto()
    SNUGTAIL = auto()
    T_SLOT = auto()


def _subpart_outline_boundary(
    start: Point,
    end: Point,
    max_dimension: float,
    subpart: DovetailSubpart = DovetailSubpart.TAIL,
    tolerance: float = 0.1,
    scarf_offset: float = 0,
) -> Line:
    direction_multiplier = 1 if subpart == DovetailSubpart.TAIL else -1
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


def _snugtail_subpart_outline(
    start: Point,
    end: Point,
    max_dimension: float = 1000,
    subpart: DovetailSubpart = DovetailSubpart.TAIL,
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
        - subpart: which subpart to create (DovetailSubpart.TAIL or DovetailSubpart.SOCKET)
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - scarf_offset: setting this to a non-zero value will shift the dovetail to allow for tilt adjustemnt between the top & bottom outlines
        - straighten_dovetail: setting this to True will draw the straight line of the cut,
            allowing for the correct tolerances for the subpart
    """
    if (length_ratio + depth_ratio > 1) and not straighten_dovetail:
        raise ValueError(
            "the combined length_ratio and depth_ratio must be not exceed 1"
        )

    direction_multiplier = 1 if subpart == DovetailSubpart.TAIL else -1
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
        abs(dovetail_tolerance) * (4 if subpart == DovetailSubpart.TAIL else 6)
        - dovetail_tolerance * 2,
    )

    end_tail_line = fin_disconnect.related_point(
        opposite_angle,
        abs(dovetail_tolerance) * (4 if subpart == DovetailSubpart.TAIL else 6)
        - dovetail_tolerance * 2,
    )

    with BuildLine() as tail_line:
        add(
            _subpart_outline_boundary(
                start=start,
                end=end,
                max_dimension=max_dimension,
                subpart=subpart,
                tolerance=tolerance,
                scarf_offset=scarf_offset,
            )
        )

        FilletPolyline(
            *[cut_start, fin_join, start_fin],
            radius=abs(dovetail_tolerance)
            * (3 if subpart == DovetailSubpart.TAIL else 2),
        )
        if straighten_dovetail:
            Line(start_fin, start_snugtail)
        else:
            add(
                _dovetail_split_line(
                    start=start_fin.related_point(base_angle, -dovetail_tolerance),
                    end=start_snugtail.related_point(base_angle, -dovetail_tolerance),
                    linear_offset=-tail_depth / 2,
                    subpart=subpart,
                    tolerance=tolerance,
                    tail_angle_offset=tail_angle_offset,
                    taper_distance=taper_distance,
                    length_ratio=length_ratio,
                    depth_ratio=depth_ratio,
                )
            )
        FilletPolyline(
            *[start_snugtail, fin_connect, start_tail_line],
            radius=abs(dovetail_tolerance)
            * (2 if subpart == DovetailSubpart.TAIL else 3),
        )
        if straighten_dovetail:
            Line(
                start_tail_line,
                end_tail_line,
            )
        else:
            add(
                _dovetail_split_line(
                    start=start_tail_line.related_point(
                        base_angle - 90, -dovetail_tolerance
                    ),
                    end=end_tail_line.related_point(
                        base_angle - 90, -dovetail_tolerance
                    ),
                    subpart=subpart,
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
            radius=abs(dovetail_tolerance)
            * (2 if subpart == DovetailSubpart.TAIL else 3),
        )
        if straighten_dovetail:
            Line(end_snugtail, end_fin)
        else:
            add(
                _dovetail_split_line(
                    start=end_snugtail.related_point(base_angle, dovetail_tolerance),
                    end=end_fin.related_point(base_angle, dovetail_tolerance),
                    subpart=subpart,
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
            radius=abs(dovetail_tolerance)
            * (3 if subpart == DovetailSubpart.TAIL else 2),
        )
    return tail_line.line


def _dovetail_subpart_outline(
    start: Point,
    end: Point,
    max_dimension: float = 1000,
    subpart: DovetailSubpart = DovetailSubpart.TAIL,
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
        - subpart: which subpart to create (DovetailSubpart.TAIL or DovetailSubpart.SOCKET)
        - style: valid styles are DovetailStyle.TRADITIONAL, DovetailStyle.T_SLOT
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - scarf_offset: setting this to a non-zero value will shift the dovetail to allow for tilt adjustemnt between the top & bottom outlines
        - straighten_dovetail: setting this to True will draw the straight line of the cut,
            allowing for the correct tolerances for the subpart
    """
    if style not in (DovetailStyle.TRADITIONAL, DovetailStyle.T_SLOT):
        raise ValueError(f"Invalid style: {style}")
    direction_multiplier = 1 if subpart == DovetailSubpart.TAIL else -1
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
            _subpart_outline_boundary(
                start=start,
                end=end,
                max_dimension=max_dimension,
                subpart=subpart,
                tolerance=tolerance,
                scarf_offset=scarf_offset,
            )
        )
        if straighten_dovetail:
            Line(toleranced_start_point, toleranced_end_point)
        elif style == DovetailStyle.T_SLOT:
            add(
                _tslot_split_line(
                    start=adjusted_start_point,
                    end=adjusted_end_point,
                    subpart=subpart,
                    slot_count=slot_count,
                    depth=depth,
                    tolerance=tolerance,
                    taper_distance=taper_distance,
                )
            )
        else:
            add(
                _dovetail_split_line(
                    start=adjusted_start_point,
                    end=adjusted_end_point,
                    subpart=subpart,
                    linear_offset=linear_offset,
                    tolerance=tolerance,
                    tail_angle_offset=tail_angle_offset,
                    taper_distance=taper_distance,
                    length_ratio=length_ratio,
                    depth_ratio=depth_ratio,
                )
            )
    return tail_line.line


def _subpart_outline(
    start: Point,
    end: Point,
    max_dimension: float = 1000,
    subpart: DovetailSubpart = DovetailSubpart.TAIL,
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
        - subpart: which subpart to create (DovetailSubpart.TAIL or DovetailSubpart.SOCKET)
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
        - scarf_offset: setting this to a non-zero value will shift the dovetail to allow for tilt adjustemnt between the top & bottom outlines
        - straighten_dovetail: setting this to True will draw the straight line of the cut,
            allowing for the correct tolerances for the subpart
    """
    if style == DovetailStyle.SNUGTAIL:
        # NOTE: depth_ratio is deliberately NOT forwarded to snugtail. Commit f6c4b7b
        # ("changes to proportions after physical prototyping") rewrote snugtail's depth
        # model -- tail_depth was halved throughout and depth_ratio was removed from the
        # cut_length formulas outright -- so the parameter no longer means the same thing
        # it does for TRADITIONAL/T_SLOT. _snugtail_subpart_outline keeps its own
        # prototyped default (0.15). Forwarding it here would change the geometry of every
        # snugtail joint. This is not an oversight; do not "fix" it.
        return _snugtail_subpart_outline(
            start=start,
            end=end,
            max_dimension=max_dimension,
            subpart=subpart,
            tolerance=tolerance,
            tail_angle_offset=tail_angle_offset,
            taper_distance=taper_distance,
            length_ratio=length_ratio,
            scarf_offset=scarf_offset,
            straighten_dovetail=straighten_dovetail,
        )
    else:
        return _dovetail_subpart_outline(
            start=start,
            end=end,
            max_dimension=max_dimension,
            subpart=subpart,
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


def _traditional_subpart_divots(
    part: Part,
    start: Point,
    end: Point,
    subpart: DovetailSubpart = DovetailSubpart.TAIL,
    linear_offset: float = 0,
    tolerance: float = 0.025,
    vertical_tolerance: float = 0.2,
    scarf_angle: float = 0,
    taper_angle: float = 0,
    depth_ratio: float = 1 / 6,
    vertical_offset: float = 0,
    click_fit_radius: float = 0,
) -> Part:
    """
    adds/subtracts click-fit divots to part and returns it
    ----------
    Arguments:
        - part: the part to add divots to
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - subpart: which subpart to create (DovetailSubpart.TAIL or DovetailSubpart.SOCKET)
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
    scarf_offset = (part.bounding_box().size.Z) * tan(radians(scarf_angle)) / 2

    tailtop_z = part.bounding_box().max.Z + (
        vertical_offset if vertical_offset < 0 else 0
    )

    adjusted_top_divot_angle = scarf_angle - taper_angle

    taper_offset = (part.bounding_box().size.Z - abs(vertical_offset)) * tan(
        radians(adjusted_top_divot_angle)
    )

    topmode = (
        Mode.SUBTRACT
        if ((subpart == DovetailSubpart.TAIL) == (vertical_offset < 0))
        else Mode.ADD
    )
    bottommode = (
        Mode.ADD
        if ((subpart == DovetailSubpart.SOCKET) == (vertical_offset >= 0))
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
        add(part, mode=Mode.ADD)
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


def _snugtail_divots(
    part: Part,
    start: Point,
    end: Point,
    subpart: DovetailSubpart = DovetailSubpart.TAIL,
    tolerance: float = 0.025,
    scarf_angle: float = 0,
    depth_ratio: float = 1 / 10,
    length_ratio: float = 1 / 5,
    vertical_offset: float = 0,
    click_fit_radius: float = 0,
) -> Part:
    part_width = start.distance_to(end)
    direction_multiplier = -1 if subpart == DovetailSubpart.TAIL else 1
    inner_width = (
        part_width - (part_width * depth_ratio * 2) - (tolerance * direction_multiplier)
    )
    cut_angle = start.angle_to(end)
    with BuildPart() as divotedpart:
        add(part, mode=Mode.ADD)
        with BuildPart(
            Location(
                (
                    0,
                    part_width * length_ratio * 1.5 + midpoint(start, end).Y,
                    click_fit_radius * 2,
                )
            ),
            mode=Mode.SUBTRACT if subpart == DovetailSubpart.SOCKET else Mode.ADD,
        ):
            with PolarLocations(inner_width / 2, 2, start_angle=cut_angle):
                Divot(
                    radius=click_fit_radius,
                    positive=True,
                    extend_base=True,
                ).rotate(Axis.Y, -90)
    return divotedpart.part


def _subpart_divots(
    part: Part,
    start: Point,
    end: Point,
    subpart: DovetailSubpart = DovetailSubpart.TAIL,
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
) -> Part:
    """
    adds/subtracts click-fit divots to part and returns it
    ----------
    Arguments:
        - part: the part to add divots to
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - subpart: which subpart to create (DovetailSubpart.TAIL or DovetailSubpart.SOCKET)
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
        return _traditional_subpart_divots(
            part=part,
            start=start,
            end=end,
            subpart=subpart,
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
        # NOTE: these ratios are intentionally literal and independent of the joint's
        # depth_ratio/length_ratio. They position the click-fit divots, not the tail, and
        # have been fixed at these values since d4a42a9 ("fully integrated snugtail and
        # traditional dovetails"). The TRADITIONAL branch above forwards the joint ratios
        # because its divots scale with the tail; snugtail's do not. Do not "fix" this.
        return _snugtail_divots(
            part=part,
            start=start,
            end=end,
            subpart=subpart,
            tolerance=tolerance,
            scarf_angle=scarf_angle,
            depth_ratio=1 / 10,
            length_ratio=1 / 5,
            vertical_offset=vertical_offset,
            click_fit_radius=click_fit_radius,
        )


def _subpart_slab(
    start: Point,
    end: Point,
    max_dimension: float,
    subpart: DovetailSubpart = DovetailSubpart.TAIL,
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
    tail_angle_offset: float = 15,
    length_ratio: float = 1 / 3,
    depth_ratio: float = 1 / 6,
    straighten_dovetail: bool = False,
) -> Part:
    """
    lofts one Z-slab of a subpart between two Z heights, from the outline at each height

    Every shaping argument must be forwarded to both _subpart_outline calls -- the floor
    outline and the top outline have to describe the same joint or the loft between them
    is wrong. Historical note: b079844 extracted this helper out of dovetail_subpart and
    declared linear_offset, tail_angle_offset, length_ratio and depth_ratio here without
    passing them through, which silently disabled all four for every caller.

    args:
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - max_dimension: the maximum dimension of the part being split, used to size the outline
        - subpart: which subpart to create (DovetailSubpart.TAIL or DovetailSubpart.SOCKET)
        - style: the dovetail style; determines which shaping arguments apply
        - floor_z / top_z: the Z heights of the bottom and top outlines, in mm
        - floor_taper_distance / top_taper_distance: taper shrink applied at each height
        - floor_scarf_offset / top_scarf_offset: scarf shift applied at each height
        - tolerance: the tolerance for the split, in mm
        - slot_count, depth: T_SLOT shaping
        - linear_offset, tail_angle_offset, length_ratio, depth_ratio: tail shaping
        - straighten_dovetail: draw the straight line of the cut rather than the joint profile
    """
    with BuildPart() as intersect:
        with BuildSketch(Plane.XY.offset(floor_z)):
            with BuildLine() as baseline:
                add(
                    _subpart_outline(
                        start=start,
                        end=end,
                        max_dimension=max_dimension,
                        subpart=subpart,
                        style=style,
                        tolerance=tolerance,
                        taper_distance=floor_taper_distance,
                        slot_count=slot_count,
                        depth=depth,
                        linear_offset=linear_offset,
                        tail_angle_offset=tail_angle_offset,
                        length_ratio=length_ratio,
                        depth_ratio=depth_ratio,
                        scarf_offset=floor_scarf_offset,
                        straighten_dovetail=straighten_dovetail,
                    )
                )
            make_face()
        with BuildSketch(Plane.XY.offset(top_z)) as topline:
            with BuildLine():
                add(
                    _subpart_outline(
                        start=start,
                        end=end,
                        max_dimension=max_dimension,
                        subpart=subpart,
                        style=style,
                        tolerance=tolerance,
                        taper_distance=top_taper_distance,
                        slot_count=slot_count,
                        depth=depth,
                        linear_offset=linear_offset,
                        tail_angle_offset=tail_angle_offset,
                        length_ratio=length_ratio,
                        depth_ratio=depth_ratio,
                        scarf_offset=top_scarf_offset,
                        straighten_dovetail=straighten_dovetail,
                    )
                )
            make_face()
        loft()
    return intersect.part


#: which shaping arguments actually reach the outline for each style. Measured,
#: not assumed: a parameter absent here is accepted and then discarded, which is
#: how four documented knobs silently did nothing before 0.2.0.
_STYLE_PARAMETERS: dict[DovetailStyle, frozenset[str]] = {
    DovetailStyle.TRADITIONAL: frozenset(
        {"linear_offset", "tail_angle_offset", "length_ratio", "depth_ratio"}
    ),
    DovetailStyle.SNUGTAIL: frozenset({"tail_angle_offset", "length_ratio"}),
    DovetailStyle.T_SLOT: frozenset({"slot_count", "depth"}),
}

#: the default of each style-conditional argument, used to tell "not passed"
#: from "passed deliberately"
_STYLE_PARAMETER_DEFAULTS: dict[str, float] = {
    "linear_offset": 0,
    "tail_angle_offset": 15,
    "length_ratio": 1 / 3,
    "depth_ratio": 1 / 6,
    "slot_count": 1,
    "depth": 2,
}


def _reject_inert_parameters(style: DovetailStyle, **passed: float) -> None:
    """Raise if an argument was given that the chosen style would discard.

    Validation belongs here, at the public boundary, where style and every
    argument are visible in one frame. Raising from inside the dispatch would
    cover only part of the set and report from the wrong stack frame.
    """
    applies = _STYLE_PARAMETERS[style]
    for name, value in passed.items():
        if name in applies or value == _STYLE_PARAMETER_DEFAULTS[name]:
            continue
        used_by = sorted(
            other.name for other, params in _STYLE_PARAMETERS.items() if name in params
        )
        raise ValueError(
            f"{name}={value!r} has no effect for DovetailStyle.{style.name} and "
            f"would be silently ignored; it applies to: {', '.join(used_by)}"
        )


def dovetail_subpart(
    part: Part,
    start: Point,
    end: Point,
    subpart: DovetailSubpart = DovetailSubpart.TAIL,
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
    given a part and a start and end point on the XY plane, returns the requested subpart of the split
    args:
        - part: the part to split
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - subpart: which subpart to create (DovetailSubpart.TAIL or DovetailSubpart.SOCKET)
        - style: create a traditional dovetal or a cut that wraps around 3 sides of the object and creates a tighter fit
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified.
            TRADITIONAL only; slides the joint along the cut without changing its volume
        - tolerance: the tolerance for the split, in mm
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail),
            in degrees. TRADITIONAL and SNUGTAIL only
        - taper_angle: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail.
            TRADITIONAL and SNUGTAIL only
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail.
            TRADITIONAL only -- SNUGTAIL keeps its own prototyped 0.15, see _subpart_outline
        - slot_count: the number of slots to add. T_SLOT only
        - depth: the depth of the T-slot into the socket, in mm. T_SLOT only
        - scarf_angle: setting this to a non-zero value will tilt the dovetail along the Z axis which may improve part stability
        - vertical_offset: offsets the dovetail along the Z axis by the ammount specified, which results in a straight line
            cut on one side, and provides a hard stop for fitting. A positive number results in a straight cut on the bottom
            of the part passed, a negagive number results in a straight cut on the top of the part passed
    """
    _reject_inert_parameters(
        style,
        linear_offset=linear_offset,
        tail_angle_offset=tail_angle_offset,
        length_ratio=length_ratio,
        depth_ratio=depth_ratio,
        slot_count=slot_count,
        depth=depth,
    )
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
        * (1 if subpart == DovetailSubpart.TAIL else -1)
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
                _subpart_slab(
                    start=start,
                    end=end,
                    max_dimension=max_dimension,
                    subpart=subpart,
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
                    tail_angle_offset=tail_angle_offset,
                    length_ratio=length_ratio,
                    depth_ratio=depth_ratio,
                    straighten_dovetail=True,
                )
            )
        current_floor = (
            part.bounding_box().min.Z
            if vertical_offset <= 0
            else part.bounding_box().min.Z + abs(vertical_offset) + vertical_tolerance
        )
        add(
            _subpart_slab(
                start=start,
                end=end,
                max_dimension=max_dimension,
                subpart=subpart,
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
                _subpart_slab(
                    start=start,
                    end=end,
                    max_dimension=max_dimension,
                    subpart=subpart,
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
            intersect.part = _subpart_divots(
                part=intersect.part,
                start=start,
                end=end,
                subpart=subpart,
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


def dovetail_split(
    part: Part,
    start: Point,
    end: Point,
    **kwargs,
) -> tuple[Part, Part]:
    """
    split a part into a mating (tail, socket) pair from one set of arguments

    Both halves of a joint must be built from identical arguments; a single
    divergent value yields two subparts that are each valid and do not fit.
    Calling dovetail_subpart twice makes that divergence possible, so prefer
    this when you want both halves.

    args:
        - part: the part to split
        - start: the start point along the XY Plane for the dovetail line
        - end: the end point along the XY Plane for the dovetail line
        - **kwargs: any other argument accepted by dovetail_subpart, except
            subpart, which is supplied for each half

    returns a (tail, socket) tuple
    """
    if "subpart" in kwargs:
        raise TypeError(
            "dovetail_split() builds both subparts; pass dovetail_subpart() a "
            "subpart= argument instead if you only want one"
        )
    tail = dovetail_subpart(part, start, end, subpart=DovetailSubpart.TAIL, **kwargs)
    socket = dovetail_subpart(
        part, start, end, subpart=DovetailSubpart.SOCKET, **kwargs
    )
    return tail, socket


def _tslot_split_line(
    start: Point,
    end: Point,
    subpart: DovetailSubpart = DovetailSubpart.TAIL,
    slot_count: int = 1,
    depth: float = 2,
    tolerance: float = 0.1,
    taper_distance: float = 0,
) -> Line:
    """
    given a start and end point, returns a tslot split line as a Line object
    -------
    arguments:
        - start: the start point for the dovetail line
        - end: the end point for the dovetail line
        - subpart: which subpart to create (DovetailSubpart.TAIL or DovetailSubpart.SOCKET)
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
        -(abs(tolerance / 2)) if subpart == DovetailSubpart.TAIL else abs(tolerance / 2)
    )

    adjusted_start_point = start.related_point(base_angle - 90, dovetail_tolerance)
    adjusted_end_point = adjusted_start_point.related_point(base_angle, length)

    last_point = adjusted_start_point

    with BuildLine() as tslot_outline:

        for _slot_index in range(slot_count):
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
                radius=abs(tolerance) * (2 if subpart == DovetailSubpart.TAIL else 3),
            )
            FilletPolyline(
                mid_trunk_start,
                branch_start,
                branch_start_inner_mid,
                radius=abs(tolerance) * (2 if subpart == DovetailSubpart.TAIL else 3),
            )
            FilletPolyline(
                branch_start_inner_mid,
                branch_start_inner,
                branch_start_mid,
                radius=abs(tolerance) * (3 if subpart == DovetailSubpart.TAIL else 2),
            )
            FilletPolyline(
                branch_start_mid,
                branch_start_outer,
                branch_mid,
                radius=abs(tolerance) * (3 if subpart == DovetailSubpart.TAIL else 2),
            )
            FilletPolyline(
                branch_mid,
                branch_end_outer,
                branch_end_mid,
                radius=abs(tolerance) * (3 if subpart == DovetailSubpart.TAIL else 2),
            )
            FilletPolyline(
                branch_end_mid,
                branch_end_inner,
                branch_end_inner_mid,
                radius=abs(tolerance) * (3 if subpart == DovetailSubpart.TAIL else 2),
            )
            FilletPolyline(
                branch_end_inner_mid,
                branch_end,
                mid_trunk_end,
                radius=abs(tolerance) * (2 if subpart == DovetailSubpart.TAIL else 3),
            )
            FilletPolyline(
                mid_trunk_end,
                trunk_end,
                root_end,
                radius=abs(tolerance) * (2 if subpart == DovetailSubpart.TAIL else 3),
            )
            last_point = root_end
        Polyline(last_point, adjusted_end_point)
    return tslot_outline.line


def _dovetail_split_line(
    start: Point,
    end: Point,
    subpart: DovetailSubpart = DovetailSubpart.TAIL,
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
        - subpart: which subpart to create (DovetailSubpart.TAIL or DovetailSubpart.SOCKET)
        - linear_offset: offsets the center of the tail or socket along the line by the ammount specified
        - tolerance: the tolerance for the split
        - tail_angle_offset: the adjustment pitch of angle of the dovetail (0 will result in a square dovetail)
        - taper_distance: an extra shrinking factor for the dovetail size, allows for easier assembly
        - length_ratio: the ratio of the length of the tongue to the total length of the dovetail
        - depth_ratio: the ratio of the depth of the tongue to the total length of the dovetail
    """
    dovetail_tolerance = (
        -(abs(tolerance / 2)) if subpart == DovetailSubpart.TAIL else abs(tolerance / 2)
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
            radius=abs(dovetail_tolerance)
            * (2 if subpart == DovetailSubpart.TAIL else 3),
        )
        FilletPolyline(
            midpoint(tail_base_start, tail_end_start),
            tail_end_start,
            midpoint(tail_end_start, tail_end),
            radius=abs(dovetail_tolerance)
            * (3 if subpart == DovetailSubpart.TAIL else 2),
        )
        FilletPolyline(
            midpoint(tail_end_start, tail_end),
            tail_end,
            midpoint(tail_end, tail_base_resume),
            radius=abs(dovetail_tolerance)
            * (3 if subpart == DovetailSubpart.TAIL else 2),
        )
        FilletPolyline(
            midpoint(tail_end, tail_base_resume),
            tail_base_resume,
            adjusted_end_point,
            radius=abs(dovetail_tolerance)
            * (2 if subpart == DovetailSubpart.TAIL else 3),
        )

    return dovetail_outline.line


# if __name__ == "__main__":
#     from ocp_vscode import show, Camera
#     with BuildPart(mode=Mode.PRIVATE) as test:
#         Box(40, 200, 78.7, align=(Align.CENTER, Align.CENTER, Align.MIN))

#     splines = _snugtail_subpart_outline(
#         test.part,
#         Point(-20, 0),
#         Point(20, 0),
#         subpart=DovetailSubpart.SOCKET,
#         taper_distance=0,
#         tolerance=0.8,
#         length_ratio=.6,
#         depth_ratio=.3,
#         tail_angle_offset=35,
#         # scarf_angle=20,
#         # straighten_dovetail=True,
#     )
#     spline = _snugtail_subpart_outline(
#         test.part,
#         Point(-20, 0),
#         Point(20, 0),
#         subpart=DovetailSubpart.TAIL,
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
    from ocp_vscode import Camera, show

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
        subpart=DovetailSubpart.TAIL,
        style=DovetailStyle.T_SLOT,
        tolerance=0.1,
        depth=2,
        slot_count=1,
        taper_angle=0.25,
        scarf_angle=2,
        vertical_offset=-14.33333,
    ).move(Location((0, 0, 0)))
    sckt = dovetail_subpart(
        test.part,
        Point(-20, 0),
        Point(20, 0),
        subpart=DovetailSubpart.SOCKET,
        style=DovetailStyle.T_SLOT,
        tolerance=0.1,
        depth=2,
        slot_count=1,
        taper_angle=0.25,
        scarf_angle=2,
        vertical_offset=-14.33333,
    )
    sckt.color = (0.5, 0.5, 0.5)
    splines = _dovetail_subpart_outline(
        Point(-20, 0),
        Point(20, 0),
        subpart=DovetailSubpart.SOCKET,
        style=DovetailStyle.T_SLOT,
        taper_distance=0,
        tolerance=0.1,
        slot_count=1,
        depth=2,
        # scarf_angle=20,
        # straighten_dovetail=True,
    )
    spline = _dovetail_subpart_outline(
        Point(-20, 0),
        Point(20, 0),
        subpart=DovetailSubpart.TAIL,
        style=DovetailStyle.T_SLOT,
        taper_distance=0,
        tolerance=0.1,
        slot_count=1,
        depth=2,
        # scarf_angle=20,
        # straighten_dovetail=True,
    )
    # spline = _snugtail_subpart_outline(
    #     Point(-20, 0),
    #     Point(20, 0),
    #     subpart=DovetailSubpart.TAIL,
    #     taper_distance=0,
    #     tolerance=0.8,
    #     length_ratio=0.6,
    #     depth_ratio=0.3,
    #     tail_angle_offset=35,
    #     # scarf_angle=20,
    #     # straighten_dovetail=True,
    # )
    # splines = _dovetail_subpart_outline(
    #     test.part,
    #     Point(-20, 0),
    #     Point(20, 0),
    #     subpart=DovetailSubpart.SOCKET,
    #     taper_distance=0,
    #     tolerance=0.8,
    #     length_ratio=.6,
    #     depth_ratio=.3,
    #     tail_angle_offset=35,
    #     # scarf_angle=20,
    #     # straighten_dovetail=True,
    # )
    # spline = _dovetail_subpart_outline(
    #     test.part,
    #     Point(-20, 0),
    #     Point(20, 0),
    #     subpart=DovetailSubpart.TAIL,
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
