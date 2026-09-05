import os

# Absolute path to the package source, so tests that load a module by file path
# work regardless of the directory pytest was invoked from.
PACKAGE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src", "b3dkit")
)


def module_path(module_name: str) -> str:
    """Absolute path to a b3dkit source file, e.g. module_path("dovetail")."""
    return os.path.join(PACKAGE_DIR, f"{module_name}.py")
