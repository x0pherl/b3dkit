# Bolt Fittings Module Documentation

## Overview

The `bolt_fittings` module provides functions for creating various types of bolt holes, countersinks, and nut traps for connecting 3D printed parts. These utilities help create properly sized cavities for hardware fasteners with considerations for 3D printing orientation and tolerances.

## Classes

### TeardropBoltCutSinkhole

Part Object: TeardropBoltCutSinkhole
Creates a bolt hole with countersink using teardrop-shaped profiles for better vertical printing without support material.

#### arguments

 - shaft_radius: the radius of the bolt shaft (default: 1.65mm for M3)
 - shaft_depth: the depth of the shaft portion (default: 2mm)
 - head_radius: the radius of the bolt head countersink (default: 3.1mm)
 - head_depth: the depth of the head countersink (default: 5mm)
 - chamfer_radius: the radius of the anti-chamfer at the top (default: 1mm)
 - extension_distance: how far to extend the shaft beyond the head for through-holes (default: 100mm)
 - teardrop_ratio: the ratio to stretch the teardrop shape (default: 1.1, where 1.0 = circle, >1.0 = teardrop)

The teardrop shape uses the teardrop_ratio to determine the vertical extension (default 10% with ratio of 1.1) to accommodate printing without supports. The function creates a two-part geometry: a shaft section and a head countersink, with an optional extension for through-holes.

### BoltCutSinkhole

Part Object: BoltCutSinkhole
Creates a standard cylindrical bolt hole with countersink, suitable for all printing orientations.

#### arguments

 - shaft_radius: the radius of the bolt shaft (default: 1.65mm for M3)
 - shaft_depth: the depth of the shaft portion (default: 2mm)
 - head_radius: the radius of the bolt head countersink (default: 3.1mm)
 - head_depth: the depth of the head countersink (default: 5mm)
 - chamfer_radius: the radius of the anti-chamfer at the top (default: 1mm)
 - extension_distance: how far to extend the shaft beyond the head for through-holes (default: 100mm)

This function is a convenience wrapper around `TeardropBoltCutSinkhole` with `teardrop_ratio=1.0`, which produces perfectly cylindrical profiles. Best for horizontal printing or when support material is acceptable.

### BoltCutSinkhole

Creates a bolt hole with a square nut trap cavity, allowing nuts to be inserted from the side during assembly.

#### arguments

 - bolt_radius: the radius of the bolt shaft (default: 1.65mm for M3)
 - bolt_depth: the depth of the bolt hole before the nut trap (default: 2mm)
 - nut_height: the height (thickness) of the square nut (default: 2.1mm for M3)
 - nut_legnth: the side length of the square nut (default: 5.6mm for M3)
 - nut_depth: how far the nut trap extends (default: 100mm)
 - bolt_extension: how far to extend the bolt hole beyond the nut trap (default: 1mm)

The nut trap is oriented perpendicular to the bolt axis, allowing for side insertion of nuts. Uses teardrop profiles for the bolt holes to support vertical printing.

## Usage Notes

- Default values are sized for M3 bolts with appropriate printing tolerances
- Teardrop versions use `teardrop_ratio` to control the vertical extension (default 1.1 = 10% extension)
- Setting `teardrop_ratio=1.0` produces perfectly cylindrical holes (same as `BoltCutSinkhole`)
- The anti-chamfer at the top provides a smooth entry and prevents material buildup
- Extension distance can be set to 0 for blind holes or large values for through-holes
- All dimensions should account for your printer's tolerances (typically 0.1-0.2mm)

## Example
```python
from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Location,
)
from b3dkit.bolt_fittings import (
    TeardropBoltCutSinkhole,
    BoltCutSinkhole,
    BoltCutSinkhole,
)

# Create a part with a vertical teardrop bolt hole
with BuildPart() as part1:
    Box(20, 20, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Subtract a teardrop bolt hole for vertical printing
    TeardropBoltCutSinkhole(
        shaft_radius=1.65,
        shaft_depth=3,
        head_radius=3.1,
        head_depth=5,
        chamfer_radius=1,
        extension_distance=0,  # Blind hole
        teardrop_ratio=1.1,  # Default 10% teardrop extension
        mode=Mode.SUBTRACT
    )

# Create a part with standard bolt hole
with BuildPart() as part2:
    Box(20, 20, 10)
    # Standard cylindrical bolt hole
    BoltCutSinkhole(
        shaft_radius=1.65,
        shaft_depth=8,
        head_radius=3.1,
        head_depth=2,
        chamfer_radius=0.5,
        extension_distance=100,  # Through hole
        mode=Mode.SUBTRACT
    )

# Create a part with nut trap
with BuildPart() as part3:
    Box(30, 15, 10)
    # Position and subtract nut trap
    with Locations([(0, 0, 0)]):
        BoltCutSinkhole(
            bolt_radius=1.65,
            bolt_depth=3,
            nut_height=2.1,
            nut_legnth=5.6,
            nut_depth=20,
            bolt_extension=2,
            mode=Mode.SUBTRACT
        )
```
### heatsink_insert_cut

```python
heatsink_insert_cut(
    head_radius: float = 3,
    head_depth: float = 5,
    shaft_radius: float = 2.1,
    shaft_length: float = 20
) -> Part
```

Creates a cutout template for a heatsink and bolt assembly.

**Arguments:**
- `head_radius` (float, default=3): Radius of the heatsink head
- `head_depth` (float, default=5): Depth of the heatsink head cutout
- `shaft_radius` (float, default=2.1): Radius of the bolt shaft
- `shaft_length` (float, default=20): Length of the bolt shaft

**Returns:**
- `Part`: The heatsink cutout geometry

### nut_cut

```python
nut_cut(
    head_radius: float = 3,
    head_depth: float = 5,
    shaft_radius: float = 2.1,
    shaft_length: float = 20
) -> Part
```

Creates a cutout template for a hexagonal nut and bolt assembly.

**Arguments:**
- `head_radius` (float, default=3): Radius of the hexagonal nut
- `head_depth` (float, default=5): Depth of the nut cutout
- `shaft_radius` (float, default=2.1): Radius of the bolt shaft
- `shaft_length` (float, default=20): Length of the bolt shaft

**Returns:**
- `Part`: The nut cutout geometry

### screw_cut

```python
screw_cut(
    head_radius: float = 4.5,
    head_sink: float = 1.4,
    shaft_radius: float = 2.25,
    shaft_length: float = 20,
    bottom_clearance: float = 20
) -> Part
```

Creates a cutout template for a countersunk screw with tapered head transition.

**Arguments:**
- `head_radius` (float, default=4.5): Radius of the screw head (must be > shaft_radius)
- `head_sink` (float, default=1.4): Depth of the countersunk head
- `shaft_radius` (float, default=2.25): Radius of the screw shaft
- `shaft_length` (float, default=20): Length of the screw shaft
- `bottom_clearance` (float, default=20): Additional clearance below the head

**Returns:**
- `Part`: The screw cutout geometry

**Raises:**
- `ValueError`: If head_radius is not larger than shaft_radius

## Design Considerations

### Teardrop vs Cylindrical
- **Teardrop**: Use for vertical bolt holes when printing orientation is constrained. The teardrop shape prevents sagging without support material. Control the amount of overhang with `teardrop_ratio` (1.05-1.15 recommended).
- **Cylindrical**: Use when printing horizontally or when support material is not a concern. Provides slightly better dimensional accuracy. Equivalent to calling `teardrop_bolt_cut_sinkhole` with `teardrop_ratio=1.0`.

### Countersink Sizing
- The head_radius should be slightly larger than the actual bolt head to account for printing tolerances
- The head_depth should accommodate the full bolt head height plus a small margin

### Nut Trap Design
- Square nut traps work best when the opening is perpendicular to the bolt axis
- Add 0.2-0.3mm to nut dimensions for easy insertion while maintaining grip
- The nut_depth should extend far enough to prevent the nut from pulling through

### Tolerances
- Default values include standard 3D printing tolerances
- For tight fits, reduce radii by 0.1-0.2mm
- For loose fits or poor printer calibration, increase radii by 0.2-0.3mm
