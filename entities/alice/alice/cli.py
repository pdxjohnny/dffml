import sys
import copy
import pathlib
import platform
import contextlib
import dataclasses
from typing import Dict

import dffml
import shouldi.cli
import dffml_operations_innersource.cli

from .system_context import Alice
from .threats_md import THREATS_MD_DATAFLOW


class AliceGitRepo(NamedTuple):
    directory: str
    URL: str


DFFMLCLICMD = NewType("dffml.util.cli.CMD", object)


# NOTE When CLI and operations are merged: All this is the same stuff that will
# happen to Operation config_cls structures. We need a more ergonomic API to
# obsucre the complexity dataclasses introduces when modifying fields/defaults
# within subclasses.
for dffml_cli_class_name, field_modifications in {
    "RunSingle": {
        "dataflow": {"default_factory": lambda: THREATS_MD_DATAFLOW},
        "no_echo": {"default": True},
    },
}.items():
    # Create the class and config names by prepending InnerSource
    new_class_name = "AliceThreatsMd"
    # Create a derived class
    new_class = getattr(dffml.cli.dataflow, dffml_cli_class_name).subclass(
        new_class_name, field_modifications,
    )
    # Add our new class to the global namespace
    setattr(
        sys.modules[__name__], new_class.CONFIG.__qualname__, new_class.CONFIG,
    )
    setattr(
        sys.modules[__name__], new_class.__qualname__, new_class,
    )

class ShouldiCLI(dffml.CMD):

    # TODO Overlay dataflow so that upstream shouldi install is used as part of
    # our python package evauation
    # TODO Take PURL or SW Heritage ID as an input definition
    use = shouldi.cli.ShouldI.install
    reuse = shouldi.use.Use
    contribute = dffml_operations_innersource.cli.InnerSourceCLI.run.records._set
    # diagram = ShouldiDiagram


class AliceProduceCLI(dffml.CMD):

    sbom = shouldi.project.cli.ProjectCMD.create


class AliceCLI(dffml.CMD):

    produce = AliceProduceCLI


class AliceCLI(dffml.CMD):

    shouldi = ShouldiCLI
