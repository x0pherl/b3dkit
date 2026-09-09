# High Top Slide Box

Creates slide boxes with tall tops and precise sliding rail mechanisms. This module provides functions for creating boxes where the lid slides on and off with rails, making them ideal for tool storage, organizers, and other applications requiring secure but easily accessible storage.

## Overview

The high top slide box system creates a box with a base and a sliding lid that moves along rails. The "high top" design means the lid has significant height, making it suitable for storing taller items or creating compartmentalized storage. The sliding mechanism uses diamond-shaped rails for smooth operation and includes optional divots for secure positioning.

## Functions

### high_top_slide_box

Creates a complete slide box with both the base and lid components. Returns a compound containing both parts positioned for display or printing.

### high_top_slide_box_lid

Creates only the sliding lid component of the box. This is useful when you need to print or modify just the lid.

### high_top_slide_box_base

Creates only the base component of the box. This includes the hollowed-out interior and the rail channels that guide the lid.

## Dimension requirements

All three functions validate their inputs and raise `ValueError` if the part cannot be
built as a single solid:

- `top_height`, `rail_height` and `wall_thickness` must all be greater than 0.
- `wall_thickness * 2` must be less than the smaller of the part's width and depth.
- At least `wall_thickness` of the part's height must remain below the rails, i.e.
  `part_height - top_height - rail_height >= wall_thickness`. With less than that, the
  divots have too little material to fuse into and break away as separate solids.

## Design Considerations

### Rail System
The sliding mechanism uses diamond-shaped rails that provide smooth operation while maintaining strength. The rails can be angled slightly (`rail_angle`) to improve sliding characteristics and reduce friction.

### Tolerances
The `tolerance` parameter controls the fit between the lid and base. Typical values:
- **0.1-0.15mm**: Tight fit, minimal play
- **0.2mm**: Standard fit (default)
- **0.3-0.4mm**: Loose fit for materials that swell or rough printing

### Wall Thickness
Choose wall thickness based on your intended use:
- **1-2mm**: Light duty, small boxes
- **2-3mm**: General purpose (recommended)
- **3-4mm**: Heavy duty, large boxes

### Divots
Divots provide tactile feedback and help position the lid. They can be disabled by setting `divot_radius=0`.

## Example Usage

### Basic Slide Box

```python
from build123d import *
from b3dkit import high_top_slide_box, high_top_slide_box_base, high_top_slide_box_lid

# Create a base shape
with BuildPart() as base_box:
    Box(50, 30, 25, align=(Align.CENTER, Align.CENTER, Align.MIN))
    fillet(base_box.part.edges().filter_by(Axis.Z), radius=2)

# Create the slide box
slide_box = high_top_slide_box(
    base_part=base_box.part,
    top_height=8,
    rail_height=6,
    wall_thickness=2.5,
)

# The result contains both lid and base
lid = slide_box.children[0]
base = slide_box.children[1]
```

### Precision Tool Box

```python
# For precision tools requiring tight tolerances
precision_box = high_top_slide_box(
    base_part=base_box.part,
    top_height=12,
    rail_height=8,
    wall_thickness=3,
    rail_angle=0.5,  # Slight angle for smoother operation
    tolerance=0.1,   # Tight fit
    divot_radius=0.3,  # Small divots
)
```

### Large Storage Box

```python
# For larger items with looser tolerances
with BuildPart() as large_base:
    Box(80, 60, 40, align=(Align.CENTER, Align.CENTER, Align.MIN))

storage_box = high_top_slide_box(
    base_part=large_base.part,
    top_height=15,
    rail_height=12,
    wall_thickness=4,
    tolerance=0.3,   # Looser fit
    divot_radius=0.8,  # Larger divots for easier operation
)
```

### Individual Components

```python
# Create just the lid for modification or separate printing
lid_only = high_top_slide_box_lid(
    base_part=base_box.part,
    top_height=8,
    rail_height=6,
    wall_thickness=2.5,
)

# Create just the base
base_only = high_top_slide_box_base(
    base_part=base_box.part,
    top_height=8,
    rail_height=6,
    wall_thickness=2.5,
)
```

## Print Settings

### Orientation
- **Base**: Print right-side up (as modeled)
- **Lid**: Print upside down (automatically oriented in the compound)

### Supports
- Generally no supports needed for either component
- Rail channels in the base are designed to print without supports
- Consider supports only for very large overhangs

### Layer Height
- 0.2mm layer height works well for most applications
- 0.15mm for higher precision requirements
- 0.3mm for draft prints or very large boxes

## Troubleshooting

### Lid Too Tight
- Increase `tolerance` value
- Check for warping in printed parts
- Sand rail contact surfaces lightly

### Lid Too Loose
- Decrease `tolerance` value
- Check printer calibration
- Consider scaling one part slightly

### Rails Binding
- Increase `rail_angle` slightly
- Ensure rails are clean of support material
- Check that rail channels printed correctly

### Divots Not Engaging
- Increase `divot_radius`
- Check that divots printed fully
- Ensure proper wall thickness for divot depth
