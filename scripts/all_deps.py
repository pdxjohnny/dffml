#!/usr/bin/env python3
"""
Script to get all dependencies
"""
import os
import pathlib
import argparse
import importlib
import contextlib
import unittest.mock


@contextlib.contextmanager
def chdir(new_path):
    """
    Context manager to change directroy
    """
    old_path = os.getcwd()
    os.chdir(new_path)
    try:
        yield
    finally:
        os.chdir(old_path)


def remove_package_versions(package):
    for char in [">", "<", "="]:
        if char in package:
            return package.split(char)[0].strip()
    return package.strip()


def get_kwargs(setup_filepath: pathlib.Path):
    setup_kwargs = {}

    def grab_setup_kwargs(**kwargs):
        setup_kwargs.update(kwargs)

    with chdir(str(setup_filepath.parent.resolve())):
        spec = importlib.util.spec_from_file_location(
            "setup", setup_filepath.name
        )
        with unittest.mock.patch("setuptools.setup", new=grab_setup_kwargs):
            setup = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(setup)

    return setup_kwargs


def main():
    root = pathlib.Path(__file__).parent.parent
    skel = root / "dffml" / "skel"
    shouldi_downloads = root / "examples" / "shouldi" / "tests" / "downloads"

    internal = ["dffml", "shouldi"]
    with chdir(str(root / "dffml")):
        spec = importlib.util.spec_from_file_location("plugins", "plugins.py")
        plugins = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugins)
        internal += [
            "-".join(["dffml"] + list(plugin_path))
            for plugin_path in plugins.CORE_PLUGINS
        ]

    deps = []
    for path in root.rglob("**/setup.py"):
        skip = False
        for i in [skel, shouldi_downloads]:
            if i in path.parents:
                skip = True
        if skip:
            continue
        for add in ["tests_require", "install_requires"]:
            deps.extend(get_kwargs(path).get(add, []))

    dedup = {remove_package_versions(package): package for package in deps}

    for package in internal:
        if package in dedup:
            del dedup[package]

    print("\n".join(sorted(dedup.values())))


if __name__ == "__main__":
    main()
