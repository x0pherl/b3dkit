# High Top Slide Box

Creates slide boxes with tall tops and precise sliding rail mechanisms. This module provides functions for creating boxes where the lid slides on and off with rails, making them ideal for tool storage, organizers, and other applications requiring secure but easily accessible storage.

## Overview

The high top slide box system creates a box with a base and a sliding lid that moves along rails. The "high top" design means the lid has significant height, making it suitable for storing taller items or creating compartmentalized storage. The sliding mechanism uses diamond-shaped rails for smooth operation and includes optional divots for secure positioning.

## Functions

### high_top_slide_box

```python
def high_top_slide_box(
    base_part: Part,
    top_height: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    divot_radius: float = 0.5,
    thumb_radius: float = 0,
    tolerance: float = 0.2,
) -> Compound
```

Creates a complete slide box with both the base and lid components. Returns a compound containing both parts positioned for display or printing.

**Arguments:**
- `base_part` (Part): The base part that defines the outer dimensions of the box
- `top_height` (float): Height of the sliding top portion in millimeters
- `rail_height` (float): Height of the rail system that guides the sliding motion
- `wall_thickness` (float): Thickness of the box walls in millimeters
- `rail_angle` (float, default=0): Angle of the rails in degrees for smoother sliding
- `divot_radius` (float, default=0.5): Radius of positioning divots; set to 0 to disable
- `thumb_radius` (float, default=0): Radius for thumb grips (currently unused)
- `tolerance` (float, default=0.2): Clearance between moving parts in millimeters

**Returns:**
- `Compound`: A compound containing the lid (rotated for printing) and base parts

### high_top_slide_box_lid

```python
def high_top_slide_box_lid(
    base_part: Part,
    top_height: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    divot_radius: float = 0.5,
    thumb_radius: float = 0,
    tolerance: float = 0.2,
) -> Part
```

Creates only the sliding lid component of the box. This is useful when you need to print or modify just the lid.

**Arguments:**
- Same as `high_top_slide_box`

**Returns:**
- `Part`: The sliding lid part with rails and divots

### high_top_slide_box_base

```python
def high_top_slide_box_base(
    base_part: Part,
    top_height: float,
    rail_height: float,
    wall_thickness: float,
    rail_angle: float = 0,
    divot_radius: float = 0.5,
    thumb_radius: float = 0,
    tolerance: float = 0.2,
) -> Part
```

Creates only the base component of the box. This includes the hollowed-out interior and the rail channels that guide the lid.

**Arguments:**
- Same as `high_top_slide_box`

**Returns:**
- `Part`: The base part with hollowed interior and rail channels

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
from b3dkit.high_top_slide_box import high_top_slide_box

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
