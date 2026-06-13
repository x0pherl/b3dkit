# Hexagonal Patterns

This module provides two part objects for creating hexagonal (honeycomb) patterns:

- [`HexWall`](#hexwall) — a flat box with a hexagonal cutout pattern.
- [`HexCylindrical`](#hexcylindrical) — a honeycomb of hexagonal holes wrapped around the curved surface of a cone or cylinder.

## HexWall

Part Object: `HexWall`

Create a box with a hexagonal cutout pattern defined by length, width, and height, apothem, and wall thickness. This Part is useful for generating hexagonal patterns in 3D models.

### Arguments

- `length` (float): The length of the hexagonal wall.
- `width` (float): The width of the hexagonal wall.
- `height` (float): The height of the hexagonal wall.
- `apothem` (float): The apothem (distance from the center to the midpoint of a side) of the hexagons.
- `wall_thickness` (float): The thickness of the walls of the hexagons.
- `align` (Union[Align, tuple[Align, Align, Align]], default=(Align.CENTER, Align.CENTER, Align.CENTER)): The alignment of the hexagonal wall. Can be a single `Align` value or a tuple of three `Align` values for x, y, and z alignment.
- `inverse` (bool, default=False): If `True`, creates an inverse hexagonal pattern.

### Returns

- `Part`: The created hexagonal wall part.

### Example

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

## HexCylindrical

Part Object: `HexCylindrical`

Wraps a honeycomb of hexagonal holes around the curved surface of a `Cone` or `Cylinder`. It builds the hole geometry *only* — a `Part` containing one cutter per hole — so you subtract it from your solid to vent or lighten it.

The holes are laid out row by row: `horizontal_count` holes run around the surface at each height, `vertical_count` rows stack up the slope starting `z_distance` above the base, and alternate rows are offset half a step for the honeycomb stagger. Each hex is projected onto the true surface so it follows the curvature, then thickened into a cutter.

Each row is centered on a fixed meridian, so the pattern stays left/right symmetric as a cone tapers instead of drifting to one side. Rows that would climb past the top edge of the surface are dropped automatically.

### Arguments

- `cylindrical` (Cone | Cylinder): The cone or cylinder to wrap holes around. Assumed upright on the Z axis with its base at the bottom; its circular edges define the radius at each height. A pointed cone (top radius 0) is supported — its apex radius is inferred from the bounding box.
- `hole_radius` (float): Radius of each hexagonal hole (the `RegularPolygon` radius).
- `spacing_radius` (float): Hex cell radius controlling spacing; nearest holes are `2 * spacing_radius` apart (matching `HexLocations(radius=...)`).
- `horizontal_count` (int): Number of holes around the surface in each row.
- `vertical_count` (int): Number of rows stacked up the slope. Rows that fall off the top edge are skipped, so the actual number of rows may be fewer.
- `thickness` (float): How far each cutter extends in/out of the surface. Set `thickness >= wall_thickness` to cut clean through a hollow wall.
- `z_distance` (float): Height of the lowest row of holes, measured up from the bottom of the surface (not an absolute Z coordinate).
- `rotation` (RotationLike, default=(0, 0, 0)): Angles to rotate about the axes.
- `align` (Union[None, Align, tuple[Align, Align, Align]], default=None): Align MIN, CENTER, or MAX of the object.
- `mode` (Mode, default=Mode.ADD): Combine mode used when the object is created inside an active build context.

### Returns

- `Part`: A part whose children are the hole cutters. Subtract it from your solid (e.g. `solid - HexCylindrical(...)`, or pass `mode=Mode.SUBTRACT` inside a build context) to make the holes.

### Raises

- `ValueError`: If `cylindrical` has no circular edge to derive a radius profile from (e.g. a `Box`).
- `ValueError`: If no holes fit on the surface (e.g. `z_distance` starts at or above the top edge, or the surface is too short for the given spacing).

### Example

```python
from b3dkit import HexCylindrical
from build123d import Cone, Cylinder, Align

# Vent a tapering cone with a honeycomb pattern
cone = Cone(
    bottom_radius=40,
    top_radius=20,
    height=60,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
holes = HexCylindrical(
    cone,
    hole_radius=2,
    spacing_radius=4,
    horizontal_count=16,
    vertical_count=6,
    thickness=4,        # >= wall thickness so the holes cut all the way through
    z_distance=8,       # start the first row 8mm up from the base
)
vented_cone = cone - holes

# The same call works on a straight cylinder (constant radius)
cylinder = Cylinder(
    radius=30,
    height=60,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
vented_cylinder = cylinder - HexCylindrical(
    cylinder,
    hole_radius=2,
    spacing_radius=4,
    horizontal_count=20,
    vertical_count=8,
    thickness=4,
    z_distance=6,
)
```
