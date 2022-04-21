"""
.. code-block:: console

    $ python -u -m unittest -v examples/testing/doctest_module.py
    my_function (doctest_module)
    Doctest: doctest_module.my_function ... ok

    ----------------------------------------------------------------------
    Ran 1 test in 0.001s

    OK

"""
import sys
import doctest
import unittest


def my_function(value):
    """
    Multiplies value given by 2 and returns result

    Examples
    --------

    >>> my_function(5)
    10
    """
    return value * 2


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(sys.modules[__name__]))
    return tests
