# Bolt Fittings

## Overview

The `bolt_fittings` module provides Part objects for creating bolt holes,
countersinks, and nut traps for connecting 3D printed parts. These produce
properly sized cavities for hardware fasteners, with allowances for printing
orientation and tolerance.

All linear dimensions are in millimeters. Every object here is a cutter: build
it with `mode=Mode.SUBTRACT` inside the part you want to make the hole in.

## Objects

Full signatures and arguments are in the
[API reference](reference/bolt_fittings.md), generated from the source.

| Object | Use |
|---|---|
| `TeardropBoltCutSinkhole` | Bolt hole with a countersink, teardrop-shaped so a vertical hole prints without support |
| `BoltCutSinkhole` | The same, cylindrical rather than teardrop |
| `SquareNutSinkhole` | Bolt hole with a square nut trap entering from the side |
| `NutCut` | A hexagonal nut recess on its own |
| `ScrewCut` | A screw shaft with a countersunk head |
| `HeatsinkCut` | A recess for a heat-set threaded insert |

## Usage Notes

- Default values are sized for M3 bolts with appropriate printing tolerances
- Teardrop versions use `teardrop_ratio` to control the vertical extension (default 1.1 = 10% extension)
- Setting `teardrop_ratio=1.0` produces perfectly cylindrical holes (same as `BoltCutSinkhole`)
- The anti-chamfer at the top provides a smooth entry and prevents material buildup
- `extension_distance` can be 0 for blind holes or a large value for through-holes
- All dimensions should account for your printer's tolerances (typically 0.1-0.2mm)

## Example

```python
from build123d import Align, Box, BuildPart, Locations, Mode
from b3dkit import BoltCutSinkhole, SquareNutSinkhole, TeardropBoltCutSinkhole

# A vertical bolt hole that prints without support
with BuildPart() as teardrop_part:
    Box(20, 20, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    TeardropBoltCutSinkhole(
        shaft_radius=1.65,
        shaft_depth=3,
        head_radius=3.1,
        head_depth=5,
        chamfer_radius=1,
        extension_distance=0,      # blind hole
        teardrop_ratio=1.1,        # 10% vertical extension
        mode=Mode.SUBTRACT,
    )

# The cylindrical equivalent, as a through hole
with BuildPart() as cylindrical_part:
    Box(20, 20, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    BoltCutSinkhole(
        shaft_radius=1.65,
        shaft_depth=8,
        head_radius=3.1,
        head_depth=2,
        chamfer_radius=0.5,
        extension_distance=100,    # through hole
        mode=Mode.SUBTRACT,
    )

# A bolt hole with a square nut trap
with BuildPart() as nut_trap_part:
    Box(30, 15, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((0, 0, 0)):
        SquareNutSinkhole(
            bolt_radius=1.65,
            bolt_depth=3,
            nut_height=2.1,
            nut_length=5.6,
            nut_depth=20,
            bolt_extension=2,
            mode=Mode.SUBTRACT,
        )
```

## Design Considerations

### Teardrop vs Cylindrical
- **Teardrop**: Use for vertical bolt holes when printing orientation is constrained. The teardrop shape prevents sagging without support material. Control the amount of overhang with `teardrop_ratio` (1.05-1.15 recommended).
- **Cylindrical**: Use when printing horizontally or when support material is not a concern. Provides slightly better dimensional accuracy. Equivalent to `TeardropBoltCutSinkhole` with `teardrop_ratio=1.0`.

### Countersink Sizing
- `head_radius` should be slightly larger than the actual bolt head to account for printing tolerances
- `head_depth` should accommodate the full bolt head height plus a small margin

### Nut Trap Design
- Square nut traps work best when the opening is perpendicular to the bolt axis
- Add 0.2-0.3mm to nut dimensions for easy insertion while maintaining grip
- `nut_depth` should extend far enough to prevent the nut from pulling through

### Tolerances
- Default values include standard 3D printing tolerances
- For tight fits, reduce radii by 0.1-0.2mm
- For loose fits or poor printer calibration, increase radii by 0.2-0.3mm
