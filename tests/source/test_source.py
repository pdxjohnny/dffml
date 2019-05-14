from dffml.source.source import BaseSource
from dffml.util.asynctestcase import AsyncTestCase

class FakeSource(BaseSource):
    pass

class TestSource(AsyncTestCase):

    def test_arg_lower_name(self):
        self.assertEqual('fake', FakeSource._arg_lower_name())

    def test_arg_prop(self):
        self.assertEqual('arg_source_fake_test',
                         FakeSource._arg_prop('test'))

    def test_arg_name(self):
        self.assertEqual('-source-fake-test',
                         FakeSource._arg_name('test'))

    def test_arg_from(self):
        setattr(self, 'source_fake_test', 42)
        self.assertEqual(42,
                         FakeSource._arg_from(self, 'test'))
