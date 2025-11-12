# Slide Box

Creates slide boxes with tapered sliding mechanisms and optional thumb grips. This module provides functions for creating boxes where the lid slides smoothly on and off using a tapered design that ensures a secure fit while allowing easy operation.

## Overview

The slide box system creates a box with a base and a sliding lid that moves horizontally. Unlike the high top slide box, this design uses a tapered sliding mechanism where the lid gradually narrows as it slides into the base, creating a secure friction fit. The system includes optional thumb grips for easy operation and divots for positioning feedback.

## Functions

### slide_box

```python
def slide_box(
    part: Part,
    wall_thickness: float = 2,
    top_offset: float = 0,
    thumb_radius: float = 5,
    x_straighten_distance: float = 0,
    slide_tolerance: float = 0.15,
    divot_radius: float = 0,
) -> Compound
```

Creates a complete slide box with both the base and lid components. The lid features a tapered design for smooth sliding and secure positioning.

**Arguments:**
- `part` (Part): The base part that defines the outer dimensions of the box
- `wall_thickness` (float, default=2): Thickness of the box walls in millimeters
- `top_offset` (float, default=0): Vertical offset from the top for the sliding section
- `thumb_radius` (float, default=5): Radius of the thumb grip cutout in millimeters; set to 0 to disable
- `x_straighten_distance` (float, default=0): Distance from edges where the taper becomes straight
- `slide_tolerance` (float, default=0.15): Clearance between sliding parts in millimeters
- `divot_radius` (float, default=0): Radius of positioning divots; set to 0 to disable

**Returns:**
- `Compound`: A compound containing the base and lid parts positioned for display or printing

### slide_lid

```python
def slide_lid(
    part: Part,
    wall_thickness: float = 2,
    tolerance: float = 0.15,
    top_offset: float = 0,
    thumb_radius: float = 5,
    x_straighten_distance: float = 0,
    divot_radius: float = 0,
) -> Part
```

Creates only the sliding lid component of the box. This is useful when you need to print or modify just the lid.

**Arguments:**
- `part` (Part): The base part that defines the outer dimensions
- `wall_thickness` (float, default=2): Thickness of the box walls in millimeters
- `tolerance` (float, default=0.15): Clearance between sliding parts in millimeters
- `top_offset` (float, default=0): Vertical offset from the top for the sliding section
- `thumb_radius` (float, default=5): Radius of the thumb grip cutout in millimeters
- `x_straighten_distance` (float, default=0): Distance from edges where the taper becomes straight
- `divot_radius` (float, default=0): Radius of positioning divots

**Returns:**
- `Part`: The sliding lid part with taper and optional thumb grip

### slider_template

```python
def slider_template(
    sketch: Sketch,
    wall_thickness: float = 2,
    tolerance: float = 0.2,
    top_offset: float = 0,
    x_straighten_distance: float = 0,
    divot_radius: float = 0,
    cut_template: bool = True,
) -> Part
```

Creates a slider template part based on a 2D sketch. This is an internal function used to generate the sliding mechanism geometry.

**Arguments:**
- `sketch` (Sketch): 2D sketch defining the slider cross-section
- `wall_thickness` (float, default=2): Thickness of the walls
- `tolerance` (float, default=0.2): Clearance for the sliding fit
- `top_offset` (float, default=0): Vertical offset from the top
- `x_straighten_distance` (float, default=0): Distance for straight sections at edges
- `divot_radius` (float, default=0): Radius of divots
- `cut_template` (bool, default=True): Whether this is for cutting (True) or building (False)

**Returns:**
- `Part`: The slider template part

## Design Principles

### Tapered Sliding Mechanism
The slide box uses a unique tapered design where the lid gradually narrows as it slides into the base. This creates several advantages:
- **Self-centering**: The taper guides the lid into proper alignment
- **Secure fit**: The narrowing design creates friction that holds the lid in place
- **Smooth operation**: The 22.5-degree taper angle provides optimal sliding characteristics

### Thumb Grip
The optional thumb grip is a semicircular cutout that makes it easy to slide the lid open. The grip is angled slightly (15 degrees) for ergonomic access.

### Straightening Distance
The `x_straighten_distance` parameter controls how much of the sliding mechanism remains straight at the edges. This helps ensure the lid slides smoothly without binding at the corners.

## Design Considerations

### Tolerances
The `slide_tolerance` parameter controls the fit between the lid and base:
- **0.1mm**: Very tight fit, may require force to operate
- **0.15mm**: Standard fit (default) - smooth operation with minimal play
- **0.2-0.25mm**: Loose fit for rough printing or materials that swell

### Wall Thickness
Choose wall thickness based on your box size and intended use:
- **1.5-2mm**: Small boxes, light duty
- **2-3mm**: General purpose (recommended)
- **3-4mm**: Large boxes, heavy duty

### Top Offset
The `top_offset` parameter allows you to position the sliding mechanism below the very top of the part. This is useful when your base part has features at the top that you want to preserve.

### Straightening Distance
Use `x_straighten_distance` when:
- The box is very wide and the full taper would be too extreme
- You want more consistent sliding behavior across the width
- The base part has features near the edges that need clearance

## Example Usage

### Basic Slide Box

```python
from build123d import *
from b3dkit.slide_box import slide_box

# Create a base shape
with BuildPart() as base_box:
    Box(40, 25, 15, align=(Align.CENTER, Align.CENTER, Align.MIN))
    fillet(base_box.part.edges().filter_by(Axis.Z), radius=1.5)

# Create the slide box
box = slide_box(
    part=base_box.part,
    wall_thickness=2,
    thumb_radius=3.5,
    divot_radius=0.5
)

# The result contains both base and lid
base = box.children[0]
lid = box.children[1]
```

### Precision Slide Box

```python
# For precise sliding with minimal tolerance
precision_box = slide_box(
    part=base_box.part,
    wall_thickness=2.5,
    slide_tolerance=0.1,  # Tight fit
    thumb_radius=4,
    x_straighten_distance=3,  # Straight edges for consistent sliding
    divot_radius=0.3
)
```

### Large Storage Box

```python
# For larger boxes with more generous tolerances
with BuildPart() as large_base:
    Box(80, 50, 30, align=(Align.CENTER, Align.CENTER, Align.MIN))
    fillet(large_base.part.edges().filter_by(Axis.Z), radius=2)

storage_box = slide_box(
    part=large_base.part,
    wall_thickness=3,
    slide_tolerance=0.2,  # Looser fit for large size
    thumb_radius=6,
    x_straighten_distance=8,  # More straightening for wide box
    divot_radius=0.8
)
```

### Slide Box with Top Features

```python
# When the base part has features at the top
with BuildPart() as textured_base:
    Box(50, 30, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Add text or logo at the top
    with BuildSketch(base_textured.faces().sort_by(Axis.Z)[-1]):
        Text("TOOLS", font_size=8)
    extrude(amount=-1, mode=Mode.SUBTRACT)

slide_box_with_text = slide_box(
    part=textured_base.part,
    wall_thickness=2,
    top_offset=2,  # Keep the sliding mechanism below the text
    thumb_radius=4
)
```

### Individual Components

```python
# Create just the lid for modification
lid_only = slide_lid(
    part=base_box.part,
    wall_thickness=2,
    tolerance=0.15,
    thumb_radius=3.5,
    divot_radius=0.5
)
```

## Print Settings

### Orientation
- **Base**: Print right-side up (as modeled)
- **Lid**: Print upside down (automatically oriented in the compound)

### Supports
- **Base**: No supports needed - the tapered cutout is designed to print without supports
- **Lid**: No supports needed when printed upside down
- **Thumb grip**: Prints cleanly as a bridged semicircle

### Layer Height
- **0.15-0.2mm**: Recommended for smooth sliding surfaces
- **0.3mm**: Acceptable for draft prints or very large boxes
- **0.1mm**: For highest precision requirements

### Print Speed
- Use moderate speeds (40-60mm/s) for sliding surfaces
- Slower speeds help ensure smooth surface finish for better sliding

## Assembly and Operation

### Initial Fit
1. Test fit the lid before assuming final dimensions
2. The lid should slide smoothly with slight resistance
3. Light sanding may be needed on sliding surfaces

### Break-in Period
- New boxes may feel tight initially
- A few cycles of opening/closing will improve smoothness
- Avoid forcing if the fit is too tight

### Lubrication
- Generally not needed for PLA prints
- A tiny amount of dry lubricant can help with PETG or ABS
- Avoid wet lubricants that attract dust

## Troubleshooting

### Lid Won't Slide
- **Check tolerance**: Increase `slide_tolerance` parameter
- **Check for warping**: Ensure parts printed flat
- **Sand lightly**: Remove any print artifacts from sliding surfaces
- **Check straightening**: Increase `x_straighten_distance` if binding at edges

### Lid Too Loose
- **Decrease tolerance**: Reduce `slide_tolerance` parameter
- **Check calibration**: Verify printer is properly calibrated
- **Scale adjustment**: Consider scaling the lid up by 0.1-0.2%

### Rough Sliding
- **Layer adhesion**: Check that layers are bonding properly
- **Surface finish**: Use finer layer heights
- **Post-processing**: Light sanding with fine grit (400+)

### Thumb Grip Too Small/Large
- **Adjust radius**: Modify `thumb_radius` parameter
- **Check hand size**: Consider ergonomics for intended users
- **Alternative grips**: Set `thumb_radius=0` and add custom grip features

### Divots Not Engaging
- **Increase radius**: Try larger `divot_radius`
- **Check printing**: Ensure divots printed completely
- **Material consideration**: Some materials require larger divots for tactile feedback
