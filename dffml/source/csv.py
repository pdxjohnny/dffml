# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Loads records from a csv file, using columns as features
"""
import csv
import ast
import itertools
import asyncio
from typing import Dict, List
from dataclasses import dataclass
from contextlib import asynccontextmanager

from ..record import Record
from .memory import MemorySource
from .file import FileSource, FileSourceConfig
from ..base import config
from ..util.entrypoint import entrypoint
from ..util.filelock import FileLock, NullFileLock
from ..configloader.configloader import ConfigLoaders

csv.register_dialect("strip", skipinitialspace=True)


CSV_SOURCE_CONFIG_DEFAULT_KEY = "key"
CSV_SOURCE_CONFIG_DEFAULT_LOADFILES_NAME = None


@config
class CSVSourceConfig(FileSourceConfig):
    key: str = CSV_SOURCE_CONFIG_DEFAULT_KEY
    loadfiles: List[str] = CSV_SOURCE_CONFIG_DEFAULT_LOADFILES_NAME

    def __post_init__(self):
        if self.loadfiles is None:
            self.loadfiles = []


# CSVSource is a bit of a mess
@entrypoint("csv")
class CSVSource(FileSource, MemorySource):
    """
    Uses a CSV file as the source of record feature data
    """

    CONFIG = CSVSourceConfig
    # We have to do a read, modify, write on the file to update it
    WRITEMODE: str = "w+"
    WRITEMODE_COMPRESSED: str = "wt"
    # Headers we've added to track data other than feature data for a record
    CSV_HEADERS = ["prediction", "confidence"]

    def __init__(self, config):
        super().__init__(config)

    async def __aenter__(self):
        await super().__aenter__()
        self._astack = await contextlib.AsyncExitStack().__aenter__()
        self._stack = contextlib.ExitStack().__enter__()
        # If we are in readwrite mode then we need to take a lock on the file
        if self.config.readwrite:
            self.filelock = self._stack.enter_context(
                FileLock(str(self.config.lockfile))
            )
        else:
            self.filelock = self._stack.enter_context(
                NullFileLock(str(self.config.lockfile))
            )
        # For loading file data from column with filename in it
        self.cfgl = await self._astack.enter_async_context(ConfigLoaders())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._stack.__exit__(exc_type, exc_value, traceback)
        await self._astack.__aexit__(exc_type, exc_value, traceback)
        return await super().__aexit__(exc_type, exc_value, traceback)

    async def _empty_file_init(self):
        return {}

    async def read_csv(self, fd):
        open_file = self.open_file
        dict_reader = csv.DictReader(fd, dialect="strip")
        # Record what headers are present when the file was opened
        if not self.config.key in dict_reader.fieldnames:
            open_file.write_back_key = False
        # Store all the records by their tag in write_out
        open_file.write_out = {}
        # If there is no key track row index to be used as key
        index = 0
        for row in dict_reader:
            # Load via ConfigLoaders if loadfiles parameter is given
            cfgl_data = {}
            for loadfile in self.config.loadfiles:
                _, cfgl_data[loadfile] = await self.cfgl.load_file(
                    row[loadfile]
                )
            # Grab key from row
            key = row.get(self.config.key, str(index))
            if self.config.key in row:
                del row[self.config.key]
            else:
                index += 1
            # Record data we are going to parse from this row (must include
            # features).
            record_data = {}
            # Parse headers we as the CSV source added
            csv_meta = {}
            row_keys = []
            # getting all keys starting with "prediction","confidence"
            for header in self.CSV_HEADERS:
                row_keys.extend(
                    list(
                        filter(
                            lambda x: x.startswith(header + "_"), row.keys()
                        )
                    )
                )
            # pop all prediction data from row and save in csv_meta
            for header in row_keys:
                value = row.get(header, None)
                if value is not None and value != "":
                    csv_meta[header] = row[header]
                    # Remove from feature data
                    del row[header]
            # Set the features
            features = {}
            for _key, _value in row.items():
                if self.config.loadfiles:
                    if _key in self.config.loadfiles:
                        _value = cfgl_data[_key]
                if _value != "":
                    try:
                        features[_key] = ast.literal_eval(_value)
                    except (SyntaxError, ValueError):
                        features[_key] = _value
            if features:
                record_data["features"] = features

            # Getting all prediction target names
            target_keys = filter(
                lambda x: x.startswith("prediction_"), csv_meta.keys()
            )
            target_keys = map(
                lambda x: x.replace("prediction_", ""), target_keys
            )

            predictions = {
                target_name: {
                    "value": str(csv_meta["prediction_" + target_name]),
                    "confidence": float(csv_meta["confidence_" + target_name]),
                }
                for target_name in target_keys
            }
            record_data.update({"prediction": predictions})
            # If there was no data in the row, skip it
            if not record_data and key == str(index - 1):
                continue
            # Add the record to our internal memory representation
            open_file.write_out[key] = Record(key, data=record_data)

    async def load_fd(self, fd):
        """
        Parses a CSV stream into Record instances
        """
        with self.open_file.lock.acquire():
            # TODO Make locking async
            await self.read_csv(fd)
        self.mem = self.open_file.write_out.get(self.config.tag, {})
        self.logger.debug("%r loaded %d records", self, len(self.mem))

    async def dump_fd(self, fd):
        """
        Dumps data into a CSV stream
        """
        with self.open_file.lock.acquire():
            await self.load_fd(fd)
            open_file = self.open_file
            open_file.write_out.setdefault(self.config.tag, {})
            open_file.write_out[self.config.tag].update(self.mem)
            # Bail if not last open source for this file
            if not (await open_file.dec()):
                return
            # Add our headers
            fieldnames = (
                [] if not open_file.write_back_key else [self.config.key]
            )
            fieldnames.append(self.config.tagcol)
            # Get all the feature names
            feature_fieldnames = set()
            prediction_fieldnames = set()
            for tag, records in open_file.write_out.items():
                for record in records.values():
                    feature_fieldnames |= set(record.data.features.keys())
                    prediction_fieldnames |= set(record.data.prediction.keys())
            fieldnames += sorted(list(feature_fieldnames))
            fieldnames += itertools.chain(
                *list(
                    map(
                        lambda key: ("prediction_" + key, "confidence_" + key),
                        list(prediction_fieldnames),
                    )
                )
            )
            self.logger.debug(f"fieldnames: {fieldnames}")
            # Write out the file
            writer = csv.DictWriter(fd, fieldnames=fieldnames)
            writer.writeheader()
            for tag, records in open_file.write_out.items():
                for record in records.values():
                    record_data = record.dict()
                    row = {name: "" for name in fieldnames}
                    # Always write the tag
                    row[self.config.tagcol] = tag
                    # Write the key if it existed
                    if open_file.write_back_key:
                        row[self.config.key] = record.key
                    # Write the features
                    for key, value in record_data.get("features", {}).items():
                        row[key] = value
                    # Write the prediction
                    if "prediction" in record_data:
                        for key, value in record_data["prediction"].items():
                            row["prediction_" + key] = value["value"]
                            row["confidence_" + key] = value["confidence"]
                    writer.writerow(row)
            del self.OPEN_CSV_FILES[self.config.filename]
            self.logger.debug(f"{self.config.filename} written")
        self.logger.debug("%r saved %d records", self, len(self.mem))
