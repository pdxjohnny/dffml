import sys

from dffml.df.types import Input, Operation, DataFlow, InputFlow
from dffml.df.base import operation_in, opimp_in
from dffml.df.memory import (
    MemoryOrchestrator,
    MemoryInputSet,
    MemoryInputSetConfig,
    StringInputSetContext,
)
from dffml.df.linker import Linker
from dffml.operation.output import GetSingle
from dffml.util.cli.cmd import CMD
from dffml.util.cli.arg import Arg

from shouldi.bandit import run_bandit
from shouldi.pypi import pypi_latest_package_version
from shouldi.pypi import pypi_package_json
from shouldi.pypi import pypi_package_url
from shouldi.pypi import pypi_package_contents
from shouldi.pypi import cleanup_pypi_package
from shouldi.safety import safety_check

# sys.modules[__name__] is a list of everything we've imported in this file.
# opimp_in returns a subset of that list, any OperationImplementations
OPIMPS = opimp_in(sys.modules[__name__])

# TODO(arv1ndh) Add the auto method to DataFlow
DATAFLOW = DataFlow.auto(
    pypi_package_json,
    pypi_latest_package_version,
    pypi_package_url,
    pypi_package_contents,
    cleanup_pypi_package,
    safety_check,
    run_bandit,
    GetSingle,
)
DATAFLOW.seed.append(
    Input(
        value=[
            safety_check.op.outputs["issues"].name,
            run_bandit.op.outputs["report"].name,
        ],
        definition=GetSingle.op.inputs["spec"],
    )
)


class Install(CMD):

    arg_packages = Arg(
        "packages", nargs="+", help="Package to check if we should install"
    )

    async def run(self):
        # Create an Orchestrator which will manage the running of our operations
        async with MemoryOrchestrator.basic_config() as orchestrator:
            # Create a orchestrator context, everything in DFFML follows this
            # one-two context entry pattern
            async with orchestrator(DATAFLOW) as octx:
                # For each package add a new input set to the network of inputs
                # (ictx). Operations run under a context, the context here is
                # the package_name to evaluate (the first argument). The next
                # arguments are all the inputs we're seeding the network with
                # for that context. We give the package name because
                # pypi_latest_package_version needs it to find the version,
                # which safety will then use. We also give an input to the
                # output operation GetSingle, which takes a list of data type
                # definitions we want to select as our results.

                # Run all the operations, Each iteration of this loop happens
                # when all inputs are exhausted for a context, the output
                # operations are then run and their results are yielded
                async for package_name, results in octx.run(
                    *[
                        MemoryInputSet(
                            MemoryInputSetConfig(
                                ctx=StringInputSetContext(package_name),
                                inputs=[
                                    Input(
                                        value=package_name,
                                        definition=pypi_package_json.op.inputs[
                                            "package"
                                        ],
                                    )
                                ],
                            )
                        )
                        for package_name in self.packages
                    ]
                ):
                    # Grab the number of saftey issues and the bandit report
                    # from the results dict
                    safety_issues = results[
                        safety_check.op.outputs["issues"].name
                    ]
                    bandit_report = results[
                        run_bandit.op.outputs["report"].name
                    ]
                    if (
                        safety_issues > 0
                        or bandit_report["CONFIDENCE.HIGH_AND_SEVERITY.HIGH"]
                        > 5
                    ):
                        print(f"Do not install {package_name}! {results!r}")
                    else:
                        print(f"{package_name} is okay to install")


class ShouldI(CMD):

    install = Install
