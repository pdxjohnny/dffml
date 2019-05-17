import json
from unittest.mock import patch
from typing import NamedTuple

from dffml.util.data import traverse_config_set
from dffml.util.cli.arg import Arg
from dffml.df.base import BaseKeyValueStore, BaseRedundancyCheckerConfig
from dffml.df.memory import MemoryKeyValueStore, MemoryRedundancyChecker
from dffml.util.asynctestcase import AsyncTestCase


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except:
            return repr(obj)


class KeyValueStoreWithArgumentsConfig(NamedTuple):
    filename: str


class KeyValueStoreWithArguments(BaseKeyValueStore):

    ENTRY_POINT_ORIG_LABEL = "withargs"
    CONTEXT = True

    @classmethod
    def args(cls, args, *above):
        above = cls.add_orig_label(*above)
        traverse_config_set(args, *above, "filename", Arg(type=str))
        return args

    @classmethod
    def config(cls, config, *above):
        args = cls.args({}, *above)
        above = cls.add_orig_label(*above)
        return KeyValueStoreWithArgumentsConfig(
            filename=cls.config_get(args, config, *above, "filename")
        )


class TestMemoryRedundancyChecker(AsyncTestCase):
    @property
    def extra_config_args(self):
        return {
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
        }

    def __load_kvstore_with_args(self, loading=None):
        if loading == "withargs":
            return KeyValueStoreWithArguments
        return [KeyValueStoreWithArguments]

    def test_args(self):
        with patch.object(
            BaseKeyValueStore, "load", self.__load_kvstore_with_args
        ):
            was = MemoryRedundancyChecker.args({})
            self.assertEqual(was, self.extra_config_args)

    def test_config_default_label(self):
        with patch.object(
            BaseKeyValueStore, "load", self.__load_kvstore_with_args
        ):
            config = {
                "rchecker": {
                    "arg": None,
                    "config": {
                        "memory": {
                            "arg": None,
                            "config": {
                                "kvstore": {
                                    "arg": ["withargs"],
                                    "config": {
                                        "withargs": {
                                            "arg": None,
                                            "config": {
                                                "filename": {
                                                    "arg": ["somefile"],
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
            }
            was = MemoryRedundancyChecker.config(config)
            self.assertEqual(type(was), BaseRedundancyCheckerConfig)
            self.assertEqual(
                type(was.key_value_store), KeyValueStoreWithArguments
            )
            self.assertEqual(
                type(was.key_value_store.config),
                KeyValueStoreWithArgumentsConfig,
            )
            self.assertEqual(was.key_value_store.config.filename, "somefile")
