# API Reference

Generated from the source, so it cannot drift from the code.

b3dkit's public API is the 38 names in `b3dkit.__all__`, all re-exported from the top-level package. Anything not listed is an implementation detail.

```python
from b3dkit import Divot, HexWall, Point, dovetail_split
```

| Module | Exports |
|---|---|
| [`antichamfer`](antichamfer.md) | `anti_chamfer` |
| [`ball_socket`](ball_socket.md) | `BallMount`, `BallSocket` |
| [`basic_shapes`](basic_shapes.md) | `radius_to_apothem`, `apothem_to_radius`, `opposite_length`, `adjacent_length`, `distance_to_circle_edge`, `circular_intersection`, `DiamondTorus`, `RoundedCylinder`, `PolygonalCylinder`, `DiamondCylinder`, `Teardrop`, `TeardropCylinder` |
| [`bolt_fittings`](bolt_fittings.md) | `TeardropBoltCutSinkhole`, `BoltCutSinkhole`, `SquareNutSinkhole`, `NutCut`, `ScrewCut`, `HeatsinkCut` |
| [`click_fit`](click_fit.md) | `Divot` |
| [`dovetail`](dovetail.md) | `DovetailSubpart`, `DovetailStyle`, `dovetail_subpart`, `dovetail_split` |
| [`hexwall`](hexwall.md) | `HexWall`, `HexCylindrical` |
| [`high_top_slide_box`](high_top_slide_box.md) | `high_top_slide_box_lid`, `high_top_slide_box_base`, `high_top_slide_box` |
| [`point`](point.md) | `Point`, `midpoint`, `shifted_midpoint` |
| [`slide_box`](slide_box.md) | `slide_lid`, `slide_box` |
| [`twist_snap`](twist_snap.md) | `TwistSnapConnector`, `TwistSnapSocket` |
