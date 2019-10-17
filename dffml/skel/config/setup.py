from setuptools import setup

from dffml_setup_common import SETUP_KWARGS, IMPORT_NAME

SETUP_KWARGS["entry_points"] = {
    "dffml.config": [f"misc = {IMPORT_NAME}.config:MiscConfigLoader"]
}

setup(**SETUP_KWARGS)
