# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import json
import asyncio
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import Dict

from ..record import Record
from .memory import MemorySource
from .file import FileSource, FileSourceConfig
from ..util.entrypoint import entrypoint


class JSONSourceConfig(FileSourceConfig):
    pass  # pragma: no cov


@entrypoint("json")
class JSONSource(FileSource, MemorySource):
    """
    JSONSource reads and write from a JSON file on open / close. Otherwise
    stored in memory.
    """

    CONFIG = JSONSourceConfig

    async def _empty_file_init(self):
        async with self._open_json():
            return {}

    async def load_fd(self, fd):
        self.records = json.load(fd)
        self.mem = {
            key: Record(key, data=data)
            for key, data in self.records.get(self.config.tag, {}).items()
        }
        self.logger.debug("%r loaded %d records", self, len(self.mem))

    async def dump_fd(self, fd):
        self.records[self.config.tag] = {
            record.key: record.dict() for record in self.mem.values()
        }
        json.dump(self.records, fd)
        self.logger.debug("%r saved %d records", self, len(self.mem))
