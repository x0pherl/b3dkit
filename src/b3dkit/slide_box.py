from math import radians, tan

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Color,
    Compound,
    Cylinder,
    GridLocations,
    Location,
    Mode,
    Part,
    Plane,
    Sketch,
    add,
    extrude,
    fillet,
    offset,
    pack,
    section,
)
from ocp_vscode import Camera, show

from b3dkit.click_fit import Divot

#: the draft applied to the sliding faces; the divot placement below depends on
#: this matching the taper passed to extrude()
_SLIDER_TAPER_ANGLE = 22.5


__all__ = [
    "slide_lid",
    "slide_box",
]


def _divot_spacing(
    sketch_width: float,
    wall_thickness: float,
    tolerance: float,
    x_straighten_distance: float,
    divot_radius: float,
) -> float:
    """
    Determine the x distance between the pair of divots on a slider template.

    The divots would naturally sit one wall thickness inboard of the sketch, but
    the sliding faces are tapered, so the widest part of a divot -- the top of its
    extended base, one radius above the underside of the rail -- can graze the
    tapered face. A grazing intersection leaves needle-thin slivers behind the
    boolean, so pull the pair far enough inboard that a divot only ever meets the
    flat underside.
    """
    half_width = sketch_width / 2
    # depth below the top of the template at the widest point of the divot
    widest_depth = max(wall_thickness - divot_radius, 0)
    tapered_face = (
        half_width
        - wall_thickness
        - abs(tolerance)
        + widest_depth * tan(radians(_SLIDER_TAPER_ANGLE))
    )
    return (
        min(
            half_width - x_straighten_distance - wall_thickness,
            tapered_face - divot_radius - divot_radius / 5,
        )
        * 2
    )


def _slider_template(
    sketch: Sketch,
    wall_thickness: float = 2,
    tolerance: float = 0.2,
    top_offset: float = 0,
    x_straighten_distance: float = 0,
    divot_radius: float = 0,
    cut_template: bool = True,
) -> Part:
    """
    Create a slider part based on a sketch.
    """
    with BuildPart() as slider_part:
        with BuildSketch() as top_sketch:
            offset(sketch, amount=-abs(tolerance) - (abs(wall_thickness)))
        extrude(
            top_sketch.sketch,
            amount=-wall_thickness - abs(tolerance),
            taper=-_SLIDER_TAPER_ANGLE,
        )
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
            # a divot wider than half the wall would overhang the open front of
            # the template; keep it far enough back to meet only the underside
            divot_y = max(
                sketch.bounding_box().min.Y + wall_thickness / 2,
                slider_part.part.bounding_box().min.Y + divot_radius + divot_radius / 5,
            )
            with BuildPart(
                Location((0, divot_y, -wall_thickness), (180, 0, 0)),
                mode=Mode.ADD,
            ):
                with GridLocations(
                    _divot_spacing(
                        sketch.bounding_box().size.X,
                        wall_thickness,
                        tolerance,
                        x_straighten_distance,
                        divot_radius,
                    ),
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
    tolerance: float = 0.15,
    top_offset: float = 0,
    thumb_radius: float = 5,
    x_straighten_distance: float = 0,
    divot_radius: float = 0,
) -> Part:

    cross_section = section(
        obj=part, section_by=Plane.XY.offset(part.bounding_box().max.Z - top_offset)
    )
    lid_template = _slider_template(
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
    slide_tolerance: float = 0.15,
    divot_radius: float = 0,
) -> Compound:

    cross_section = section(
        obj=part, section_by=Plane.XY.offset(part.bounding_box().max.Z - top_offset)
    )
    lid_cut_template = _slider_template(
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
