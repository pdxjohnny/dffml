import os
import itertools

import bandit
from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from shouldi.bandit import bandit_issues


class TestBanditIssues(AsyncTestCase):
    async def test_run(self):
        async with bandit_issues.imp(BaseConfig()) as op:
            async with op(None, None) as ctx:
                # Grab the confidence structure from the results. Scan bandit
                # itself because it usually catches its own test code.
                results = (
                    await ctx.run({"source": os.path.dirname(bandit.__file__)})
                )["confidence"]
                # Check that there were any issues found by expanding all of the
                # confidence values
                self.assertTrue(
                    any(
                        itertools.chain.from_iterable(
                            map(
                                lambda severity: severity.values(),
                                results.values(),
                            )
                        )
                    )
                )
