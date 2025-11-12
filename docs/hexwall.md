# HexWall Function Documentation

## Overview

Part Object: `HexWall`

Create a box with a hexagonal cutout pattern defined by length, width, and height, apothem, and wall thickness. This Part is useful for generating hexagonal patterns in 3D models.

## Arguments

- `length` (float): The length of the hexagonal wall.
- `width` (float): The width of the hexagonal wall.
- `height` (float): The height of the hexagonal wall.
- `apothem` (float): The apothem (distance from the center to the midpoint of a side) of the hexagons.
- `wall_thickness` (float): The thickness of the walls of the hexagons.
- `align` (Union[Align, tuple[Align, Align, Align]], default=(Align.CENTER, Align.CENTER, Align.CENTER)): The alignment of the hexagonal wall. Can be a single `Align` value or a tuple of three `Align` values for x, y, and z alignment.
- `inverse` (bool, default=False): If `True`, creates an inverse hexagonal pattern.

## Returns

- `Part`: The created hexagonal wall part.

## Example

```python
from b3dkit import HexWall
from build123d import Align

# Create a hexagonal wall with specified dimensions and properties
hex_wall = HexWall(
    length=100,
    width=100,
    height=10,
    apothem=5,
    wall_thickness=1,
    align=(Align.CENTER, Align.CENTER, Align.CENTER),
    inverse=False
)

# Create an inverse hexagonal wall
inverse_hex_wall = HexWall(
    length=100,
    width=100,
    height=10,
    apothem=5,
    wall_thickness=1,
    align=(Align.CENTER, Align.CENTER, Align.CENTER),
    inverse=True
)
```