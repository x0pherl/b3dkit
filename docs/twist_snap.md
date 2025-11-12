# Click Fit Module Documentation

# twist_snap
![an illustration of a twist-snap connector and socket aligned](twist_snap.png)

## Introduction

the twist_snap module provides two functions for generating twist-snap connectors; which can be useful for creating connections that can be repeatedly opened. For example, these are used for connectors for PTFE tubes in the Fender-Bender project.



The `click_fit` module provides a divot function to create parts for snap fit connectors.

## Functions

### TwistSnapConnector

#### arguments

 - connector_radius: the base radius of the connector mechanism
 - tolerance: the spacing between the connector and the socket
 - arc_percentage: the percentage of the arc that the snapfit will cover
 - snapfit_count: how many snapfit mechanisms to add
 - snapfit_radius_extension: how far beyond the connector the snapfit extends
 - wall_width: the thickness of the wall mechanism
 - wall_depth: the depth of the wall mechanism
 - snapfit_height: the height of the snapfit mechanism

### TwistSnapSocket

#### arguments

 - connector_radius: the base radius of the connector mechanism
 - tolerance: the spacing between the connector and the socket
 - arc_percentage: the percentage of the arc that the snapfit will cover
 - snapfit_count: how many snapfit mechanisms to add
 - snapfit_radius_extension: how far beyond the connector the snapfit extends
 - wall_width: the thickness of the wall mechanism
 - wall_depth: the depth of the wall mechanism
 - snapfit_height: the height of the snapfit mechanism

## Example
```
from b3dkit import twist_snap_connector, twist_snap_socket

   connector = (
        TwistSnapConnector(
            connector_radius=4.5,
            tolerance=0.12,
            snapfit_height=2,
            snapfit_radius_extension=2 * (2 / 3) - 0.06,
            wall_width=2,
            wall_depth=2,
        )
        .rotate(Axis.X, 180)
        .move(Location((0, 0, 15)))
    )
    socket = TwistSnapSocket(
        connector_radius=4.5,
        tolerance=0.12,
        snapfit_height=2,
        snapfit_radius_extension=2 * (2 / 3) - 0.06,
        wall_width=2,
        wall_depth=2,
    )

    show(connector, socket, reset_camera=Camera.KEEP)

```