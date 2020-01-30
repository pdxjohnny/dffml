import sys
import pathlib
import argparse
import unittest.mock
import importlib.util

from dffml.df.types import Input, DataFlow
from dffml.df.base import opimp_in, op
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase
from dffml.util.os import chdir

from shouldi.pypi import *


def get_kwargs(setup_filepath: str):
    setup_kwargs = {}

    def grab_setup_kwargs(**kwargs):
        setup_kwargs.update(kwargs)

    with chdir(pathlib.Path(setup_filepath).parent):
        spec = importlib.util.spec_from_file_location("setup", setup_filepath)
        with unittest.mock.patch("setuptools.setup", new=grab_setup_kwargs):
            setup = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(setup)

    return setup_kwargs


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

    deps = get_kwargs(str(setup_py_path)).get("install_requires", [])

    no_versions = {}

    print(src, remove_package_versions(deps))

    return {"package": remove_package_versions(deps)}


@op(**PACKAGE_DEPS_KWARGS)
async def package_deps_setup_cfg(src: str):
    return {"package": []}


@op(**PACKAGE_DEPS_KWARGS)
async def package_deps_requirements_txt(src: str):
    return {"package": []}


DATAFLOW = DataFlow.auto(*opimp_in(sys.modules[__name__]))
DATAFLOW.flow["pypi_package_json"].inputs["package"].append("seed")
DATAFLOW.update_by_origin()


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
                            Input(
                                value=[
                                    pypi_package_json.op.inputs["package"].name
                                ],
                                definition=GetSingle.op.inputs["spec"],
                                # definition=GetMulti.op.inputs["spec"],
                            ),
                        ]
                        for package_name in check.keys()
                    }
                ):
                    ctx_str = (await ctx.handle()).as_string()
                    with self.subTest(package=ctx_str):
                        print(ctx_str, results)
                        continue
                        self.assertEqual(
                            check[ctx_str],
                            results[
                                pypi_package_json.op.inputs["package"].name
                            ],
                        )
