import sys

from dffml.df.types import Input, DataFlow
from dffml.df.base import opimp_in, op
from dffml.df.memory import MemoryOrchestrator
from dffml.operation.output import GetSingle
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.pypi import *

PACKAGE_DEPS_KWARGS = dict(
    inputs={
        "src": pypi_package_contents.op.outputs["directory"],
    },
    outputs={
        "package": pypi_package_json.op.inputs["package"]
    },
    expand=["package"],
)

@op(**PACKAGE_DEPS_KWARGS)
async def package_deps_setup_py(src: str):
    return {
        "package": []
    }

@op(**PACKAGE_DEPS_KWARGS)
async def package_deps_setup_cfg(src: str):
    return {
        "package": []
    }

@op(**PACKAGE_DEPS_KWARGS)
async def package_deps_requirements_txt(src: str):
    return {
        "package": []
    }

class TestOperations(AsyncTestCase):
    async def test_run(self):
        dataflow = DataFlow.auto(*opimp_in(sys.modules[__name__]))
        check = {"shouldi": [], "dffml-config-yaml": []}
        async with MemoryOrchestrator.withconfig({}) as orchestrator:
            async with orchestrator(dataflow) as octx:
                async for ctx, results in octx.run(
                    {
                        package_name: [
                            Input(
                                value=package_name,
                                definition=pypi_package_json.op.inputs["package"],
                            ),
                            Input(
                                value=[pypi_package_json.op.inputs["package"].name],
                                definition=GetSingle.op.inputs["spec"],
                                # definition=GetMulti.op.inputs["spec"],
                            ),
                        ]
                        for package_name in check.keys()
                    }
                ):
                    ctx_str = (await ctx.handle()).as_string()
                    with self.subTest(package=ctx_str):
                        print(results, check[ctx_str])
                        self.assertEqual(
                            check[ctx_str],
                            results[pypi_package_json.op.inputs["package"].name],
                        )
