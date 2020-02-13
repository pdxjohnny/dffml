import sys
import pathlib
import argparse
import unittest.mock
import importlib.util

from dffml.base import config
from dffml.util.os import chdir
from dffml.df.base import opimp_in, op
from dffml.df.types import Input, DataFlow
from dffml.service.dev import SetupPyKWArg
from dffml.operation.output import GetMulti
from dffml.df.memory import MemoryOrchestrator
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.pypi import *


def remove_package_versions(packages):
    no_versions = []

    appended = False
    for package in packages:
        for char in [">", "<", "="]:
            if char in package:
                no_versions.append(package.split(char)[0].strip())
                appended = True
                break
        if not appended:
            no_versions.append(package.strip())
        appended = False

    return no_versions


PACKAGE_DEPS_KWARGS = dict(
    inputs={"src": pypi_package_contents.op.outputs["directory"],},
    outputs={"package": pypi_package_json.op.inputs["package"]},
    expand=["package"],
)


@op(**PACKAGE_DEPS_KWARGS)
async def package_deps_setup_py(src: str):
    setup_py_path = list(pathlib.Path(src).rglob("**/setup.py"))
    if not setup_py_path:
        return

    setup_py_path = setup_py_path[0]

    deps = SetupPyKWArg.get_kwargs(str(setup_py_path)).get(
        "install_requires", []
    )

    no_versions = {}

    print(src, remove_package_versions(deps))

    return {"package": remove_package_versions(deps)}


@op(**PACKAGE_DEPS_KWARGS)
async def package_deps_setup_cfg(src: str):
    # TODO
    return {"package": []}


@op(**PACKAGE_DEPS_KWARGS)
async def package_deps_requirements_txt(src: str):
    # TODO
    return {"package": []}


SUBFLOW = DataFlow.auto(*[opimp for opimp in opimp_in(sys.modules[__name__])])
SUBFLOW.seed.append(
    Input(
        value=[pypi_package_json.op.inputs["package"].name],
        definition=GetMulti.op.inputs["spec"],
    )
)
# Do not allow package names in the subflow to re-trigger the whole subflow
# again, since this will cause version numbers and directories to get crossed
SUBFLOW.flow["pypi_package_json"].inputs["package"] = ["seed"]
SUBFLOW.update_by_origin()


def create_parent_flow():
    """
    This function exists so that shouldi_dataflow_as_operation doesn't end up
    in the subflow when we grab from sys.modules[__name__]
    """

    @config
    class ShouldIDataFlowAsOperationConfig:
        dataflow: DataFlow

    @op(
        inputs={"package": pypi_package_json.op.inputs["package"]},
        outputs={"package": pypi_package_json.op.inputs["package"]},
        expand=["package"],
        config_cls=ShouldIDataFlowAsOperationConfig,
    )
    async def shouldi_dataflow_as_operation(self, package: str):
        async with self.octx.parent(self.config.dataflow) as octx:
            async for ctx, result in octx.run(
                {
                    package: [
                        Input(
                            value=package,
                            definition=self.parent.op.inputs["package"],
                        )
                    ]
                }
            ):
                packages = result[self.parent.op.inputs["package"].name]
                # Remove input package from list
                packages = list(filter(lambda pkg: pkg != package, packages))
                # TODO Deduplicate
                return {"package": packages}

    dataflow = DataFlow.auto(shouldi_dataflow_as_operation, GetMulti)
    dataflow.seed.append(
        Input(
            value=[pypi_package_json.op.inputs["package"].name],
            definition=GetMulti.op.inputs["spec"],
        )
    )
    dataflow.configs[
        "shouldi_dataflow_as_operation"
    ] = ShouldIDataFlowAsOperationConfig(dataflow=SUBFLOW)
    dataflow.flow["shouldi_dataflow_as_operation"].inputs["package"].append(
        "seed"
    )
    dataflow.update_by_origin()
    return dataflow


DATAFLOW = create_parent_flow()


class TestOperations(AsyncTestCase):
    async def test_run(self):
        check = {"shouldi": [], "dffml-config-yaml": []}
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(DATAFLOW) as octx:
                async for ctx, results in octx.run(
                    {
                        package_name: [
                            Input(
                                value=package_name,
                                definition=pypi_package_json.op.inputs[
                                    "package"
                                ],
                            ),
                        ]
                        for package_name in check.keys()
                    }
                ):
                    ctx_str = (await ctx.handle()).as_string()
                    with self.subTest(package=ctx_str):
                        print(ctx_str, results)
                        print(DATAFLOW.flow)
                        continue
                        self.assertEqual(
                            check[ctx_str],
                            results[
                                pypi_package_json.op.inputs["package"].name
                            ],
                        )
