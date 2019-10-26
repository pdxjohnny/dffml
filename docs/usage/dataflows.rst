DataFlow Deployment
===================

In the :doc:`/tutorials/operations` we created a command line meta static
analysis tool, ``shouldi``.

.. code-block:: console

    $ shouldi install dffml insecure-package
    dffml is okay to install
    Do not install insecure-package!
        safety_check_number_of_issues: 1
        bandit_output: {'CONFIDENCE.HIGH': 0.0, 'CONFIDENCE.LOW': 0.0, 'CONFIDENCE.MEDIUM': 0.0, 'CONFIDENCE.UNDEFINED': 0.0, 'SEVERITY.HIGH': 0.0, 'SEVERITY.LOW': 0.0, 'SEVERITY.MEDIUM': 0.0, 'SEVERITY.UNDEFINED': 0.0, 'loc': 100, 'nosec': 0, 'CONFIDENCE.HIGH_AND_SEVERITY.HIGH': 0}

In the :ref:`tutorials_operations_registering_opreations` section of the
operations tutorial, we registered our operations with Python's ``entry_point``
system. This allows other Python packages and DFFML plugins to access them
without the need to hardcode in ``import`` statements.

.. code-block:: console

    $ curl -s \
      --header "Content-Type: application/json" \
      --request POST \
      --data '{"insecure-package": [{"value":"insecure-package","definition":"package"}]}' \
      http://localhost:8080/shouldi | python -m json.tool
    {
        "insecure-package": {
            "safety_check_number_of_issues": 1,
            "bandit_output": {
                "CONFIDENCE.HIGH": 0,
                "CONFIDENCE.LOW": 0,
                "CONFIDENCE.MEDIUM": 0,
                "CONFIDENCE.UNDEFINED": 0,
                "SEVERITY.HIGH": 0,
                "SEVERITY.LOW": 0,
                "SEVERITY.MEDIUM": 0,
                "SEVERITY.UNDEFINED": 0,
                "loc": 100,
                "nosec": 0,
                "CONFIDENCE.HIGH_AND_SEVERITY.HIGH": 0
            }
        }
    }

.. note::

    Please install the ``dffml-config-yaml`` package to enable the
    ``-config yaml`` option. Allowing you to export to YAML instead of JSON.
    You can also convert between config file formats with the
    :ref:`cli_config_convert` command.

    JSON files work fine, but they'll take up too much page space in this
    tutorial.

MultiComms
----------

Another concept in DFFML is the ``MultiComm``, they are contain multiple
channels of communications. ``MultiComm``'s will typically be protocol based.
An IRC or Slack ``MultiComm`` channel of communication might be a chat room, or
when a particular word immediately follows the bots name.

Example:

::

    myuser    | mybot: shouldi install ...

The HTTP server was the first ``MultiComm`` written for DFFML. It's channels of
communication are URL paths (Example: ``/some/url/path``).

HTTP Deployment
---------------

We'll be working from the top level directory of the ``shouldi`` package we
created in the :doc:`/tutorials/operations`.

The source for that package is also available under the ``examples/shouldi``
directory of the DFFML source code.

.. code-block:: console

    $ cd examples/shouldi

The first step is to create a config file for the ``MultiComm`` we'll be using.
Config files for 

.. code-block:: console

    $ mkdir -p shouldi/deploy/mc/http

**shouldi/deploy/mc/http/shouldi.yaml**

.. literalinclude:: /../examples/shouldi/shouldi/deploy/mc/http/shouldi.yaml
    :language: yaml

.. code-block:: console

    $ dffml service http server -insecure -log debug -mc-config shouldi/deploy

.. warning::

    The ``-insecure`` flag is only being used here to speed up this
    tutorial. See documentation on HTTP API
    :doc:`/plugins/service/http/security` for more information.

.. code-block:: console

    $ curl -s \
      --header "Content-Type: application/json" \
      --request POST \
      --data '{"insecure-package": [{"value":"insecure-package","definition":"package"}]}' \
      http://localhost:8080/shouldi | python -m json.tool
    {
        "bandit_output": {
            "CONFIDENCE.HIGH": 0,
            "CONFIDENCE.LOW": 0,
            "CONFIDENCE.MEDIUM": 0,
            "CONFIDENCE.UNDEFINED": 0,
            "SEVERITY.HIGH": 0,
            "SEVERITY.LOW": 0,
            "SEVERITY.MEDIUM": 0,
            "SEVERITY.UNDEFINED": 0,
            "loc": 100,
            "nosec": 0,
            "CONFIDENCE.HIGH_AND_SEVERITY.HIGH": 0
        },
        "safety_check_number_of_issues": 1
    }

Extending
---------

.. code-block:: console

    $ mkdir -p shouldi/deploy/override
    $ dffml dataflow create -config yaml \
      dffml.mapping.create lines_of_code_by_language lines_of_code_to_comments \
      > shouldi/deploy/override/shouldi.yaml

The final directory structure should look like this

.. code-block:: console

    $ tree shouldi
    shouldi
    ├── bandit.py
    ├── cli.py
    ├── deploy
    │   ├── df
    │   │   └── shouldi.json
    │   ├── mc
    │   │   └── http
    │   │       └── shouldi.yaml
    │   └── override
    │       └── shouldi.yaml
    ├── __init__.py
    ├── pypi.py
    ├── safety.py
    └── version.py

    5 directories, 9 files

We now have

- The ``shouldi`` dataflow

- A config file for the ``http`` multicomm, using the dataflow named ``shouldi``

- A dataflow containing modififactions to the ``shouldi`` dataflow


**shouldi/deploy/override/shouldi.yaml**

.. literalinclude:: /../examples/shouldi/shouldi/deploy/override/shouldi.yaml
    :language: yaml

.. code-block:: console

    $ dffml dataflow merge \
        shouldi/deploy/df/shouldi.yaml \
        shouldi/deploy/override/shouldi.yaml | \
      dffml dataflow diagram \
        -stages processing -simple -config yaml /dev/stdin

Copy and pasting the graph into the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`_
results in the following graph.

.. image:: /images/shouldi-dataflow-extended.svg
    :alt: Diagram showing DataFlow with use of comment to code ratio

.. code-block:: console

    $ curl -s \
      --header "Content-Type: application/json" \
      --request POST \
      --data '{"insecure-package": [{"value":"insecure-package","definition":"package"}]}' \
      http://localhost:8080/shouldi | python -m json.tool
    {
        "bandit_output": {
            "CONFIDENCE.HIGH": 0,
            "CONFIDENCE.LOW": 0,
            "CONFIDENCE.MEDIUM": 0,
            "CONFIDENCE.UNDEFINED": 0,
            "SEVERITY.HIGH": 0,
            "SEVERITY.LOW": 0,
            "SEVERITY.MEDIUM": 0,
            "SEVERITY.UNDEFINED": 0,
            "loc": 100,
            "nosec": 0,
            "CONFIDENCE.HIGH_AND_SEVERITY.HIGH": 0
        },
        "language_to_comment_ratio": 19,
        "safety_check_number_of_issues": 1
    }
