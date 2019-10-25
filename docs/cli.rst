Command Line
============

Almost anything you can get done with the Python API you can get done with the
command line interface too.

.. contents:: Command Line Interface

Config
------

.. _cli_config_convert:

Convert
~~~~~~~

Convert one config file format into another.

.. code-block:: console

    $ dffml config convert -config-out yaml config_in.json

Service
-------

Services are various for a complete list of services maintained within the core
codebase see the :doc:`/plugins/dffml_service_cli` plugin docs.

Dev
~~~

Development utilites for creating new packages or hacking on the core codebase.

Export
++++++

Given the
`entrypoint <https://packaging.python.org/specifications/entry-points/>`_
of an object, covert the object to it's ``dict`` representation, and export it
using the given config format.

.. code-block:: console

    $ dffml service dev export -config json shouldi.cli:DATAFLOW

Entrypoints
+++++++++++

We make heavy use of the Python
`entrypoint <https://packaging.python.org/specifications/entry-points/>`_
system.

List
____

Sometimes you'll find that you've installed a package in development
mode, but the code that's being run when your using the CLI or HTTP API isn't
the code you've made modifications to, but instead it seems to be the latest
released version. That's because if the latest released version is installed,
the development mode source will be ignored by Python.

If you face this problem the first thing you'll want to do is identify the
entrypoint your plugin is being loaded from. Then you'll want to run this
command giving it that entrypoint. It will list all the registered plugins for
that entrypoint, along with the location of the source code being used.

In the following example, we see that the ``is_binary_pie`` operation registered
under the ``dffml.operation`` entrypoint is using the source from the
``site-packages`` directory. When you see ``site-packages`` you'll know that the
development version is not the one being used! That's the location where release
packages get installed. You'll want to remove the directory (and ``.dist-info``
directory) of the package name you don't want to used the released version of
from the ``site-packages`` directory. Then Python will start using the
development version (provided you have installed that source with the ``-e``
flag to ``pip install``).

.. code-block:: console

    $ dffml service dev entrypoints list dffml.operation
    is_binary_pie = dffml_operations_binsec.operations:is_binary_pie.op -> dffml-operations-binsec 0.0.1 (/home/user/.pyenv/versions/3.7.2/lib/python3.7/site-packages)
    pypi_package_json = shouldi.pypi:pypi_package_json -> shouldi 0.0.1 (/home/user/Documents/python/dffml/examples/shouldi)
    clone_git_repo = dffml_feature_git.feature.operations:clone_git_repo -> dffml-feature-git 0.2.0 (/home/user/Documents/python/dffml/feature/git)
