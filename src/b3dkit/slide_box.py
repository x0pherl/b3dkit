from build123d import (
    Align,
    BuildPart,
    Box,
    add,
    Color,
    fillet,
    offset,
    Mode,
    Plane,
    Part,
    Location,
    BuildSketch,
    extrude,
    Axis,
    Cylinder,
    pack,
    Compound,
    section,
    GridLocations,
    Sketch,
)


from ocp_vscode import show, Camera
from b3dkit import Divot


def slider_template(
    sketch: Sketch,
    wall_thickness: float = 2,
    tolerance=0.2,
    top_offset: float = 0,
    x_straighten_distance: float = 0,
    divot_radius=0,
    cut_template=True,
) -> Part:
    """
    Create a slider part based on a sketch.
    """
    with BuildPart() as slider_part:
        with BuildSketch() as top_sketch:
            offset(sketch, amount=-abs(tolerance) - (abs(wall_thickness)))
        extrude(top_sketch.sketch, amount=-wall_thickness - abs(tolerance), taper=-22.5)
        cross_section = section(
            obj=slider_part.part,
            section_by=Plane.XZ.offset(
                slider_part.part.bounding_box().max.Y
                - x_straighten_distance
                - wall_thickness
            ),
        )
        add(
            extrude(
                cross_section, amount=x_straighten_distance * 2 + wall_thickness * 2
            )
        )
        if divot_radius > 0:
            with BuildPart(
                Location(
                    (
                        0,
                        sketch.bounding_box().min.Y + wall_thickness / 2,
                        -wall_thickness,
                    ),
                    (180, 0, 0),
                ),
                mode=Mode.ADD,
            ):
                with GridLocations(
                    sketch.bounding_box().size.X
                    - x_straighten_distance * 2
                    - wall_thickness * 2,
                    0,
                    2,
                    1,
                ):
                    Divot(
                        radius=divot_radius,
                        positive=(not cut_template),
                        extend_base=True,
                    )

    return slider_part.part


def slide_lid(
    part: Part,
    wall_thickness: float = 2,
    tolerance=0.15,
    top_offset: float = 0,
    thumb_radius: float = 5,
    x_straighten_distance: float = 0,
    divot_radius=0,
) -> Part:

    cross_section = section(
        obj=part, section_by=Plane.XY.offset(part.bounding_box().max.Z - top_offset)
    )
    lid_template = slider_template(
        cross_section,
        wall_thickness,
        tolerance=tolerance,
        top_offset=top_offset,
        x_straighten_distance=x_straighten_distance,
        divot_radius=divot_radius,
        cut_template=False,
    )

    extrusion_height = part.bounding_box().max.Z - wall_thickness
    with BuildPart() as lid_part:
        add(part)
        add(
            lid_template.move(Location((0, 0, extrusion_height + wall_thickness))),
            mode=Mode.INTERSECT,
        )

        if thumb_radius > 0:
            with BuildPart(
                Location(
                    (
                        0,
                        lid_part.part.bounding_box().min.Y
                        + thumb_radius
                        + wall_thickness,
                        part.bounding_box().max.Z + wall_thickness / 4,
                    )
                ),
                mode=Mode.SUBTRACT,
            ):
                Cylinder(
                    radius=thumb_radius,
                    arc_size=180,
                    height=wall_thickness,
                    rotation=(15, 0, 0),
                )

    lid_part.part.label = "lid"

    return lid_part.part.move(Location((0, 0, 0), (0, 180, 0)))


# todo - handle top_offset for big fat slinding bits
# right now the logic works for the gobox because the top_offset (the height downward to get the fat bit)
# is equal to the thinness of the top plane because it's a nice even chamfer, but I can't assume that generically
def slide_box(
    part: Part,
    wall_thickness: float = 2,
    top_offset: float = 0,
    thumb_radius: float = 5,
    x_straighten_distance: float = 0,
    slide_tolerance=0.15,
    divot_radius: float = 0,
) -> Compound:

    cross_section = section(
        obj=part, section_by=Plane.XY.offset(part.bounding_box().max.Z - top_offset)
    )
    lid_cut_template = slider_template(
        cross_section,
        wall_thickness,
        tolerance=0,
        top_offset=top_offset,
        x_straighten_distance=x_straighten_distance,
        divot_radius=divot_radius,
    )

    extrusion_height = part.bounding_box().max.Z - wall_thickness
    with BuildPart() as box_part:
        add(part)
        extrude(
            offset(
                box_part.faces().sort_by(Axis.Z)[-1],
                amount=-abs(slide_tolerance) - abs(wall_thickness - top_offset),
            ),
            amount=-extrusion_height,
            mode=Mode.SUBTRACT,
        )
        add(
            lid_cut_template.move(Location((0, 0, extrusion_height + wall_thickness))),
            mode=Mode.SUBTRACT,
        )
    box_part.part.label = "box"

    lid = slide_lid(
        part,
        wall_thickness=wall_thickness,
        tolerance=slide_tolerance,
        top_offset=top_offset,
        thumb_radius=thumb_radius,
        x_straighten_distance=x_straighten_distance,
        divot_radius=divot_radius,
    )
    lid.label = "lid"
    lid.color = Color("red")

    box_assembly = Compound(
        label="slide box", children=pack([box_part.part, lid], padding=5, align_z=True)
    )

    return box_assembly


if __name__ == "__main__":
    with BuildPart() as base_box:
        Box(20, 44, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fillet(base_box.part.edges().filter_by(Axis.Z), radius=1.5)

    sb = slide_box(base_box.part, wall_thickness=2, thumb_radius=3.5, divot_radius=0.5)
    show(sb, reset_camera=Camera.KEEP)
