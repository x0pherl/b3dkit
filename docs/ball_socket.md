# Ball Socket

# Ball Socket Joint System Documentation

## Overview

The ball socket joint components are designed to create flexible connections between 3D printed parts that require multi-axis rotation. This system consists of two complementary components: a ball mount and a ball socket. The ball mount is a ball attached to a shaft, while the ball socket provides a cavity with flexible walls that grip the ball while allowing smooth rotation.

This joint system is particularly useful for creating articulated mechanisms, adjustable brackets, camera mounts, robotic joints, or any application where you need a connection that can rotate freely in multiple directions while maintaining a somewhat secure hold.

The `BallMount` and `BallSocket` classes create matched components with built-in tolerances for 3D printing.

## Classes

### BallMount

Part Object: BallMount

Creates a mounting point for a BallSocket, defined by the radius of the ball.

## Arguments

- `ball_radius` (float): The radius of the spherical ball in millimeters. This determines the overall size of the joint system and must match the ball_radius used for the corresponding ball_socket.
- `rotation` (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
- `align` (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
        or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
- `mode` (Mode, optional): combine mode. Defaults to Mode.ADD


### BallSocket

Part Object: BallMount

Creates a ball socket component for a ball-and-socket joint system, defined by the ball radius, wall_thickness, and tolerance.

## Arguments

- `ball_radius` (float): The radius of the spherical ball that will be inserted into this socket, in millimeters. Must match the ball_radius of the corresponding ball_mount for proper fit.
- `wall_thickness` (float, default=2): The thickness of the socket walls in millimeters. Affects both strength and flexibility. Thicker walls provide more strength but may reduce flexibility. Recommended range: 1.5-3mm.
- `tolerance` (float, default=0.1): Additional clearance around the ball in millimeters. Positive values create looser fits, negative values create tighter fits. Typical range: 0.05-0.2mm.
- `rotation` (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
- `align` (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
        or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
- `mode` (Mode, optional): combine mode. Defaults to Mode.ADD


## Example Usage

```python
from b3dkit.ball_socket import BallMount, BallSocket

# Create a basic ball joint system with 15mm radius
mount = BallMount(15.0)
socket = BallSocket(15.0)

# Create a tighter-fitting joint with thicker walls
precision_mount = BallMount(12.0)
precision_socket = BallSocket(
    ball_radius=12.0,
    wall_thickness=2.5,
    tolerance=0.05
)

# Create a looser joint for easy assembly
loose_mount = BallMount(10.0)
loose_socket = BallSocket(
    ball_radius=10.0,
    wall_thickness=2.0,
    tolerance=0.15
)

# For heavy-duty applications
heavy_duty_mount = BallMount(20.0)
heavy_duty_socket = BallSocket(
    ball_radius=20.0,
    wall_thickness=4.0,
    tolerance=0.1
)
```