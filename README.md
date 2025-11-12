# b3dkit Overview

 b3dkit is a general purpose library extending some of [build123d](https://github.com/gumyr/build123d)'s Parts and adding handy utility functions.

It's grown to include some capabilities not required by that project. Useful components include:

- dovetail: Splits a build123d `Part` object into two parts that can easily be slid together with very tight tolerances. Useful when building parts larger than your printer's build volume. This includes a "snugtail" type that is uniquely suited to 3d printing and results in very strong bonds with a high surface area for friction to hold it in place, or glue to bond.
- click_fit: a tapered profile that allows for better printing & assembly than a simple half Sphere to allow parts to "click" or snap into place when fit together. The extruded shape and the socket are both shaped carefully to allow a mix of easy assembly and good hold.
- Point: a lightweight X,Y coordinate point object with some geometric functions built into the object.
- HexWall: builds a field of hexagons with gaps in-between within a given set of bounds.

# Documentation

Complete developer documentation for b3dkit is maintained in the docs folder and on the [b3dkit documentation](https://b3dkit.readthedocs.io) site.

# Fork from fb-lbrary

The b3dkit library began as a library specific to [Fender-Bender](https://github.com/x0pherl/fender-bender): a way to externalize and isolate some common utilities, functions, & methods from the  project. It has since grown to include many parts and utilities that are not used by fender-bender. As part of a major rewrite to adhere method names and usage to feel more like Build123d native usage, we've forked and renamed the project to b3dkit, to better reflect our current purpose.


# Modifying the Source
The included source files rely on the build123d library. I recommend following the build123d installation instructions.

# Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

# License
This project is licensed under the terms of the [MIT](https://choosealicense.com/licenses/mit/) license
