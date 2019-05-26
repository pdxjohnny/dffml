from setuptools import find_packages, setup

setup(
    name='dffml-operation-examples',
    version='0.0.0',
    description='DFFML Operation Examples',
    long_description='No Readme...',
    long_description_content_type='text/markdown',
    author='John Andersen',
    author_email='john.s.andersen@intel.com',
    maintainer='John Andersen',
    maintainer_email='john.s.andersen@intel.com',
    url='https://github.com/intel/dffml',
    license='MIT',
    keywords=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    packages=find_packages(),
    install_requires=[
        # 'dffml>=0.2.0',
    ],
    entry_points={
        'dffml.operation': [
            'insecure_smtp = dffml_operation_examples.smtp:InsecureSMTP.op',
        ],
        'dffml.operation.implementation': [
            'insecure_smtp = dffml_operation_examples.smtp:InsecureSMTP',
        ],
    },
)
