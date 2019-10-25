import venv
import tempfile
import contextlib

from dffml.util.asynctestcase import AsyncTestCase

class TestModels(AsyncTestCase):

    @classmethod
    def setUpClass(cls):
        print(super(AsyncTestCase, cls).setUpClass())
        print('done')
        super(AsyncTestCase, cls).setUpClass()
        builder = venv.EnvBuilder(system_site_packages=False, clear=True,
                symlinks=False, upgrade=True, with_pip=True, prompt=None)
        cls.venv_dir = cls.cls_exit_stack.enter_context(tempfile.TemporaryDirectory(prefix="dffml-test-"))
        builder.create(cls.venv_dir)

    def test_something(self):
        pass
