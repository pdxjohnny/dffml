# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import io
import atexit
import shutil
import random
import inspect
import asyncio
import logging
import tempfile
import unittest
import collections
from unittest.mock import patch
from functools import wraps
from contextlib import contextmanager, ExitStack
from typing import List, Dict, Any, Optional, Tuple, AsyncIterator

from dffml.repo import Repo
from dffml.feature import Feature, Features, DefFeature
from dffml.source.source import Sources
from dffml.source.memory import MemorySource, MemorySourceConfig
from dffml.source.file  import FileSourceConfig
from dffml.source.json  import JSONSource
from dffml.model import Model
from dffml.accuracy import Accuracy as AccuracyType
from dffml.util.asynctestcase import AsyncTestCase
from dffml.util.cli.cmd import DisplayHelp

from dffml.cli import OperationsAll, OperationsRepo, \
                      EvaluateAll, EvaluateRepo, \
                      Train, Accuracy, PredictAll, PredictRepo, \
                      ListRepos

from .test_df import OPERATIONS, OPIMPS

class ReposTestCase(AsyncTestCase):

    def setUp(self):
        super().setUp()
        self.repos = [Repo(str(random.random())) for _ in range(0, 10)]
        self.sources = Sources(MemorySource(MemorySourceConfig(repos=self.repos)))
        self.features = Features(FakeFeature())

class FakeFeature(Feature):

    NAME: str = 'fake'

    def dtype(self):
        return float # pragma: no cov

    def length(self):
        return 1 # pragma: no cov

    async def applicable(self, data):
        return True

    async def fetch(self, data):
        pass

    async def parse(self, data):
        pass

    async def calc(self, data):
        return float(data.src_url)

class FakeModel(Model):

    async def train(self, sources: Sources, features: Features,
            classifications: List[Any], steps: int, num_epochs: int):
        pass

    async def accuracy(self, sources: Sources, features: Features,
            classifications: List[Any]) -> AccuracyType:
        return AccuracyType(1.00)

    async def predict(self, repos: AsyncIterator[Repo], features: Features,
            classifications: List[Any]) -> \
                    AsyncIterator[Tuple[Repo, Any, float]]:
        async for repo in repos:
            yield repo, '', 1.0

@contextmanager
def empty_json_file():
    '''
    JSONSource will try to parse a file if it exists and so it needs to be
    given a file with an empty JSON object in it, {}.
    '''
    with tempfile.NamedTemporaryFile() as fileobj:
        fileobj.write(b'{}')
        fileobj.seek(0)
        yield fileobj

def tempjson(func):
    '''
    A decorator to call empty_json_file for testcases that need it. The
    decorator will call the function it decorates with the keyword argument
    jsonfile set to the tempfile.NamedTemporaryFile object it has created.
    '''
    @wraps(func)
    async def wrapper(*args, **kwargs):
        with empty_json_file() as jsonfile:
            return await func(*args, jsonfile=jsonfile, **kwargs)
    return wrapper

class TestListRepos(ReposTestCase):

    @tempjson
    async def test_run(self, jsonfile=None):
        config = FileSourceConfig(filename=jsonfile.name)
        async with JSONSource(config) as source:
            async with source() as sctx:
                await sctx.update(Repo('test-repo'))
        with patch('sys.stdout', new_callable=io.StringIO) as stdout:
            result = await ListRepos.cli('-sources',
                                         'primary=json',
                                         '-source-primary-filename',
                                         jsonfile.name,
                                         '-source-primary-readonly',
                                         'false')
            self.assertIn('test-repo', stdout.getvalue())

class TestOperationsAll(ReposTestCase):

    def setUp(self):
        super().setUp()
        self.repo_keys = {
            'add 40 and 2': 42,
            'multiply 42 and 10': 420
            }
        self.repos = list(map(Repo, self.repo_keys.keys()))
        self.sources = Sources(MemorySource(MemorySourceConfig(repos=self.repos)))
        self.features = Features(DefFeature('string_calculator', int, 1))
        self.cli = OperationsAll(
            ops=OPERATIONS,
            opimpn_memory_opimps=OPIMPS,
            repo_def='calc_string',
            output_specs=[(['result'], 'get_single_spec',)],
            remap=[('get_single', 'result', 'string_calculator')],
            sources=self.sources,
            features=self.features)

    async def test_run(self):
        repos = {repo.src_url: repo async for repo in self.cli.run()}
        self.assertEqual(len(repos), len(self.repos))
        for repo in self.repos:
            self.assertIn(repo.src_url, repos)
            self.assertIn('string_calculator', repos[repo.src_url].features())
            self.assertEqual(self.repo_keys[repo.src_url],
                    repos[repo.src_url]\
                    .features(['string_calculator'])['string_calculator'])

class TestOperationsRepo(TestOperationsAll):

    def setUp(self):
        super().setUp()
        self.subset = self.repos[int(len(self.repos) / 2):]
        self.cli = OperationsRepo(
            keys=[repo.src_url for repo in self.subset],
            ops=OPERATIONS,
            opimpn_memory_opimps=OPIMPS,
            repo_def='calc_string',
            output_specs=[(['result'], 'get_single_spec',)],
            remap=[('get_single', 'result', 'string_calculator')],
            sources=self.sources,
            features=self.features)

    async def test_run(self):
        repos = {repo.src_url: repo async for repo in self.cli.run()}
        self.assertEqual(len(repos), len(self.subset))
        for repo in self.subset:
            self.assertIn(repo.src_url, repos)
            self.assertIn('string_calculator', repos[repo.src_url].features())
            self.assertEqual(self.repo_keys[repo.src_url],
                    repos[repo.src_url]\
                    .features(['string_calculator'])['string_calculator'])

class TestEvaluateAll(ReposTestCase):

    def setUp(self):
        super().setUp()
        self.cli = EvaluateAll(sources=self.sources, features=self.features)

    async def test_run(self):
        repos = {repo.src_url: repo async for repo in self.cli.run()}
        self.assertEqual(len(repos), len(self.repos))
        for repo in self.repos:
            self.assertIn(repo.src_url, repos)
            self.assertIn('fake', repos[repo.src_url].features())
            self.assertEqual(float(repo.src_url),
                    repos[repo.src_url].features(['fake'])['fake'])

class TestEvaluateRepo(ReposTestCase):

    def setUp(self):
        super().setUp()
        self.subset = self.repos[int(len(self.repos) / 2):]
        self.cli = EvaluateRepo(sources=self.sources, features=self.features,
                keys=[repo.src_url for repo in self.subset])

    async def test_run(self):
        repos = {repo.src_url: repo async for repo in self.cli.run()}
        self.assertEqual(len(repos), len(self.subset))
        for repo in self.subset:
            self.assertIn(repo.src_url, repos)
            self.assertIn('fake', repos[repo.src_url].features())
            self.assertEqual(float(repo.src_url),
                    repos[repo.src_url].features(['fake'])['fake'])

class TestTrain(AsyncTestCase):

    def setUp(self):
        self.cli = Train(model=FakeModel(), model_dir=None,
                sources=Sources(MemorySource(MemorySourceConfig(repos=[]))),
                features=Features())

    async def test_run(self):
        await self.cli.run()

class TestAccuracy(AsyncTestCase):

    def setUp(self):
        self.cli = Accuracy(model=FakeModel(),
                sources=Sources(MemorySource(MemorySourceConfig(repos=[]))),
                features=Features())

    async def test_run(self):
        self.assertEqual(1.0, await self.cli.run())

class TestPredictAll(ReposTestCase):

    def setUp(self):
        super().setUp()
        self.cli = PredictAll(model=FakeModel(), sources=self.sources,
                features=self.features)

    async def test_run(self):
        repos = {repo.src_url: repo async for repo in self.cli.run()}
        self.assertEqual(len(repos), len(self.repos))
        for repo in self.repos:
            self.assertIn(repo.src_url, repos)

class TestPredictRepo(ReposTestCase):

    def setUp(self):
        super().setUp()
        self.subset = self.repos[int(len(self.repos) / 2):]
        self.cli = PredictRepo(model=FakeModel(), sources=self.sources,
                features=self.features,
                keys=[repo.src_url for repo in self.subset])

    async def test_run(self):
        repos = {repo.src_url: repo async for repo in self.cli.run()}
        self.assertEqual(len(repos), len(self.subset))
        for repo in self.subset:
            self.assertIn(repo.src_url, repos)
