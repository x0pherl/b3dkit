# Basic Shapes

Utility functions for creating and manipulating basic 3D shapes and geometric calculations. These functions extend build123d's capabilities with shapes and operations commonly used in 3D design.

## Geometric Calculation

### adjacent_length

Calculates the adjacent side length of a right triangle given the angle and opposite side length.

### apothem_to_radius

**Arguments**
- `apothem` (float): The apothem of the polygon
- `side_count` (int): The number of sides of the poygon.

### circular_intersection

calculates the circumradius of a regular polygon given its apothem
    
Finds the intersection point along one axis given a coordinate on the other axis of a circle's perimeter.

**Raises:**
- `ValueError`: If coordinate is greater than radius or negative

### distance_to_circle_edge

Calculates the distance from a given point to the edge of a circle in a specified direction.

**Raises:**
- `ValueError`: If the ray does not meet the circle at all

### opposite_length

Calculates the opposite side length of a right triangle given the angle and adjacent side length.

### radius_to_apothem

## Part Classes

### DiamondCylinder
Part Object: DiamondCylinder

Creates an extruded diamond (4-sided polygon) that behaves like a cylinder. This is a convenience wrapper for `PolygonalCylinder` with 4 sides.

**Arc Size Behavior:**
- `arc_size=360` produces the full diamond profile
- `arc_size<360` clips the XY profile and reduces volume while preserving Z behavior from `height` and `stretch[2]`

### DiamondTorus

Part Object: DiamondTorus

Creates a torus by sweeping a diamond (square rotated 45°) along a circular path.

Creates a torus by sweeping a diamond (square rotated 45°) along a circular path.

        or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
- `mode` (Mode, optional): combine mode. Defaults to Mode.ADD

### PolygonalCylinder

Part Object: PolygonalCylinder

Creates an extruded regular polygon that behaves like a cylinder.

**Arc Size Behavior:**
- `arc_size=360` keeps the full regular polygonal profile
- `arc_size<360` clips the XY profile and reduces volume while preserving Z behavior from `height` and `stretch[2]`

### RoundedCylinder

Part Object: RoundedCylinder

Creates a cylinder with rounded (filleted) top and bottom edges.

        or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
- `mode` (Mode, optional): combine mode. Defaults to Mode.ADD

**Raises:**
- `ValueError`: If height is not greater than radius * 2

### TeardropCylinder

Part Object: TeardropCylinder

Creates a 3D teardrop-shaped cylinder by extruding a teardrop sketch. Particularly useful for creating holes that print well on FDM printers without supports.

### Teardrop

Sketch Object: Teardrop

Creates a 2D teardrop-shaped sketch. The shape is useful for 3D printing holes that minimize overhangs.

        or MAX of object. Defaults to (Align.CENTER, Align.CENTER)
- `mode` (Mode, optional): combine mode. Defaults to Mode.ADD

## Examples

```python
from build123d import BuildPart, Mode
from b3dkit import (
    DiamondTorus,
    RoundedCylinder,
    TeardropCylinder,
    adjacent_length,
    opposite_length,
)

# A cylinder with rounded ends
rounded_cyl = RoundedCylinder(radius=10, height=30)

# A torus swept from a diamond profile
torus = DiamondTorus(major_radius=20, minor_radius=3)

# A teardrop hole, which prints without support when the axis is horizontal
with BuildPart() as part:
    RoundedCylinder(radius=5, height=30)   # height must exceed radius * 2
    TeardropCylinder(
        radius=5,
        peak_distance=6,
        height=15,
        mode=Mode.SUBTRACT,
    )

# Right-triangle helpers, useful when laying out tapers
opp = opposite_length(30, 10)   # 30 degree angle, adjacent side of 10
adj = adjacent_length(45, 5)    # 45 degree angle, opposite side of 5
```