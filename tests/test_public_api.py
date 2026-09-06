"""Invariants over b3dkit's whole public surface.

These walk ``__all__`` rather than naming symbols one by one, so a new export
is held to the same contract as the existing ones without anyone remembering to
add a test. Encoding the rules as tests rather than prose matters here: the
project has one maintainer, so every change is self-reviewed.
"""

import ast
import inspect
import pathlib
import types

import pytest
from build123d import BasePartObject, BaseSketchObject

import b3dkit

SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "b3dkit"

PUBLIC_NAMES = sorted(b3dkit.__all__)
#: Objects that position their result against a shape they are given, for which
#: rotation and align cannot mean anything. See HexCylindrical.
POSITIONED_AGAINST_INPUT = {"HexCylindrical"}

PART_OBJECTS = sorted(
    name
    for name in b3dkit.__all__
    if isinstance(getattr(b3dkit, name), type)
    and issubclass(getattr(b3dkit, name), (BasePartObject, BaseSketchObject))
)


class TestExportSurface:
    def test_all_is_sorted_into_module_groups_and_complete(self):
        for name in b3dkit.__all__:
            assert hasattr(b3dkit, name), f"{name} is in __all__ but not importable"

    def test_star_import_matches_all_exactly(self):
        namespace: dict = {}
        exec("from b3dkit import *", namespace)  # noqa: S102
        exported = {k for k in namespace if not k.startswith("_")}
        assert exported == set(b3dkit.__all__)

    @pytest.mark.parametrize("name", PUBLIC_NAMES)
    def test_every_export_is_ours(self, name):
        """b3dkit must not re-export build123d, ocp_vscode or the stdlib.

        Wildcard imports previously leaked 72 third-party names into the
        package namespace, which under SemVer would have made b3dkit's public
        surface hostage to build123d's release cadence.
        """
        obj = getattr(b3dkit, name)
        module = getattr(obj, "__module__", None)
        assert module is not None, f"{name} has no __module__"
        assert module.startswith("b3dkit"), f"{name} is re-exported from {module}"

    def test_no_submodule_shadows_a_module_it_does_not_own(self):
        for name in b3dkit.__all__:
            assert not isinstance(
                getattr(b3dkit, name), types.ModuleType
            ), f"{name} in __all__ is a module, not an API symbol"


class TestDocumented:
    @pytest.mark.parametrize("name", PUBLIC_NAMES)
    def test_every_export_has_a_docstring(self, name):
        obj = getattr(b3dkit, name)
        doc = inspect.getdoc(obj)
        if isinstance(obj, type) and not doc:
            doc = inspect.getdoc(obj.__init__)
        assert doc and doc.strip(), f"{name} has no docstring"


class TestPartObjectContract:
    """Tier 1: an object built inside a builder must validate that context.

    Without the preamble a Part object used inside a BuildSketch produced no
    error and the wrong output. Eight of the nineteen were missing it.
    """

    @pytest.mark.parametrize("name", PART_OBJECTS)
    def test_declares_builder_preamble(self, name):
        """Satisfied by the class itself or by a b3dkit base it delegates to.

        DiamondCylinder and BoltCutSinkhole are thin subclasses that forward to
        PolygonalCylinder and TeardropBoltCutSinkhole via super().__init__, so
        the parent's preamble runs on their behalf.
        """
        sources = [
            inspect.getsource(klass)
            for klass in getattr(b3dkit, name).__mro__
            if getattr(klass, "__module__", "").startswith("b3dkit")
        ]
        assert any(
            "_get_context" in src for src in sources
        ), f"neither {name} nor any b3dkit base asks for a builder context"
        assert any(
            "validate_inputs" in src for src in sources
        ), f"neither {name} nor any b3dkit base validates its inputs"

    @pytest.mark.parametrize("name", PART_OBJECTS)
    def test_signature_ends_with_rotation_align_mode(self, name):
        """build123d's own objects end this way; ours should read the same.

        HexCylindrical is exempt and takes mode only. It positions its result
        against a shape it is given, so rotation and align cannot mean anything
        for it -- both were measurably inert when it still offered them.
        """
        params = list(inspect.signature(getattr(b3dkit, name)).parameters)
        if name in POSITIONED_AGAINST_INPUT:
            assert params[-1] == "mode", f"{name} should still end with mode"
            assert (
                "rotation" not in params and "align" not in params
            ), f"{name} positions against its input; rotation and align would be inert"
            return
        assert params[-3:] == [
            "rotation",
            "align",
            "mode",
        ], f"{name} ends with {params[-3:]}, not ['rotation', 'align', 'mode']"


class TestNoPrivateBuild123dCoupling:
    """b3dkit may use build123d's documented extension points, not its tables.

    anti_chamfer identified itself as "chamfer" in build123d's internal
    operations_apply_to dict, inheriting a looser contract than it could honour.
    """

    def test_no_module_references_operations_apply_to(self):
        for path in sorted(SRC.glob("*.py")):
            code = "\n".join(
                line
                for line in path.read_text().splitlines()
                if not line.strip().startswith("#")
            )
            assert (
                "operations_apply_to" not in code
            ), f"{path.name} reaches into build123d's operations table"

    def test_validate_inputs_is_never_called_with_a_string(self):
        """Passing a string routes through the private table; pass self."""
        for path in sorted(SRC.glob("*.py")):
            for node in ast.walk(ast.parse(path.read_text())):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "validate_inputs"
                    and len(node.args) >= 2
                ):
                    assert not isinstance(node.args[1], ast.Constant), (
                        f"{path.name}:{node.lineno} passes a literal to "
                        "validate_inputs, borrowing another operation's identity"
                    )


class TestHeadlessImport:
    def test_library_code_never_imports_the_viewer_at_module_scope(self):
        """ocp_vscode is an optional extra; only __main__ demos may use it."""
        offenders = []
        for path in sorted(SRC.glob("*.py")):
            for node in ast.parse(path.read_text()).body:  # top level only
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    name = getattr(node, "module", None) or ""
                    if "ocp_vscode" in name:
                        offenders.append(f"{path.name}:{node.lineno}")
        assert not offenders, f"module-scope viewer imports: {offenders}"
