import inspect
import pathlib
import unittest
import importlib
from typing import Optional, Callable


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
        spec = importlib.util.spec_from_file_location(import_name, str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield import_name, module


root = pathlib.Path(__file__).parent.parent / "dffml"
skel = root / "skel"
package_name = "dffml"
# Skip any files in skel and __main__.py and __init__.py
skip = lambda _import_name, path: skel in path.parents or path.name.startswith(
    "__"
)

# All classes to test
to_test = {}

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
    print(obj)
