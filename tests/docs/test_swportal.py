import pathlib

from dffml import AsyncTestCase
from dffml.util.testing.consoletest.cli import main as consoletest


class TestSWPortal(AsyncTestCase):
    async def test_readme(self):
        await consoletest(
            [
                str(
                    pathlib.Path(__file__).parents[2]
                    / "examples"
                    / "swportal"
                    / "README.rst"
                ),
                "--setup",
                str(
                    pathlib.Path(__file__).parent
                    / "swportal_consoletest_test_setup.py"
                ),
            ]
        )
