from unittest.mock import patch
from typing import NamedTuple

from dffml import (
    run,
    DataFlow,
    GetSingle,
    Input,
    Definition,
    op,
    OperationException,
)
from dffml.util.cli.arg import Arg, parse_unknown
from dffml.util.entrypoint import entrypoint
from dffml.df.base import BaseKeyValueStore, BaseRedundancyCheckerConfig
from dffml.df.memory import MemoryKeyValueStore, MemoryRedundancyChecker
from dffml.util.asynctestcase import AsyncTestCase


class KeyValueStoreWithArgumentsConfig(NamedTuple):
    filename: str


@entrypoint("withargs")
class KeyValueStoreWithArguments(BaseKeyValueStore):

    CONTEXT = NotImplementedError

    def __call__(self):
        raise NotImplementedError

    @classmethod
    def args(cls, args, *above):
        cls.config_set(args, above, "filename", Arg(type=str))
        return args

    @classmethod
    def config(cls, config, *above):
        return KeyValueStoreWithArgumentsConfig(
            filename=cls.config_get(config, above, "filename")
        )


def load_kvstore_with_args(loading=None):
    if loading == "withargs":
        return KeyValueStoreWithArguments
    return [KeyValueStoreWithArguments]


class TestMemoryRedundancyChecker(AsyncTestCase):
    @patch.object(BaseKeyValueStore, "load", load_kvstore_with_args)
    def test_args(self):
        self.assertEqual(
            MemoryRedundancyChecker.args({}),
            {
                "rchecker": {
                    "plugin": None,
                    "config": {
                        "memory": {
                            "plugin": None,
                            "config": {
                                "kvstore": {
                                    "plugin": Arg(
                                        type=BaseKeyValueStore.load,
                                        default=MemoryKeyValueStore,
                                    ),
                                    "config": {
                                        "withargs": {
                                            "plugin": None,
                                            "config": {
                                                "filename": {
                                                    "plugin": Arg(type=str),
                                                    "config": {},
                                                }
                                            },
                                        }
                                    },
                                }
                            },
                        }
                    },
                }
            },
        )

    @patch.object(BaseKeyValueStore, "load", load_kvstore_with_args)
    def test_config_default_label(self):
        was = MemoryRedundancyChecker.config(
            parse_unknown(
                "--rchecker-memory-kvstore",
                "withargs",
                "--rchecker-memory-kvstore-withargs-filename",
                "somefile",
            )
        )
        self.assertEqual(type(was), BaseRedundancyCheckerConfig)
        self.assertEqual(type(was.key_value_store), KeyValueStoreWithArguments)
        self.assertEqual(
            type(was.key_value_store.config), KeyValueStoreWithArgumentsConfig
        )
        self.assertEqual(was.key_value_store.config.filename, "somefile")


@op(
    outputs={"result": Definition(name="fail_result", primitive="string")},
    retry=3,
)
async def fail_and_retry(self):
    i = getattr(self.parent, "i", 0)
    i += 1
    setattr(self.parent, "i", i)
    if i <= 2:
        raise Exception(f"Failure {i}")
    return {"result": "done"}


class TestMemoryOperationImplementationNetworkContext(AsyncTestCase):
    @staticmethod
    async def run_dataflow(dataflow):
        async for ctx, results in run(
            dataflow,
            [
                Input(
                    value=[fail_and_retry.op.outputs["result"].name],
                    definition=GetSingle.op.inputs["spec"],
                ),
            ],
        ):
            yield results

    async def test_retry_success(self):
        done = False
        async for results in self.run_dataflow(
            DataFlow.auto(fail_and_retry, GetSingle)
        ):
            done = True
            self.assertEqual(results, {"fail_result": "done"})
        self.assertTrue(done)

    async def test_retry_fail(self):
        dataflow = DataFlow.auto(fail_and_retry, GetSingle)
        dataflow.operations["fail_and_retry"] = dataflow.operations[
            "fail_and_retry"
        ]._replace(retry=dataflow.operations["fail_and_retry"].retry - 1)

        try:
            async for results in self.run_dataflow(dataflow):
                pass
        except OperationException as error:
            self.assertEqual(error.__cause__.__class__, Exception)
            self.assertEqual(error.__cause__.args[0], "Failure 2")
