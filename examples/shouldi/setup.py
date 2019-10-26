from setuptools import setup

from dffml_setup_common import SETUP_KWARGS

SETUP_KWARGS["install_requires"] += [
    "aiohttp>=3.5.4",
    "bandit>=1.6.2",
    "safety>=1.8.5",
]
SETUP_KWARGS["entry_points"] = {
    "console_scripts": ["shouldi = shouldi.cli:ShouldI.main"],
    "dffml.operation": [
        "run_bandit = shouldi.bandit:run_bandit",
        "safety_check = shouldi.safety:safety_check",
        "pypi_latest_package_version = shouldi.pypi:pypi_latest_package_version",
        "pypi_package_json = shouldi.pypi:pypi_package_json",
        "pypi_package_url = shouldi.pypi:pypi_package_url",
        "pypi_package_contents = shouldi.pypi:pypi_package_contents",
        "cleanup_pypi_package = shouldi.pypi:cleanup_pypi_package",
    ],
}

setup(**SETUP_KWARGS)
