import os
import io
import sys
import shutil
import doctest
import inspect
import pathlib
import unittest
import tempfile
import importlib
import contextlib
from typing import Optional, Callable

from dffml.util.asynctestcase import AsyncTestCase


def import_file(import_name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(import_name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def modules(
    root: pathlib.Path,
    package_name: str,
    *,
    skip: Optional[Callable[[str, pathlib.Path], bool]] = None,
):
    for path in root.rglob("*.py"):
        # Figure out name
        import_name = pathlib.Path(str(path)[len(str(root)) :]).parts[1:]
        import_name = (
            package_name
            + "."
            + ".".join(
                list(import_name[:-1]) + [import_name[-1].replace(".py", "")]
            )
        )
        # Check if we should skip importing this file
        if skip and skip(import_name, path):
            continue
        # Import module
        yield import_name, import_file(import_name, path)


class DefaultTestCase:
    def setUp(self):
        self.orig_cwd = os.getcwd()
        self.tempdir = tempfile.mkdtemp()
        os.chdir(self.tempdir)

    def tearDown(self):
        os.chdir(self.orig_cwd)
        shutil.rmtree(self.tempdir)


root = pathlib.Path(__file__).parent.parent / "dffml"
skel = root / "skel"
package_name = "dffml"
# Skip any files in skel and __main__.py and __init__.py
skip = lambda _import_name, path: skel in path.parents or path.name.startswith(
    "__"
)

# All classes to test
to_test = {}


doctest_header = import_file(
    "doctest_header",
    pathlib.Path(__file__).parent.parent / "docs" / "doctest_header.py",
)

@contextlib.contextmanager
def tempdir(state):
    with tempfile.TemporaryDirectory() as new_cwd:
        try:
            orig_cwd = os.getcwd()
            os.chdir(new_cwd)
            yield
        finally:
            os.chdir(orig_cwd)

@contextlib.contextmanager
def operation_io_AcceptUserInput(state):
    with unittest.mock.patch("builtins.input", return_value="Data flow is awesome"):
        yield


def mktestcase(obj):
    state = {}
    extra_context = sys.modules[__name__].__dict__.get(
        (obj.__module__[len(package_name) + 1:] + "." + obj.__qualname__).replace(".", "_"),
        None
    )
    def testcase(self):
        with contextlib.ExitStack() as stack:
            stack.enter_context(tempdir(state))
            if extra_context is not None:
                stack.enter_context(extra_context(state))

            output = io.StringIO()

            verbose=(os.environ.get("LOGGING", "").lower() == "debug")

            finder = doctest.DocTestFinder(verbose=verbose, recurse=False)
            runner = doctest.DocTestRunner(verbose=verbose)



            for test in finder.find(obj, obj.__qualname__, globs=doctest_header.__dict__):
                results = runner.run(test, out=output.write)

                """
                doctest.run_docstring_examples(
                    obj,
                    doctest_header.__dict__,
                    verbose=(os.environ.get("LOGGING", "").lower() == "debug"),
                    name=obj.__qualname__,
                )
                """

                if results.failed:
                    raise Exception(output.getvalue())

    return testcase



for import_name, module in modules(root, package_name, skip=skip):
    for name, obj in inspect.getmembers(module):
        if (
            not hasattr(obj, "__module__")
            or not obj.__module__.startswith(import_name)
            or (not inspect.isclass(obj) and not inspect.isfunction(obj))
        ):
            continue
        to_test[obj.__module__ + "." + obj.__qualname__] = obj

for obj in to_test.values():
    docstring = inspect.getdoc(obj)
    if docstring is None or not "\n>>>" in docstring:
        continue
    """
    if not "parser_helper" in docstring:
        continue
    """

    base_name = (
        obj.__module__.replace(package_name, "base")
        .replace(".", " ")
        .title()
        .replace(" ", "")
    )
    test_name = (
        obj.__module__.replace(package_name, "test")
        .replace(".", " ")
        .title()
        .replace(" ", "")
    )

    """
    test_class = type(
        test_name,
        (
            sys.modules[__name__].__dict__.get(base_name, DefaultTestCase),
            AsyncTestCase,
        ),
        {},
    )

    setattr(test_class, "test_" + obj.__qualname__, mktestcase(obj))

    print("Made testcase", obj, test_class)

    tests.addTest(test_class('run'))
    """
    description = (obj.__module__[len(package_name) + 1:] + "." + obj.__qualname__).replace(".", "_")
    testcase = unittest.FunctionTestCase(mktestcase(obj),
            description=description)

    testcase = type(description, (unittest.TestCase, ), {"test_docstring": mktestcase(obj)})

    setattr(sys.modules[__name__], description, testcase)

"""
def load_tests(loader, tests, ignore):
    for obj in to_test.values():
        docstring = inspect.getdoc(obj)
        if docstring is None or not "\n>>>" in docstring:
            continue

        base_name = (
            obj.__module__.replace(package_name, "base")
            .replace(".", " ")
            .title()
            .replace(" ", "")
        )
        test_name = (
            obj.__module__.replace(package_name, "test")
            .replace(".", " ")
            .title()
            .replace(" ", "")
        )

        description = (obj.__module__[len(package_name) + 1:] + "." + obj.__qualname__).replace(".", "_")
        testcase = unittest.FunctionTestCase(mktestcase(obj),
                description=description)

        print(sys.modules[__name__], description, testcase)

        # tests.addTest(unittest.FunctionTestCase(mktestcase(obj),
        #         description=(obj.__module__[len(package_name) + 1:] + "." + obj.__qualname__).replace(".", "_")))
    return tests
"""
