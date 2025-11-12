# Anti Chamfer Module Documentation

## Overview

The `antichamfer` module provides functionality to create anti-chamfers. An anti-chamfer extends outward from a face, similar to a foot or flat crown molding, rather than cutting inward like a traditional chamfer. This is useful for creating bases, flanges, or decorative edges that extend beyond the original part geometry.

## Functions

### anti_chamfer

#### arguments

 - length: the depth of the anti-chamfer (how far to offset inward from the original face)
 - length2: the width of the taper at the bottom (optional, defaults to length if not specified)
 - face: the face or faces to apply the anti-chamfer to (can be a single Face or an iterable of Faces)

The function creates a tapered extrusion that extends outward from the specified faces. The taper angle is calculated based on the ratio of length2 to length, creating different bevel profiles depending on these values.

## Usage Notes

- When length2 is not specified, the anti-chamfer creates a 45-degree bevel
- When length2 is smaller than length, the bevel is steeper (more vertical)
- When length2 is larger than length, the bevel is more gradual (more horizontal)
- The function automatically handles both single Face objects and collections of faces

## Example
```python
from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Location,
    fillet,
)
from b3dkit.antichamfer import anti_chamfer

# Create a basic box
with BuildPart() as base_part:
    Box(20, 20, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))

# Apply anti-chamfer to the top face with equal length values (45-degree bevel)
result = anti_chamfer(
    base_part.faces().filter_by(Axis.Z)[-1],  # top face
    2.0,  # length
    2.0,  # length2
    
)

# Apply anti-chamfer to multiple faces with different taper
with BuildPart() as complex_part:
    Box(30, 15, 8)
    fillet(complex_part.edges().filter_by(Axis.Z), 1)

# Anti-chamfer on top and bottom faces with steeper taper
anti_chamfered = anti_chamfer(
    [
        complex_part.faces().filter_by(Axis.Z)[-1],  # top
        complex_part.faces().filter_by(Axis.Z)[0]    # bottom
    ],
    1.5,   # length
    0.8,   # length2 - Creates steeper angle
)
```
