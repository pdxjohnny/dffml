# pylint: disable=missing-docstring,no-self-use
import os
import logging
import unittest

from dffml import AsyncTestCase, run_doctest

from dffml_feature_git.util.github import GitHub

# logging.basicConfig(level=logging.DEBUG)


def get_token():
    if "GITHUB_TOKEN" in os.environ:
        return os.environ["GITHUB_TOKEN"]
    try:
        import keyring
    except ImportError:
        return
    token = keyring.get_password("github", "api.token")
    if token is not None:
        return token


TOKEN = get_token()


class TestGitHub(AsyncTestCase):
    def test_owner_project(self):
        run_doctest(GitHub.owner_project, {"globs": {"GitHub": GitHub}})

    async def setUp(self):
        if TOKEN is None:
            return
        self.github = await GitHub(token=TOKEN).__aenter__()
        self.ctx = await self.github().__aenter__()

    async def tearDown(self):
        if not hasattr(self, "ctx"):
            return
        await self.ctx.__aexit__(None, None, None)
        await self.github.__aexit__(None, None, None)

    @unittest.skipUnless(TOKEN, "GitHub token required")
    async def test_github_issues(self):
        issues = [issue async for issue in self.ctx.issues("intel", "dffml")]
        print(issues[0])
        self.assertGreater(len(issues), 466)

    @unittest.skipUnless(TOKEN, "GitHub token required")
    async def test_github_pull_requests(self):
        pull_requests = [
            pull_request
            async for pull_request in self.ctx.pull_requests("intel", "dffml")
        ]
        print(pull_requests[0])
        self.assertGreater(len(pull_requests), 362)
