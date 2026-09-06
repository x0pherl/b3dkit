"""build123d libraries and utilities.

The names listed in ``__all__`` are b3dkit's public API; anything else is an
implementation detail.
"""

from importlib.metadata import PackageNotFoundError, version

from b3dkit.antichamfer import anti_chamfer
from b3dkit.ball_socket import BallMount, BallSocket
from b3dkit.basic_shapes import (
    DiamondCylinder,
    DiamondTorus,
    PolygonalCylinder,
    RoundedCylinder,
    Teardrop,
    TeardropCylinder,
    adjacent_length,
    apothem_to_radius,
    circular_intersection,
    distance_to_circle_edge,
    opposite_length,
    radius_to_apothem,
)
from b3dkit.bolt_fittings import (
    BoltCutSinkhole,
    HeatsinkCut,
    NutCut,
    ScrewCut,
    SquareNutSinkhole,
    TeardropBoltCutSinkhole,
)
from b3dkit.click_fit import Divot
from b3dkit.dovetail import (
    DovetailStyle,
    DovetailSubpart,
    dovetail_split,
    dovetail_subpart,
)
from b3dkit.hexwall import HexCylindrical, HexWall
from b3dkit.high_top_slide_box import (
    high_top_slide_box,
    high_top_slide_box_base,
    high_top_slide_box_lid,
)
from b3dkit.point import Point, midpoint, shifted_midpoint
from b3dkit.slide_box import slide_box, slide_lid
from b3dkit.twist_snap import TwistSnapConnector, TwistSnapSocket

try:
    __version__ = version("b3dkit")
except PackageNotFoundError:  # running from a source tree without an install
    __version__ = "unknown"

__all__ = [
    # antichamfer
    "anti_chamfer",
    # ball_socket
    "BallMount",
    "BallSocket",
    # basic_shapes
    "DiamondCylinder",
    "DiamondTorus",
    "PolygonalCylinder",
    "RoundedCylinder",
    "Teardrop",
    "TeardropCylinder",
    "adjacent_length",
    "apothem_to_radius",
    "circular_intersection",
    "distance_to_circle_edge",
    "opposite_length",
    "radius_to_apothem",
    # bolt_fittings
    "BoltCutSinkhole",
    "HeatsinkCut",
    "NutCut",
    "ScrewCut",
    "SquareNutSinkhole",
    "TeardropBoltCutSinkhole",
    # click_fit
    "Divot",
    # dovetail
    "DovetailSubpart",
    "DovetailStyle",
    "dovetail_subpart",
    "dovetail_split",
    # hexwall
    "HexCylindrical",
    "HexWall",
    # high_top_slide_box
    "high_top_slide_box",
    "high_top_slide_box_base",
    "high_top_slide_box_lid",
    # point
    "Point",
    "midpoint",
    "shifted_midpoint",
    # slide_box
    "slide_box",
    "slide_lid",
    # twist_snap
    "TwistSnapConnector",
    "TwistSnapSocket",
]
