from functools import wraps
from unittest.mock import patch
from typing import NamedTuple

from dffml.util.data import traverse_config_set
from dffml.util.cli.arg import Arg, parse_unknown
from dffml.util.entrypoint import entry_point
from dffml.df.base import BaseKeyValueStore, BaseRedundancyCheckerConfig
from dffml.df.memory import MemoryKeyValueStore, MemoryRedundancyCheckerConfig, MemoryRedundancyChecker
from dffml.util.asynctestcase import AsyncTestCase


class KeyValueStoreWithArgumentsConfig(NamedTuple):
    filename: str


@entry_point("withargs")
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
    @patch.object(MemoryRedundancyCheckerConfig.kvstore, load_kvstore_with_args)
    def test_args(self):
        self.maxDiff = 99999
        self.assertEqual(
            MemoryRedundancyChecker.args({}),
            {
                "rchecker": {
                    "arg": None,
                    "config": {
                        "memory": {
                            "arg": None,
                            "config": {
                                "kvstore": {
                                    "arg": Arg(
                                        type=BaseKeyValueStore.load,
                                        default=MemoryKeyValueStore,
                                    ),
                                    "config": {
                                        "withargs": {
                                            "arg": None,
                                            "config": {
                                                "filename": {
                                                    "arg": Arg(type=str),
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
        self.assertEqual(type(was), MemoryRedundancyCheckerConfig)
        self.assertEqual(type(was.kvstore), KeyValueStoreWithArguments)
        self.assertEqual(
            type(was.kvstore.config), KeyValueStoreWithArgumentsConfig
        )
        self.assertEqual(was.kvstore.config.filename, "somefile")
