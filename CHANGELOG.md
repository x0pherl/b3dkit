# Changelog

All notable changes to b3dkit are documented here. This project follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/). b3dkit is `0.x`, so breaking changes
ship in minor releases.

## [Unreleased]

## [0.5.0] - 2026-09-09

### Changed

- **`NutCut` now sits on the origin rather than straddling it.** The recess ran
  from `-head_depth` to `0` while the shaft began at `+head_depth`, so the two
  never met: the cutter came back as two solids with a `head_depth` gap, and
  subtracting it left a membrane the bolt could not pass through. It is now one
  solid spanning `0` to `head_depth + shaft_length`.

  **This moves the cutter.** It previously had to be positioned *below* a
  surface to work; it can now be placed *on* one. Anything calling `NutCut` and
  compensating for the old placement needs that compensation removed.

- **`dovetail_subpart` no longer adds each click-fit divot twice.** One copy
  landed outside the part as a free-floating sliver. Only geometry using
  `click_fit_radius` is affected; the tail's fused solid is unchanged and the
  socket's moves by 0.02%.

- **A positive `vertical_offset` no longer cuts the dovetail socket in two.**
  Tails, `vertical_offset=0` and negative offsets are all unchanged.

### Known issues

Found while adding solid-count assertions, all pre-existing and all invisible to
the `is_valid` checks that used to stand in for them:

- `TwistSnapConnector` returns five solids: a base and four snapfits that meet
  only on a shared plane and never fuse.
- `HexWall` can return partial hexagons clipped at the bounds as separate
  slivers, depending on how the grid divides the given width.
- `SNUGTAIL` splits its own tail into disconnected fins on parts wider than
  about 30mm. Pinned by `TestSnugtailWidthLimit`.


## [0.4.0] - 2026-09-08

### Removed

- **`TwistSnapConnector` no longer accepts `tolerance` or `wall_width`.** Both
  were read by nothing. All fit clearance lives on the socket, which opens its
  bore to `connector_radius + tolerance`; applying it on the connector as well
  would have doubled the gap. Geometry is unchanged.
- **`HexCylindrical` no longer accepts `rotation` or `align`.** Both were inert.
  Its cutters are positioned against the surface they wrap, so moving them off
  it is never useful. Rotate the `cylindrical` argument instead.
- **`thumb_radius` removed from `high_top_slide_box`**, where it was threaded
  through four signatures and read by nothing. It remains live in `slide_box`.
- `docs/conf.py` and `docs/Makefile`, dead Sphinx configuration that was being
  served as static assets on the published site.

### Added

- **`dovetail_split(part, start, end, **kwargs) -> tuple[Part, Part]`** builds a
  mating pair from one argument set, so the two halves cannot diverge.
- **Generated API reference.** Signatures and arguments now come from the source
  via mkdocstrings and cannot drift from it.
- **`py.typed`**, so downstream type checkers see b3dkit's annotations, and
  `b3dkit.__version__`.
- Input validation on `high_top_slide_box`: dimensions leaving less than
  `wall_thickness` above `top_height + rail_height` previously produced a part
  in three pieces and now raise.
- `CONTRIBUTING.md`, this changelog, CI across Python 3.11-3.13, and a release
  workflow publishing through PyPI Trusted Publishing.

### Changed

- **`dovetail_subpart` rejects arguments the chosen style would discard.** Each
  style uses only a subset of the shaping arguments; the rest were accepted and
  silently ignored. Passing one now raises `ValueError` naming the styles it
  applies to.
- **`Point` is stricter and immutable.** `Point((3, 4))` now works, where a
  tuple was previously mis-parsed into `Point(x=(3, 4), y=None)`; `Point(3)` and
  `Point()` raise instead of building a half-initialised point;
  `axial_distance_to` raises for any axis but `Axis.X` or `Axis.Y`, where it
  previously returned the Y distance for all of them; assigning to `x` or `y`
  raises.
- **`anti_chamfer` refuses the wrong builder.** It identified itself as
  `"chamfer"` in build123d's internal dispatch table, inheriting permission to
  run inside a `BuildSketch`, where it completed silently and did the wrong
  thing. It now raises and applies to `BuildPart` only.
- **`slide_box()` no longer packs or colours its result.** Print orientation is
  kept; bed layout and viewer tint were presentation baked into geometry. Call
  build123d's `pack()` yourself if you want the parts arranged.
- **Eight Part objects now validate their builder context** — `BallMount`,
  `BallSocket`, `SquareNutSinkhole`, `Divot`, `HexWall`, `HexCylindrical`,
  `TwistSnapConnector`, `TwistSnapSocket`. Using one inside a `BuildSketch`
  previously produced no error and the wrong output.
- **`ocp_vscode` is now an optional `[viewer]` extra.** No library code path used
  it; all nine imports fed only `__main__` demo blocks. Installing b3dkit no
  longer pulls a viewer, web server and tessellation stack.
- **Python 3.11 or newer** is required. `ocp_tessellate`, reached through
  `ocp_vscode`, imports `typing.NotRequired`, which is 3.11+.
- Documentation builds no longer install the package, so ReadTheDocs stops
  pulling the OpenCascade wheels to render Markdown.

### Fixed

- **`dovetail_subpart` silently ignored four documented arguments.**
  `linear_offset`, `tail_angle_offset`, `length_ratio` and `depth_ratio` were
  accepted, passed one level down and dropped, so the module reported full line
  coverage while four public knobs did nothing. Introduced when `subpart_section`
  was extracted in "initial T Slot dovetail support". Callers who passed none of
  them get identical geometry; callers who passed any get the geometry they
  asked for.
- **Every documented example now runs.** The documentation described functions
  that never existed (`heatsink_insert_cut`, `nut_cut`, `screw_cut`,
  `socket_subpart`, `half_part`), imported others from the wrong module, listed
  `anti_chamfer`'s arguments in the wrong order, and gave the dovetail
  `tolerance` default as 0.05 where the source says 0.025.

### Renamed

| Old | New | Notes |
|---|---|---|
| `DovetailPart` | `DovetailSubpart` | The old name read as a build123d `Part`, which is the function's return type |
| `section=` | `subpart=` | `section` collides with build123d's own slice operation |
| `slide_tolerance=` | `tolerance=` | One module used two names and three defaults for one concept |
| `nut_legnth=` | `nut_length=` | Misspelled keyword argument |
| `subpart_section` | `_subpart_slab` | Private; it lofts a Z-slab |

Ten dovetail internals and `slider_template` became private. Nothing outside the
package used them.

`from b3dkit import *` no longer re-exports build123d. The namespace went from
129 names, 72 of them third-party, to the library's own. Import `Box`, `Mode`,
`Part` and friends from `build123d`.

## [0.3.2] - 2026-09-06

First release through the automated pipeline. Contains the dovetail argument
forwarding fix, the `__all__` export surface, the `DovetailSubpart` rename and
the Python 3.11 floor.

## [0.1.5] and earlier

See the git history. b3dkit began as `fb-library`; the rename accompanied a
rewrite that reworked names and usage to feel closer to native build123d.

[Unreleased]: https://github.com/x0pherl/b3dkit/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/x0pherl/b3dkit/releases/tag/v0.5.0
[0.4.0]: https://github.com/x0pherl/b3dkit/releases/tag/v0.4.0
[0.3.2]: https://github.com/x0pherl/b3dkit/releases/tag/v0.3.2
