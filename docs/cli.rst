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
