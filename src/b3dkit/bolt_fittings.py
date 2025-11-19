from typing import Union
from build123d import (
    Align,
    Axis,
    BasePartObject,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    GridLocations,
    Location,
    Mode,
    Part,
    Box,
    Plane,
    RegularPolygon,
    RotationLike,
    add,
    extrude,
    loft,
    tuplify,
    validate_inputs,
)
from b3dkit.antichamfer import anti_chamfer
from b3dkit.basic_shapes import TeardropCylinder
from ocp_vscode import show, Camera


class TeardropBoltCutSinkhole(BasePartObject):

    def __init__(
        self,
        shaft_radius: float = 1.65,
        shaft_depth: float = 2,
        head_radius: float = 3.1,
        head_depth: float = 5,
        chamfer_radius: float = 1,
        extension_distance: float = 100,
        teardrop_ratio: float = 1.1,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        template for the cutout for a hexagonal nutt
        -------
        arguments:
            - shaft_radius: float
                The radius of the bolt shaft
            - shaft_depth: float
                The depth of the shaft portion
            - head_radius: float
                The radius of the bolt head countersink
            - head_depth: float
                The depth of the head countersink
            - chamfer_radius: float
                The radius of the anti-chamfer at the top
            - extension_distance: float
                How far to extend the shaft beyond the head (for through-holes)
            - teardrop_ratio: float
                The ratio to stretch the teardrop shape (1.0 = circle, 1.1 = recommended teardrop)
            - rotation: the rotation of the sinkhole
            - align: the alignment of the sinkhole (default
                    is (Align.CENTER, Align.CENTER, Align.CENTER) )
            - mode: the mode to use when adding the sinkhole
        """
        context: BuildPart = BuildPart._get_context()
        validate_inputs(context, self)

        with BuildPart(Location((0, 0, shaft_depth))) as sinkhole:
            TeardropCylinder(
                radius=shaft_radius,
                height=shaft_depth,
                peak_distance=shaft_radius * teardrop_ratio,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            ),
            TeardropCylinder(
                radius=head_radius,
                height=head_depth,
                peak_distance=head_radius * teardrop_ratio,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ),
            if extension_distance > 0:
                extrude(
                    sinkhole.faces().sort_by(Axis.Z)[-1],
                    amount=extension_distance,
                )
            anti_chamfer(
                sinkhole.part.faces().sort_by(Axis.Z)[-1],
                chamfer_radius,
            )
        super().__init__(
            part=sinkhole.part,
            rotation=rotation,
            align=tuplify(align, 3),
            mode=mode,
        )


class BoltCutSinkhole(TeardropBoltCutSinkhole):

    def __init__(
        self,
        shaft_radius: float = 1.65,
        shaft_depth: float = 2,
        head_radius: float = 3.1,
        head_depth: float = 5,
        chamfer_radius: float = 1,
        extension_distance: float = 100,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """create a cylindrical bolt hole with countersink
        ----------
        Arguments:
            - shaft_radius: float
                The radius of the bolt shaft
            - shaft_depth: float
                The depth of the shaft portion
            - head_radius: float
                The radius of the bolt head countersink
            - head_depth: float
                The depth of the head countersink
            - chamfer_radius: float
                The radius of the anti-chamfer at the top
            - extension_distance: float
                How far to extend the shaft beyond the head (for through-holes)
            - rotation: the rotation of the sinkhole
            - align: the alignment of the sinkhole (default
                    is (Align.CENTER, Align.CENTER, Align.CENTER) )
            - mode: the mode to use when adding the sinkhole
        Returns:
            - Part: A cylindrical bolt hole part with countersink"""

        super().__init__(
            shaft_radius=shaft_radius,
            shaft_depth=shaft_depth,
            head_radius=head_radius,
            head_depth=head_depth,
            chamfer_radius=chamfer_radius,
            extension_distance=extension_distance,
            teardrop_ratio=1.0,
            rotation=rotation,
            align=tuplify(align, 3),
            mode=mode,
        )


class SquareNutSinkhole(BasePartObject):

    def __init__(
        self,
        bolt_radius: float = 1.65,
        bolt_depth: float = 2,
        nut_height: float = 2.1,
        nut_legnth: float = 5.6,
        nut_depth: float = 100,
        bolt_extension: float = 1,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """create a bolt hole with square nut trap
        ----------
        Arguments:
            - bolt_radius: float
                The radius of the bolt shaft
            - bolt_depth: float
                The depth of the bolt hole before the nut trap
            - nut_height: float
                The height (thickness) of the square nut
            - nut_legnth: float
                The side length of the square nut
            - nut_depth: float
                How far the nut trap extends
            - bolt_extension: float
                How far to extend the bolt hole beyond the nut trap
                - rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
                - align (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
                or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
                - mode (Mode, optional): combine mode. Defaults to Mode.ADD
        """
        with BuildPart() as sinkhole:
            TeardropCylinder(
                radius=bolt_radius,
                height=bolt_depth,
                peak_distance=bolt_radius * 1.1,
                rotation=(-90, 0, 0),
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            ),
            with BuildPart(Location((0, bolt_depth, 0))) as nut:
                Box(
                    nut_legnth,
                    nut_height,
                    nut_legnth,
                    align=(Align.CENTER, Align.MIN, Align.CENTER),
                )
                extrude(nut.part.faces().sort_by(Axis.Z)[-1], amount=nut_depth)
            if bolt_extension > 0:
                with BuildPart(Location((0, bolt_depth + nut_height, 0))) as nut:
                    TeardropCylinder(
                        radius=bolt_radius,
                        height=bolt_extension,
                        peak_distance=bolt_radius * 1.1,
                        rotation=(-90, 0, 0),
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    ),
        super().__init__(
            part=sinkhole.part,
            rotation=rotation,
            align=tuplify(align, 3),
            mode=mode,
        )


class NutCut(BasePartObject):

    def __init__(
        self,
        head_radius: float = 3,
        head_depth: float = 5,
        shaft_radius: float = 2.1,
        shaft_length: float = 20,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        template for the cutout for a hexagonal nutt
        -------
        arguments:
            - head_radius: the radius of the heatsink head
            - head_depth: the depth of the heatsink head
            - shaft_radius: the radius of the bolt shaft
            - shaft_length: the length of the bolt shaft
            - rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
            - align (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
            or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
            - mode (Mode, optional): combine mode. Defaults to Mode.ADD
        """
        context: BuildPart = BuildPart._get_context()
        validate_inputs(context, self)

        with BuildPart(Location((0, 0, head_depth))) as cut:
            with BuildSketch():
                RegularPolygon(radius=head_radius, side_count=6)
            extrude(amount=-head_depth)
            Cylinder(
                radius=shaft_radius,
                height=shaft_length,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        super().__init__(
            part=cut.part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


class ScrewCut(BasePartObject):

    def __init__(
        self,
        head_radius: float = 4.5,
        head_depth: float = 1.4,
        shaft_radius: float = 2.25,
        shaft_length: float = 20,
        bottom_clearance: float = 20,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        template for the cutout for a screwhead
            -------
            arguments:
                - head_radius: the radius of the heatsink head
                - head_depth: the depth of the heatsink head
                - shaft_radius: the radius of the bolt shaft
                - shaft_length: the length of the bolt shaft
                - rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
                - align (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
                or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
                - mode (Mode, optional): combine mode. Defaults to Mode.ADD
        """
        context: BuildPart = BuildPart._get_context()
        validate_inputs(context, self)

        if head_radius <= shaft_radius:
            raise ValueError("head_radius must be larger than shaft_radius")
        with BuildPart() as head:
            with BuildSketch(Plane.XY.offset(-bottom_clearance)):
                Circle(head_radius)
            with BuildSketch():
                Circle(head_radius)
            with BuildSketch(Plane.XY.offset(head_depth)):
                Circle(head_radius)
            with BuildSketch(Plane.XY.offset(head_depth + head_radius - shaft_radius)):
                Circle(shaft_radius)
            with BuildSketch(Plane.XY.offset(shaft_length)):
                Circle(shaft_radius)
            loft(ruled=True)
        super().__init__(
            part=head.part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


class HeatsinkCut(BasePartObject):

    def __init__(
        self,
        head_radius: float = 3,
        head_depth: float = 5,
        shaft_radius: float = 2.1,
        shaft_length: float = 20,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        template for the cutout for a heatsink and bolt
        -------
        arguments:
            - head_radius: the radius of the heatsink head
            - head_depth: the depth of the heatsink head
            - shaft_radius: the radius of the bolt shaft
            - shaft_length: the length of the bolt shaft
            - rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
            align (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
                or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
            - mode (Mode, optional): combine mode. Defaults to Mode.ADD
        """
        context: BuildPart = BuildPart._get_context()
        validate_inputs(context, self)

        with BuildPart(Location((0, 0, head_depth))) as cut:
            Cylinder(
                radius=head_radius,
                height=head_depth,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
            )
            Cylinder(
                radius=shaft_radius,
                height=shaft_length,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        super().__init__(
            part=cut.part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


if __name__ == "__main__":
    with BuildPart() as tst:
        Box(20, 20, 20)
        with GridLocations(10, 10, 2, 2):
            BoltCutSinkhole(mode=Mode.SUBTRACT)
    show(tst.part, reset_camera=Camera.KEEP)
