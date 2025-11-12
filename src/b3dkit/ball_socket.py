from math import sqrt
from typing import Union

from build123d import (
    BasePartObject,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    Location,
    Mode,
    Part,
    Plane,
    PolarLocations,
    RotationLike,
    Sphere,
    Align,
    loft,
    fillet,
    Axis,
    tuplify,
)
from ocp_vscode import show, Camera


class BallMount(BasePartObject):

    def __init__(
        self,
        ball_radius: float,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ) -> Part:
        """
        Creates a ball mount component for a ball-and-socket joint system.

        The ball mount consists of a spherical ball attached to a tapered shaft. The shaft
        is designed to be inserted into another part or component, while the ball mates
        with a corresponding ball socket to create a flexible joint that allows rotation
        in multiple axes. The shaft has a sophisticated tapered design that transitions from
        the full ball radius at the base to approximately 36% of the ball radius at the
        insertion point, providing strength while allowing for easy integration into
        mounting systems.

        args:
            - ball_radius: the radius of the spherical ball in millimeters. This determines
            the overall size of the joint system and must match the ball_radius used
            for the corresponding ball_socket.
            - rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
            - align (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
                or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
            - mode (Mode, optional): combine mode. Defaults to Mode.ADD
        """
        with BuildPart() as ballmount:
            with BuildPart(Location((0, 0, ball_radius * 2.5))):
                Sphere(
                    radius=ball_radius, align=(Align.CENTER, Align.CENTER, Align.CENTER)
                )
            with BuildPart() as shaft:
                with BuildSketch():
                    Circle(
                        radius=ball_radius,
                        align=(Align.CENTER, Align.CENTER),
                    )
                with BuildSketch(Plane.XY.offset(ball_radius * 0.5)):
                    Circle(
                        radius=ball_radius / 2.75,
                        align=(Align.CENTER, Align.CENTER),
                    )
                height_ratio = 0.25
                with BuildSketch(Plane.XY.offset(ball_radius * (2 + height_ratio))):
                    Circle(
                        radius=ball_radius * (sqrt(1 - height_ratio**2)),
                        align=(Align.CENTER, Align.CENTER),
                    )
                loft()

        ballmount.part.label = "Ball Mount"
        super().__init__(
            part=ballmount.part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


class BallSocket(BasePartObject):

    def __init__(
        self,
        ball_radius: float,
        wall_thickness: float = 2,
        tolerance: float = 0.1,
        rotation: RotationLike = (0, 0, 0),
        align: Union[None, Align, tuple[Align, Align, Align]] = None,
        mode: Mode = Mode.ADD,
    ):
        """
        Creates a ball socket component for a ball-and-socket joint system.

        The ball socket is designed to receive and hold a ball mount, creating a flexible
        joint that allows rotation in multiple axes. The socket features a hemispherical
        cavity to house the ball, a cylindrical outer shell for strength, and flexible
        cuts that allow the socket to grip the ball while still permitting smooth rotation.
        The socket includes a flange at the top with a smooth filleted edge for comfortable
        operation and four radial flex cuts that allow the socket walls to compress slightly
        for ball retention while maintaining smooth rotation.

        args:
            - ball_radius: the radius of the spherical ball that will be inserted into
            this socket, in millimeters. Must match the ball_radius of the corresponding
            ball_mount for proper fit.
            - wall_thickness: the thickness of the socket walls in millimeters. Affects
            both strength and flexibility. Thicker walls provide more strength but may
            reduce flexibility.
            - tolerance: additional clearance around the ball in millimeters. Positive
            values create looser fits, negative values create tighter fits.
            - rotation (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
            - align (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
                or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
            - mode (Mode, optional): combine mode. Defaults to Mode.ADD

        """
        with BuildPart() as socket:
            Cylinder(
                radius=ball_radius + wall_thickness,
                height=ball_radius + wall_thickness * 2.5,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            with BuildPart(
                Plane.XY.offset(wall_thickness), mode=Mode.SUBTRACT
            ) as bowl_cut:
                Sphere(
                    radius=ball_radius + tolerance,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            # Fillet the top edge if inner wires exist (after sphere subtraction they may not)
            top_face = socket.faces().sort_by(Axis.Z)[-1]
            if top_face.inner_wires():
                fillet(
                    top_face.inner_wires().edge(),
                    min(wall_thickness * 0.4, ball_radius * 0.1),  # Limit fillet radius
                )
            with BuildPart(
                Plane.XY.offset(ball_radius * 0.75 + wall_thickness), mode=Mode.SUBTRACT
            ) as flexcuts:
                with PolarLocations(0, 4):
                    Box(
                        ball_radius,
                        (ball_radius + wall_thickness) * 2,
                        ball_radius / 2 + wall_thickness,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                    )
                    Cylinder(
                        radius=ball_radius / 2,
                        height=(ball_radius + wall_thickness) * 2,
                        align=(Align.CENTER, Align.CENTER, Align.CENTER),
                        rotation=(90, 0, 0),
                    )
        socket.part.label = "Ball Socket"
        super().__init__(
            part=socket.part, rotation=rotation, align=tuplify(align, 3), mode=mode
        )


if __name__ == "__main__":
    show(
        BallMount(
            24.24871131,
        ),
        BallSocket(
            24.24871131,
            # 15,
            wall_thickness=2,
            tolerance=-0.05,
        ),
        reset_camera=Camera.KEEP,
    )
