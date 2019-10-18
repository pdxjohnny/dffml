from setuptools import setup

from dffml_setup_common import SETUP_KWARGS, IMPORT_NAME

SETUP_KWARGS["install_requires"] += ["PyYAML>=5.1.2"]
SETUP_KWARGS["entry_points"] = {
    "dffml.config": [f"yaml = {IMPORT_NAME}.config:YamlConfigLoader"]
}

setup(**SETUP_KWARGS)
