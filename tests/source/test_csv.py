# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import unittest

from dffml.source.file import FileSourceConfig
from dffml.source.csv import CSVSource
from dffml.util.testing.source import FileSourceTest
from dffml.util.asynctestcase import AsyncTestCase


class TestCSVSource(FileSourceTest, AsyncTestCase):
    async def setUpSource(self):
        return CSVSource(FileSourceConfig(filename=self.testfile))

    @unittest.skip("Labels not implemented yet for CSV files")
    async def test_label(self):
        """
        Labels not implemented yet for CSV files
        """
