"""Generate the Python stubs from the .proto tree at build time.

The protos stay the source of truth exactly as Java consumes them; this only
stages a copy under a `rise_protocol/` prefix so the generated modules land in
one namespace instead of polluting site-packages with top-level `error` and
`common` packages.
"""

from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

ROOT = Path(__file__).parent
PROTO_ROOT = ROOT / "src" / "main" / "proto"
PACKAGE = "rise_protocol"


class ProtoBuildHook(BuildHookInterface):
    PLUGIN_NAME = "custom"

    def initialize(self, version, build_data):
        import grpc_tools
        from grpc_tools import protoc

        out = ROOT / PACKAGE
        if out.exists():
            shutil.rmtree(out)
        out.mkdir()

        with tempfile.TemporaryDirectory() as tmp:
            # Stage the whole proto tree one level down, under the package name.
            staged = Path(tmp) / PACKAGE
            shutil.copytree(PROTO_ROOT, staged)

            # Re-point the protos' own imports at the staged prefix. The files in
            # the repo are untouched; only this throwaway copy is rewritten.
            for proto in staged.rglob("*.proto"):
                text = proto.read_text()
                text = re.sub(r'import "(?!google/)([^"]+)"', rf'import "{PACKAGE}/\1"', text)
                proto.write_text(text)

            well_known = Path(grpc_tools.__file__).parent / "_proto"
            args = [
                "protoc",
                f"--proto_path={tmp}",
                f"--proto_path={well_known}",
                f"--python_out={ROOT}",
                f"--pyi_out={ROOT}",
                f"--grpc_python_out={ROOT}",
                *[str(p) for p in sorted(staged.rglob("*.proto"))],
            ]
            if protoc.main(args) != 0:
                raise RuntimeError("protoc failed")

        for directory in {p.parent for p in out.rglob("*.py")} | {out}:
            (directory / "__init__.py").touch()
