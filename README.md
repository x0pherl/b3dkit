# b3dkit

Utilities for [build123d](https://github.com/gumyr/build123d) parts that have to be
**printed and assembled**: splitting parts too big for the bed, snapping them
together, fastening them, and venting them.

All linear dimensions are in millimeters and all angles are in degrees, matching
build123d.

## Installation

```bash
pip install b3dkit
```

Requires Python 3.11+ and build123d 0.11+. To run the `__main__` demo in each
module, which previews parts in VS Code, install the viewer extra:

```bash
pip install b3dkit[viewer]
```

## What's in it

| | |
|---|---|
| **dovetail** | Splits a `Part` into two that slide together with tight tolerances, for parts larger than your build volume. Includes a "snugtail" style suited to 3D printing, which wraps three sides for a large friction and glue surface. |
| **click_fit** | A tapered divot that prints and assembles better than a half sphere, letting parts click into place. |
| **twist_snap** | A connector and socket that lock with a twist, for joints meant to be opened repeatedly. |
| **ball_socket** | A ball mount and matching socket. |
| **bolt_fittings** | Bolt holes, countersinks, nut traps and heat-set insert recesses, sized for M3 by default. |
| **hexwall** | A honeycomb of hexagonal holes, flat or wrapped around a cone or cylinder, for venting and lightening. |
| **basic_shapes** | Rounded, polygonal, diamond and teardrop cylinders, plus the trigonometry helpers that place them. |
| **antichamfer** | Extends a face outward with a taper, like a foot or flat crown moulding. |
| **slide_box**, **high_top_slide_box** | Boxes with sliding lids. |
| **Point** | A lightweight 2D point with the geometry helpers the rest of the library needs. |

## Example

```python
from build123d import Align, Box, BuildPart, Mode
from b3dkit import DovetailStyle, Point, dovetail_split

with BuildPart(mode=Mode.PRIVATE) as oversized:
    Box(50, 40, 50, align=(Align.CENTER, Align.CENTER, Align.MIN))

# split it into a mating pair that fits the bed
tail, socket = dovetail_split(
    oversized.part,
    Point(0, -20),
    Point(0, 20),
    style=DovetailStyle.SNUGTAIL,
)
```

## Documentation

Full documentation, including a generated API reference, is at
[b3dkit.readthedocs.io](https://b3dkit.readthedocs.io).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

## History

b3dkit began as `fb-library`, a way to isolate common utilities from
[Fender-Bender](https://github.com/x0pherl/fender-bender). It outgrew that
project, and was renamed during a rewrite that reworked names and usage to feel
closer to native build123d.

## License

Licensed under the terms of the [MIT](https://choosealicense.com/licenses/mit/)
license.
