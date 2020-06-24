import ast
from io import open

from setuptools import find_packages, setup

with open('cvemap/version.py', 'r') as f:
    for line in f:
        if line.startswith('VERSION'):
            version = ast.literal_eval(line.strip().split('=')[-1].strip())
            break

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    INSTALL_REQUIRES = [line for line in f]

setup(
    name='cvemap',
    version=version,
    description='',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='John Andersen',
    author_email='john.s.andersen@intel.com',
    url='https://github.intel.com/johnsa1/cvemap',
    license='MIT',

    keywords=[
        '',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=INSTALL_REQUIRES,
    tests_require=[],

    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cvemap = cvemap.cli:main',
            'cvedb-server = cvemap.cvedb:Server.start',
        ],
        # 'dffml.metric': [
        #     'cvemap = cvemap.metric.cvemap:CVEMap',
        # ],
    },
)
