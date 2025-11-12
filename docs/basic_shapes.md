# Basic Shapes

Utility functions for creating and manipulating basic 3D shapes and geometric calculations. These functions extend build123d's capabilities with shapes and operations commonly used in 3D design.

## Geometric Calculation

### adjacent_length

```python
def adjacent_length(angle: float, opposite_length: float) -> float
```

Calculates the adjacent side length of a right triangle given the angle and opposite side length.

**Arguments:**
- `angle` (float): The angle in degrees
- `opposite_length` (float): The length of the opposite side

**Returns:**
- `float`: The length of the adjacent side


### apothem_to_radius

```python
def apothem_to_radius(apothem: float, side_count: int = 6) -> float
```

**Arguments**
- `apothem` (float): The apothem of the polygon
- `side_count` (float): The number of sides of the poygon.

**Returns:**
- `float`: The radius of the polygon

### circular_intersection

```python
circular_intersection(radius: float, coordinate: float) -> float
```

calculates the circumradius of a regular polygon given its apothem
    
Finds the intersection point along one axis given a coordinate on the other axis of a circle's perimeter.

**Arguments:**
- `radius` (float): The radius of the circle
- `coordinate` (float): A coordinate along one axis (must be positive and less than radius)

**Returns:**
- `float`: The intersection coordinate on the other axis

**Raises:**
- `ValueError`: If coordinate is greater than radius or negative

### distance_to_circle_edge

```python
distance_to_circle_edge(radius: float, point: tuple, angle: float) -> float
```

Calculates the distance from a given point to the edge of a circle in a specified direction.

**Arguments:**
- `radius` (float): The radius of the circle
- `point` (tuple): The starting point (x, y)
- `angle` (float): The direction angle in degrees

**Returns:**
- `float`: Distance to the circle edge

**Raises:**
- `ValueError`: If the discriminant is negative (no intersection)

### opposite_length

```python
def opposite_length(angle: float, adjacent_length: float) -> float
```

Calculates the opposite side length of a right triangle given the angle and adjacent side length.

**Arguments:**
- `angle` (float): The angle in degrees
- `adjacent_length` (float): The length of the adjacent side

**Returns:**
- `float`: The length of the opposite side

### radius_to_appothem

```python
def radius_to_appothem(radius: float, side_count: int = 6) -> float
```

**Arguments:**
- `radius` (float): the radius of the polygon
- `side_count` (float): the number of sides of the polygon

**Returns:**
- `float`: The apothem of the polygon

## Part Classes

### DiamondCylinder
Part Object: DiamondCylinder

Creates an extruded diamond (4-sided polygon) that behaves like a cylinder. This is a convenience wrapper for `PolygonalCylinder` with 4 sides.

```python
DiamondCylinder(
    radius: float,
    height: float,
    rotation: tuple = (0, 0, 0),
    align: tuple = (Align.CENTER, Align.CENTER, Align.CENTER),
    stretch: tuple = (1, 1, 1)
)
```

**Arguments:**
- `radius` (float): The radius of the circumscribed circle
- `height` (float): The height of the extrusion
- `rotation` (tuple, default=(0, 0, 0)): Rotation angles (X, Y, Z) in degrees
- `align` (tuple, default=(Align.CENTER, Align.CENTER, Align.CENTER)): Alignment
- `stretch` (tuple, default=(1, 1, 1)): Scaling factors (X, Y, Z)

**Returns:**
- `Part`: The diamond cylinder

### DiamondTorus

Part Object: DiamondTorus

Creates a torus by sweeping a diamond (square rotated 45°) along a circular path.

```python
DiamondTorus(
    major_radius: float, 
    minor_radius: float, 
    stretch: tuple = (1, 1)
)
```

Creates a torus by sweeping a diamond (square rotated 45°) along a circular path.

**Arguments:**
- `major_radius` (float): The radius of the circular sweep path
- `minor_radius` (float): The radius of the diamond cross-section
- `stretch` (tuple, default=(1, 1)): Scaling factors for the diamond shape
- `rotation` (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
- `align` (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
        or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
- `mode` (Mode, optional): combine mode. Defaults to Mode.ADD



### PolygonalCylinder

Part Object: PolygonalCylinder

Creates an extruded regular polygon that behaves like a cylinder.


```python
PolygonalCylinder(
    radius: float,
    height: float,
    sides: int = 6,
    rotation: tuple = (0, 0, 0),
    align: tuple = (Align.CENTER, Align.CENTER, Align.CENTER),
    stretch: tuple = (1, 1, 1)
)
```


**Arguments:**
- `radius` (float): The radius of the circumscribed circle
- `height` (float): The height of the extrusion
- `sides` (int, default=6): Number of sides of the polygon
- `stretch` (tuple, default=(1, 1, 1)): Scaling factors (X, Y, Z)
- `rotation` (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
- `align` (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
        or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
- `mode` (Mode, optional): combine mode. Defaults to Mode.ADD


### RoundedCylinder

Part Object: RoundedCylinder

Creates a cylinder with rounded (filleted) top and bottom edges.

```python
RoundedCylinder(
    radius: float, 
    height: float, 
    align: tuple = (Align.CENTER, Align.CENTER, Align.CENTER)
)
```

**Arguments:**
- `radius` (float): The radius of the cylinder
- `height` (float): The height of the cylinder (must be > radius * 2)
- `rotation` (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
- `align` (Align | tuple[Align, Align, Align] | None, optional): align MIN, CENTER,
        or MAX of object. Defaults to (Align.CENTER, Align.CENTER, Align.CENTER)
- `mode` (Mode, optional): combine mode. Defaults to Mode.ADD

**Raises:**
- `ValueError`: If height is not greater than radius * 2


### TeardropCylinder

Part Object: TeardropCylinder

Creates a 3D teardrop-shaped cylinder by extruding a teardrop sketch. Particularly useful for creating holes that print well on FDM printers without supports.

```python
TeardropCylinder(
    radius: float,
    peak_distance: float,
    height: float,
    rotation: RotationLike = (0, 0, 0),
    align: Align | tuple[Align, Align, Align] = (Align.CENTER, Align.CENTER, Align.CENTER),
    mode: Mode = Mode.ADD
)
```

**Arguments:**
- `radius` (float): The radius of the circular portion
- `peak_distance` (float): Distance from circle center to the teardrop peak
- `height` (float): Height of the extrusion
- `rotation` (tuple, default=(0, 0, 0)): Rotation angles (X, Y, Z)
- `align` (tuple, default=(Align.CENTER, Align.CENTER, Align.CENTER)): Alignment
- `mode` (Mode, default=Mode.ADD): Build mode


### Teardrop

Sketch Object: Teardrop

Creates a 2D teardrop-shaped sketch. The shape is useful for 3D printing holes that minimize overhangs.

```python
Teardrop(
    radius: float,
    peak_distance: float,
    align: Align | tuple[Align, Align] = (Align.CENTER, Align.CENTER)
)
```

**Arguments:**
- `radius` (float): The radius of the circular portion
- `peak_distance` (float): Distance from circle center to the teardrop peak
- `rotation` (RotationLike, optional): angles to rotate about axes. Defaults to (0, 0, 0)
- `align` (Align | tuple[Align, Align] | None, optional): align MIN, CENTER,
        or MAX of object. Defaults to (Align.CENTER, Align.CENTER)
- `mode` (Mode, optional): combine mode. Defaults to Mode.ADD

## Examples

```python
from b3dkit.basic_shapes import (
    RoundedCylinder, 
    DiamondTorus, 
    TeardropCylinder,
    ScrewCut,
    half_part,
    opposite_length,
    adjacent_length
)
from build123d import BuildPart, Mode

# Create a rounded cylinder
rounded_cyl = RoundedCylinder(radius=10, height=30)

# Create a diamond torus
torus = DiamondTorus(major_radius=20, minor_radius=3)

# Create a teardrop hole for 3D printing
with BuildPart() as part:
    RoundedCylinder(radius=15, height=10)
    TeardropCylinder(
        radius=5, 
        peak_distance=6, 
        height=15, 
        mode=Mode.SUBTRACT
    )

# Create a screw cutout
screw_hole = ScrewCut(
    head_radius=5,
    head_sink=2,
    shaft_radius=2.5,
    shaft_length=25
)

# Calculate triangle dimensions
opp = opposite_length(30, 10)  # Given 30° angle and adjacent side of 10
adj = adjacent_length(45, 5)   # Given 45° angle and opposite side of 5

# Create a cross-section view
cross_section = half_part(part.part)
```