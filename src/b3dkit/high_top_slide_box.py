from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Compound,
    GridLocations,
    Location,
    Part,
    PolarLocations,
    Polyline,
    Mode,
    add,
    extrude,
    fillet,
    make_face,
    pack,
)
from dataclasses import field
from b3dkit.point import Point, midpoint
from b3dkit.basic_shapes import (
    DiamondCylinder,
    opposite_length,
)
from b3dkit.click_fit import Divot

from ocp_vscode import show, Camera


def _slide_top_rail_cut(
    part_width: float,
    part_depth: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    effective_tolerance: float = 0.05,
):
    """
    Creates the rail cut geometry for the sliding mechanism of a high top slide box.

    This internal function generates the precise cut pattern needed for the sliding rails,
    including diamond-shaped guides and tolerance adjustments. The rails allow smooth
    sliding motion while maintaining secure positioning.

    args:
        - part_width: the width of the base part in millimeters
        - part_depth: the depth of the base part in millimeters
        - rail_height: the height of the rail system in millimeters
        - wall_thickness: the thickness of the box walls in millimeters
        - rail_angle: the angle of the rails in degrees for improved sliding
        - effective_tolerance: the calculated tolerance for the sliding fit
    """
    rail_front_right = Point(
        (part_width - wall_thickness * 2 / 3 + effective_tolerance) / 2,
        (part_depth - wall_thickness) / 2,
    )
    rail_back_right = Point(
        (
            rail_front_right.x
            - (
                0
                if (rail_angle == 0)
                else opposite_length(
                    rail_angle, adjacent_length=part_depth - wall_thickness
                )
            )
        ),
        -(part_depth - wall_thickness) / 2,
    )

    with BuildPart(
        Location((0, wall_thickness / 2, 0)),
        mode=Mode.SUBTRACT,
    ) as rail_cut:
        with BuildSketch(Location((0, wall_thickness / 2))):
            with BuildLine():

                Polyline(
                    rail_front_right,
                    rail_back_right,
                    Point(-(rail_back_right.x), rail_back_right.y),
                    Point(-(rail_front_right.x), rail_front_right.y),
                    rail_front_right,
                )
            make_face()
        extrude(amount=rail_height)
        guide_radius = wall_thickness / 3 - effective_tolerance / 2
        with BuildPart(
            (
                Location(
                    (
                        rail_front_right.x,
                        rail_front_right.y + wall_thickness / 2,
                        rail_height,
                    )
                )
            ),
            mode=Mode.ADD,
        ):
            DiamondCylinder(
                radius=wall_thickness - effective_tolerance / 2,
                height=part_depth - wall_thickness,
                align=(Align.MAX, Align.CENTER, Align.MIN),
                rotation=(90, 0, -rail_angle),
            )
        with BuildPart(
            (
                Location(
                    (
                        -rail_front_right.x,
                        rail_front_right.y + wall_thickness / 2,
                        rail_height,
                    )
                )
            ),
            mode=Mode.ADD,
        ):
            DiamondCylinder(
                radius=wall_thickness - effective_tolerance / 2,
                height=part_depth - wall_thickness,
                align=(Align.MIN, Align.CENTER, Align.MIN),
                rotation=(90, 0, rail_angle),
            )

        with BuildPart(
            (
                Location(
                    (
                        rail_front_right.x,
                        rail_front_right.y + wall_thickness / 2,
                        rail_height / 2 - effective_tolerance,
                    )
                )
            ),
            mode=Mode.SUBTRACT,
        ):
            DiamondCylinder(
                radius=guide_radius,
                height=part_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                rotation=(90, 0, -rail_angle),
            )
        with BuildPart(
            (
                Location(
                    (
                        -rail_front_right.x,
                        rail_front_right.y + wall_thickness / 2,
                        rail_height / 2 - effective_tolerance,
                    )
                )
            ),
            mode=Mode.SUBTRACT,
        ):
            DiamondCylinder(
                radius=guide_radius,
                height=part_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                rotation=(90, 0, rail_angle),
            )

    return rail_cut.part


def _high_top_slide_box_top(
    base_part: Part,
    top_height: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    divot_radius: float = 0.5,
    thumb_radius: float = 0,
    tolerance: float = 0.2,
    cut_template: bool = False,
) -> Part:
    """
    Creates the top component for a high top slide box with rails and optional divots.

    This internal function generates either the actual sliding lid or a template for cutting
    the base, depending on the cut_template parameter. It includes rail geometry, divots for
    positioning feedback, and proper tolerance adjustments.

    args:
        - base_part: the base part that defines the outer dimensions
        - top_height: the height of the sliding top portion in millimeters
        - rail_height: the height of the rail system in millimeters
        - wall_thickness: the thickness of the box walls in millimeters
        - rail_angle: the angle of the rails in degrees for smoother sliding
        - divot_radius: the radius of positioning divots, set to 0 to disable
        - thumb_radius: the radius for thumb grips (currently unused)
        - tolerance: the clearance between moving parts in millimeters
        - cut_template: whether this is for cutting (True) or building the lid (False)
    """
    effective_tolerance = abs(tolerance) / (-2 if cut_template else 2)
    with BuildPart() as top:
        part_width = base_part.bounding_box().size.X
        part_depth = base_part.bounding_box().size.Y
        part_height = base_part.bounding_box().size.Z
        part_max_dimension = max(part_width, part_depth, part_height)
        with BuildPart(
            Location(
                (
                    0,
                    0,
                    -part_height
                    + top_height
                    + rail_height
                    + wall_thickness
                    - effective_tolerance * 4,
                )
            )
        ):
            add(base_part)
            with BuildPart(mode=Mode.INTERSECT):
                Box(
                    part_max_dimension,
                    part_max_dimension,
                    part_max_dimension,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
        with BuildPart(
            Location((0, wall_thickness / 2, rail_height)),
            mode=Mode.SUBTRACT,
        ) as top_cut:
            Box(
                part_width - wall_thickness * 2 + effective_tolerance * 2,
                part_depth - wall_thickness,
                top_height,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        with BuildPart(
            Location((0, 0, 0)),
            mode=Mode.SUBTRACT,
        ) as rail_cut:
            add(
                _slide_top_rail_cut(
                    part_width=part_width,
                    part_depth=part_depth,
                    rail_height=rail_height,
                    wall_thickness=wall_thickness,
                    rail_angle=rail_angle,
                    effective_tolerance=effective_tolerance,
                )
            )
        if divot_radius > 0:
            with BuildPart(
                Location(
                    (0, (part_depth - wall_thickness) / 2, top_height + rail_height),
                    (180, 0, 0),
                ),
            ):
                with PolarLocations(radius=part_width / 3 - wall_thickness, count=2):
                    Divot(
                        radius=divot_radius,
                        positive=not cut_template,
                        extend_base=True,
                    )

            with BuildPart(
                Location(
                    (0, (-part_depth + wall_thickness) / 2, 0),
                    (180, 0, 0),
                ),
            ):
                with PolarLocations(radius=part_width / 3 - wall_thickness, count=2):
                    Divot(
                        radius=divot_radius,
                        positive=not cut_template,
                        extend_base=True,
                    )
    top.part.label = "lid"
    return top.part


def high_top_slide_box_lid(
    base_part: Part,
    top_height: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    divot_radius: float = 0.5,
    thumb_radius: float = 0,
    tolerance: float = 0.2,
) -> Part:
    """
    Creates the sliding lid component for a high top slide box.

    The lid features rails that slide smoothly into the base component, with optional
    divots for tactile positioning feedback. The lid maintains the top portion of the
    original part while adding the necessary sliding mechanism.

    args:
        - base_part: the base part that defines the outer dimensions
        - top_height: the height of the sliding top portion in millimeters
        - rail_height: the height of the rail system in millimeters
        - wall_thickness: the thickness of the box walls in millimeters
        - rail_angle: the angle of the rails in degrees for smoother sliding
        - divot_radius: the radius of positioning divots, set to 0 to disable
        - thumb_radius: the radius for thumb grips (currently unused)
        - tolerance: the clearance between moving parts in millimeters
    """
    lid = _high_top_slide_box_top(
        base_part,
        top_height,
        rail_height,
        wall_thickness,
        rail_angle,
        divot_radius,
        thumb_radius,
        tolerance,
        cut_template=False,
    )
    lid.label = "box top"
    return lid


def high_top_slide_box_base(
    base_part: Part,
    top_height: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    divot_radius: float = 0.5,
    thumb_radius: float = 0,
    tolerance: float = 0.2,
) -> Part:
    """
    Creates the base component for a high top slide box with rail channels.

    The base is hollowed out to create storage space and includes channels that receive
    the sliding lid's rails. Diamond-shaped guide cylinders help ensure smooth operation
    and proper alignment of the sliding mechanism.

    args:
        - base_part: the base part that defines the outer dimensions
        - top_height: the height of the sliding top portion in millimeters
        - rail_height: the height of the rail system in millimeters
        - wall_thickness: the thickness of the box walls in millimeters
        - rail_angle: the angle of the rails in degrees for smoother sliding
        - divot_radius: the radius of positioning divots, set to 0 to disable
        - thumb_radius: the radius for thumb grips (currently unused)
        - tolerance: the clearance between moving parts in millimeters
    """
    part_width = base_part.bounding_box().size.X
    part_depth = base_part.bounding_box().size.Y
    part_height = base_part.bounding_box().size.Z

    with BuildPart() as boxbottom:
        add(base_part)
        with BuildPart(
            Location(
                (
                    0,
                    0,
                    wall_thickness,
                ),
                (0, 0, 0),
            ),
            mode=Mode.SUBTRACT,
        ):
            Box(
                part_width - wall_thickness * 2,
                part_depth - wall_thickness * 2,
                part_height - wall_thickness,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        with BuildPart(
            Location(
                (
                    0,
                    0,
                    part_height
                    - top_height
                    - rail_height
                    - wall_thickness
                    + tolerance * 2,
                ),
                (0, 0, 0),
            ),
            mode=Mode.SUBTRACT,
        ):
            add(
                _high_top_slide_box_top(
                    base_part,
                    top_height,
                    rail_height,
                    wall_thickness,
                    rail_angle,
                    divot_radius,
                    thumb_radius,
                    tolerance,
                    cut_template=True,
                )
            )
        with BuildPart(
            Location(
                (
                    0,
                    -part_depth / 2 + wall_thickness,
                    part_height
                    - top_height
                    - rail_height
                    - wall_thickness
                    + tolerance * 2,
                )
            ),
            mode=Mode.SUBTRACT,
        ):
            with GridLocations(part_width, 0, 2, 1) as grid_locs:
                DiamondCylinder(
                    radius=wall_thickness,
                    height=part_height * 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

    boxbottom.part.label = "box bottom"
    return boxbottom.part


def high_top_slide_box(
    base_part: Part,
    top_height: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    divot_radius: float = 0.5,
    thumb_radius: float = 0,
    tolerance: float = 0.2,
) -> Compound:
    """
    Creates a complete high top slide box with both lid and base components.

    This function generates a sliding box system where the lid has significant height
    and slides on rails into the base. The system uses diamond-shaped rails for smooth
    operation and includes optional divots for positioning feedback. The lid is automatically
    oriented for 3D printing.

    args:
        - base_part: the base part that defines the outer dimensions of the box
        - top_height: the height of the sliding top portion in millimeters
        - rail_height: the height of the rail system that guides sliding motion
        - wall_thickness: the thickness of the box walls in millimeters
        - rail_angle: the angle of the rails in degrees for smoother sliding
        - divot_radius: the radius of positioning divots, set to 0 to disable
        - thumb_radius: the radius for thumb grips (currently unused)
        - tolerance: the clearance between moving parts in millimeters
    """

    return Compound(
        label="slide box",
        children=[
            high_top_slide_box_lid(
                base_part=base_part,
                top_height=top_height,
                rail_height=rail_height,
                wall_thickness=wall_thickness,
                rail_angle=rail_angle,
                divot_radius=divot_radius,
                thumb_radius=thumb_radius,
                tolerance=tolerance,
            ).rotate(Axis.X, 180),
            high_top_slide_box_base(
                base_part=base_part,
                top_height=top_height,
                rail_height=rail_height,
                wall_thickness=wall_thickness,
                rail_angle=rail_angle,
                divot_radius=divot_radius,
                thumb_radius=thumb_radius,
                tolerance=tolerance,
            ),
        ],
    )


if __name__ == "__main__":
    with BuildPart() as base_box:
        Box(44, 44, 44, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(base_box.part.edges().filter_by(Axis.Z), radius=1.5)

    sb = high_top_slide_box(
        base_part=base_box.part,
        top_height=5,
        rail_height=10,
        wall_thickness=4,
        rail_angle=0.5,
        divot_radius=0.5,
        thumb_radius=0,
        tolerance=0.1,
    )
    top = (
        sb.children[0].move(Location((0, 0, 19)))
        # .rotate(Axis.Z, 180)
        # .rotate(Axis.Y, 180)
        # .move(Location((-44 - 5, 44, sb.children[1].bounding_box().size.Z + 4 - 0.1)))
    )
    # show(sb, reset_camera=Camera.KEEP)
    show(
        pack([top, sb.children[1]], padding=5, align_z=True),
        reset_camera=Camera.KEEP,
    )
