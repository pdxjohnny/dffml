DataFlow Deployment
===================

In the :doc:`/tutorials/operations` tutorial we created a command line meta
static analysis tool, ``shouldi``.

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

HTTP Deployment
---------------

We can take the

.. code-block:: console

    $ dffml service http server -insecure -log debug -mc-config shouldi/deploy

.. warning::

    The ``-insecure`` flag is only being used here to speed up this already long
    tutorial. See documentation on HTTP API security for more information.

.. code-block:: console

    $ curl -s \
      --header "Content-Type: application/json" \
      --request POST \
      --data '[{"value":"insecure-package","definition":"package"}]' \
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

    $ dffml dataflow create -config json \
      dffml.mapping.create lines_of_code_by_language lines_of_code_to_comments \
      > shouldi/deploy/override/shouldi.json

**shouldi/deploy/override/shouldi.json**

.. literalinclude:: /../examples/shouldi/shouldi/deploy/override/shouldi.json
    :language: json

.. code-block:: console

    $ dffml dataflow merge \
        shouldi/deploy/df/shouldi.json \
        shouldi/deploy/override/shouldi.json | \
      dffml dataflow diagram \
        -stages processing -simple -config json /dev/stdin

Copy and pasting the graph into the
`mermaidjs live editor <https://mermaidjs.github.io/mermaid-live-editor>`_
results in the following graph.

.. image:: /images/shouldi-dataflow-extended.svg
    :alt: Diagram showing DataFlow with use of comment to code ratio

.. code-block:: console

    $ curl -s \
      --header "Content-Type: application/json" \
      --request POST \
      --data '[{"value":"insecure-package","definition":"package"}]' \
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
