import json
import pathlib
import subprocess

from dffml import *


class TestOpSource(AsyncTestCase):
    async def test_docstring(self):
        with chdir(pathlib.Path(__file__).parent / "op"):
            # Load the records
            records = json.loads(subprocess.check_output(["list.sh"]))
            # Load what the output should be
            correct = json.loads(pathlib.Path("correct.json").read_text())
            # Make the output is what it should be
            self.assertDictEqual(records, correct)
